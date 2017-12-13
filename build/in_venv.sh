#!/bin/bash

virtualenv venv
. ./venv/bin/activate
pip install panda3d -i https://archive.panda3d.org/branches/deploy-ng --upgrade
scons "$@"
