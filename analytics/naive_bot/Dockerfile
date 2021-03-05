FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y wget unzip

# miniconda install
ENV PATH="/root/miniconda3/bin:${PATH}"
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh \
    && echo PATH="/root/miniconda3/bin":$PATH >> .bashrc \
    && exec bash \
    && conda --version
    
# chromedriver
RUN wget -N http://chromedriver.storage.googleapis.com/2.29/chromedriver_linux64.zip -P ~/Downloads && \
    unzip ~/Downloads/chromedriver_linux64.zip -d ~/Downloads
RUN mv -f ~/Downloads/chromedriver /usr/local/share/ && \
    chmod +x /usr/local/share/chromedriver
RUN ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver && \
    ln -s /usr/local/share/chromedriver /usr/bin/chromedriver

# copy code


# install dependencies


# entrypoint