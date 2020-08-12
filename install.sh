#!/bin/bash

set -x
set -e

cat service.template | sed -e "s|USER|$(whoami)|g; s|COMMAND|$(pwd)/homestats.py|g" > homestats.service

sudo mv homestats.service /etc/systemd/system/
sudo systemctl enable homestats.service