#!/bin/bash

#virtualenv venv
#. ./venv/bin/activate
#pip install --upgrade pip
#pip install --upgrade setuptools
#pip install panda3d -i https://archive.panda3d.org/branches/deploy-ng --upgrade
scons "$@"
