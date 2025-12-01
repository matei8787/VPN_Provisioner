#!/bin/bash

files=$(ls ./systemd_templates)

for file in $files; do
    systemctl disable $file 
done
