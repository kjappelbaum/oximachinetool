#!/bin/bash
docker run -d -p 8090:80 --rm --name=tools-barebone-shiftml-instance tools-barebone-shiftml && echo "You can connect to http://localhost:8090"