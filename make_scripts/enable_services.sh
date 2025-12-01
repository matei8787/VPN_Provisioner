#!/bin/bash

files=$(ls ./systemd_templates)

for file in $files; do
    systemctl enable $file 
done
