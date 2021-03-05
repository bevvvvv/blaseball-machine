#!/bin/bash

if [ $# -ne 1 ]
    then
        echo "Script requires a single arg: default password"
    else
        docker run --name pgadmin --restart always -p 80:80 \
            -e PGADMIN_DEFAULT_EMAIL=computerwhiz1337@gmail.com \
            -e PGADMIN_DEFAULT_PASSWORD=$1 \
            -d dpage/pgadmin4
fi