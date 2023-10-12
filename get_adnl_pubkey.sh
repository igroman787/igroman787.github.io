#!/bin/bash
set -e

# check sudo permissions
if [ "$(id -u)" != "0" ]; then
    echo "Please run script as root"
    exit 1
fi

# create work dir
work_dir=/tmp/get_adnl_pubkey
mkdir $work_dir && cd $work_dir

# create virtual environment
virtualenv venv
. venv/bin/activate

# install package
pip3 install PyNaCl==1.5.0

wget https://raw.githubusercontent.com/igroman787/igroman787.github.io/master/get_adnl_pubkey.py
python3 get_adnl_pubkey.py

deactivate
