#!/bin/bash

set -o errexit
set -o nounset

. ./scripts/utils/start_gunicorn.sh

start_gunicorn
