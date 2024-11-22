#!/bin/bash

sudo docker compose -f ~/docker/docker-compose-udms.yml pull
sudo docker compose -f ~/docker/docker-compose-udms.yml up --force-recreate --build -d 

