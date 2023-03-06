#!/bin/bash

f=${1:-*} # default to all files
scp -r "./search/$f" farnam:~/project/search
