#!/bin/bash

set -x
set -e

cat hs_service.template | sed -e "s|USER|$(whoami)|g; s|COMMAND|$(pwd)/hs_serial.py|g" > hs_serial.service
cat hs_service.template | sed -e "s|USER|$(whoami)|g; s|COMMAND|$(pwd)/hs_web.py|g" > hs_web.service

sudo mv hs_*.service /etc/systemd/system/
sudo systemctl enable hs_serial.service
sudo systemctl enable hs_web.service