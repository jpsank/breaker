#!/bin/bash

f=${1:-search/*} # default to all files
scp -r $f farnam:~/project/breaker/$f
