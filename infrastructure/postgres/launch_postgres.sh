#!/bin/bash

if [ $# -ne 1 ]
    then
        echo "Script requires a single arg: superuser password"
    else
        docker run --name bm-postgres -d -p 5432:5432 --restart always \
            -e POSTGRES_PASSWORD=$1 \
            -e POSTGRES_USER=postgres \
            -e DB_HOST=0.0.0.0 \
            -v /var/lib/postgresql/data:/var/lib/postgresql/data \
            -v "$PWD/pg.conf":/etc/postgresql/postgresql.conf \
            postgres:13.2  -c 'config_file=/etc/postgresql/postgresql.conf'
fi