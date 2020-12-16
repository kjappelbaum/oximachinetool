#!/bin/bash
echo "Connect to http://localhost:8091"
docker run -d -p 8091:80 --rm --security-opt seccomp:unconfined --name=custom-tools-instance oximachine_new
