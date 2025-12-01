#!/bin/bash

for dir in */; do
    mkdir -p /opt/services
    cp -r ./$dir /opt/services
done
