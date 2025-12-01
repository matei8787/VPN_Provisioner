#!/bin/bash

files=$(ls ./systemd_templates)

for file in $files; do
    cp ./systemd_templates/$file /etc/systemd/system/
done
