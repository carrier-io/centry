#!/usr/bin/env bash

#TODO: Interactive pylon default configuration...
echo 'Please copy config/pylon-example.yml to config/pylon.yml and edit it according to your needs.'
echo 'More info in README.md'
echo 'Press `Esc` to exit or any other key when ready...'

read -s -n1 key
case $key in
    $'\e') exit 1;;
esac
