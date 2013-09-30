#!/bin/bash

HOST=$(curl -s http://169.254.169.254/latest/meta-data/public-hostname)
~/google_appengine/dev_appserver.py . --host $HOST --admin_host $HOST 

