import sys
import logging
import datetime as dt
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()
logger = logging.getLogger('uvicorn.error')

@app.post('/bet')
async def bet_listener(username: str, password:str, tasks: BackgroundTasks):
    logger.info('Dispatching betting bot...')
    tasks.add_task(bet, username, password)
    return {'message': 'Succesfully dispatched bot.'}

def bet(username: str, password: str):
    # driver needs to be in path
    driver = webdriver.Chrome()
    driver.get("https://www.blaseball.com/league")

    # login with supplied credentials
    LOGIN_PATH = '/html/body/div[1]/div/div/nav/div/a[2]'
    get_elem_xpath(LOGIN_PATH, driver).click()
    USER_PATH = '//*[@id="root"]/div/div/div/div[2]/div/div/form/div[1]/input'
    get_elem_xpath(USER_PATH, driver).send_keys(username)
    PASSWD_PATH = '//*[@id="root"]/div/div/div/div[2]/div/div/form/div[2]/input'
    get_elem_xpath(PASSWD_PATH, driver).send_keys(password)
    SUBMIT_PATH = '//*[@id="root"]/div/div/div/div[2]/div/div/form/div[3]/input'
    get_elem_xpath(SUBMIT_PATH, driver).click()
    LEAGUE_BUTTON = '//*[@id="root"]/div/nav/div[2]/a[2]'
    get_elem_xpath(LEAGUE_BUTTON, driver).click()

    # grab previous data
    team_names = driver.find_elements_by_class_name("GameWidget-ScoreName")
    team_scores = driver.find_elements_by_class_name("GameWidget-ScoreNumber")
    team_record = driver.find_elements_by_class_name("GameWidget-ScoreRecord")
    team_prob = driver.find_elements_by_class_name("GameWidget-WinChance")
    leage_info = driver.find_elements_by_class_name("League-Number")

    # create df to populate
    column_names = ['home_team', 'away_team', 'home_score', 'away_score', 'winner',
                    'home_record', 'away_record', 'home_win_prob', 'away_win_prob',
                    'timestamp', 'season', 'season_day']
    df = pd.DataFrame(columns=column_names)

    for team_one in range(0, len(team_names), 2):
        entry = {}
        team_two = team_one + 1
        entry['home_team'] = team_names[team_one].text
        entry['away_team'] = team_names[team_two].text
        entry['home_score'] = int(team_scores[team_one].text)
        entry['away_score'] = int(team_scores[team_two].text)
        entry['home_record'] = team_record[team_one].text
        entry['away_record'] = team_record[team_two].text
        entry['home_win_prob'] = team_prob[team_one].text
        entry['away_win_prob'] = team_prob[team_two].text
        entry['timestamp'] = dt.datetime.now()
        entry['season'] = int(leage_info[0].text)
        entry['season_day'] = int(leage_info[1].text)
        
        # determine winner
        if entry['home_score'] < entry['away_score']:
            entry['winner'] = entry['away_team']
        elif entry['away_score'] < entry['home_score']:
            entry['winner'] = entry['home_team']
        else:
            entry['winner'] = 'Tie'

        # populate df
        df = df.append(entry, ignore_index=True)

    logger.info(df)

    # bet on new games
    BET_PATH = '//*[@id="root"]/div/div/div[2]/a[2]'
    get_elem_xpath(BET_PATH, driver).click()

    team_names = driver.find_elements_by_class_name("GameWidget-ScoreName")
    team_scores = driver.find_elements_by_class_name("GameWidget-ScoreNumber")
    team_record = driver.find_elements_by_class_name("GameWidget-ScoreRecord")
    team_prob = driver.find_elements_by_class_name("GameWidget-WinChance")
    leage_info = driver.find_elements_by_class_name("League-Number")

    bet_buttons = driver.find_elements_by_css_selector("button.Widget-Button.btn.btn-success")
    bet_buttons.pop(0)

    # create df to populate
    column_names = ['home_team', 'away_team', 'decision'
                    'home_record', 'away_record', 'home_win_prob', 'away_win_prob',
                    'timestamp', 'season', 'season_day']
    df = pd.DataFrame(columns=column_names)

    for team_one in range(0, len(team_names), 2):
        logger.info(team_one)
        entry = {}
        team_two = team_one + 1
        entry['home_team'] = team_names[team_one].text
        entry['away_team'] = team_names[team_two].text
        entry['home_score'] = int(team_scores[team_one].text)
        entry['away_score'] = int(team_scores[team_two].text)
        entry['home_record'] = team_record[team_one].text
        entry['away_record'] = team_record[team_two].text
        entry['home_win_prob'] = team_prob[team_one].text
        entry['away_win_prob'] = team_prob[team_two].text
        entry['timestamp'] = dt.datetime.now()
        entry['season'] = int(leage_info[0].text)
        entry['season_day'] = int(leage_info[1].text)

        # bet
        button = bet_buttons[team_one//2]
        def click_button(button):
            driver.execute_script('arguments[0].scrollIntoView();', button)
            time.sleep(2)
            logger.info(len(bet_buttons))
            button.click()
        try:
            click_button(button)
        except:
            try:
                bet_buttons.pop(team_one//2)
                click_button(bet_buttons[team_one//2])
            except:
                logger.error('Could not click bet button.')
                driver.quit()
                return

        
        names = driver.find_elements_by_class_name('ModalForm-Form-Team-Name')
        win_pct = driver.find_elements_by_class_name('ModalForm-Form-Team-Percentage')
        win_pct = [int(elem.text.replace('%','')) for elem in win_pct]
        if win_pct[0] > win_pct[1]:
            entry['decision'] = names[0]
            driver.find_element_by_css_selector('div.ModalForm-Form-Team.Home').click()
        else:
            entry['decision'] = names[1]
            driver.find_element_by_css_selector('div.ModalForm-Form-Team.Away').click()
        try:
            amount_path = '//*[@id="amount"]'
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, amount_path)))
            amount_input = driver.find_element_by_xpath(amount_path)
            amount_input.click()
            amount_input.send_keys(Keys.BACKSPACE)
            amount_input.send_keys('1')
            logger.info('bet!')
        except:
            logger.error('Error loading page!')
            driver.quit()
            return
        # submit bet
        #get_elem_xpath('//*[@id="root"]/div/div/div[4]/div/form/div[4]/button', driver).click()
        # close window
        get_elem_xpath('//*[@id="root"]/div/div/div[4]/div/button', driver).click()

        df = df.append(entry, ignore_index=True)

    driver.close()
    driver.quit()

    logger.info(df)
    logger.info('Process complete')

def get_elem_xpath(path, driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, path)))
    except:
        logger.error('Error loading page!')
        driver.quit()
    return driver.find_element_by_xpath(path)
