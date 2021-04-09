#!/bin/sh

cd lkft/kselftest
sudo ./kselftest.sh -p ~/kselftests -g 5.4 -S skipfile-lkft.yaml -s true
