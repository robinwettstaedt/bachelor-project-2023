#!/bin/bash

# Run the other 3 bash scripts in order
. ./docker-stop.sh
. ./docker-build.sh
. ./docker-run.sh

