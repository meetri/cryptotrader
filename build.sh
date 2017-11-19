#!/bin/bash

docker build -t meetri/cryptocoin:latest . && \
    docker push meetri/cryptocoin:latest
