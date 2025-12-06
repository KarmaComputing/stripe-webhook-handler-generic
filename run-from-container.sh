#!/bin/bash

# Did you forget to run ./build.sh first?
docker run -e "PYTHON_LOG_LEVEL=DEBUG" --publish 5001:80 test

