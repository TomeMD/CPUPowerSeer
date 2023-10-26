#!/usr/bin/env bash

CPU_POWER_MODEL=$(dirname -- "$(readlink -f -- "$0")")

export PYTHONPATH=${PYTHONPATH}:${CPU_POWER_MODEL}

