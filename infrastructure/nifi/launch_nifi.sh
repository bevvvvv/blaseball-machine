#!/bin/bash

docker run --name nifi \
  -p 8080:8080 -d --restart always \
  apache/nifi:latest

docker run --name nifi-registry \
  -p 18080:18080 -d --restart always \
  apache/nifi-registry:latest