#!/bin/bash
docker run -p 8090:80 --rm --name=tools-barebone-instance tools-barebone && echo "You can connect to http://localhost:8090"