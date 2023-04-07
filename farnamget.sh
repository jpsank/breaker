#!/bin/bash

dirname=$( dirname -- "$0"; )

f=$1
scp -r farnam:"~/project/breaker/$f" "$dirname/$f"
