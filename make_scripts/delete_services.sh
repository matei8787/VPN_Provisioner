#!/bin/bash

files=$(ls ./systemd_templates)

for file in $files; do
    rm /etc/systemd/system/$file 
done
