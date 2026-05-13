#!/bin/bash
sudo systemctl stop postgresql
sudo mv /var/lib/postgresql/16/main/standby.signal /var/lib/postgresql/16/main/standby.signal.bck
sudo systemctl start postgresql