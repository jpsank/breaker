#!/bin/bash

f=${1:-*} # default to all files
scp -r "$f" farnam:"~/project/breaker/$f"
