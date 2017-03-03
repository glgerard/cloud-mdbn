#!/usr/bin/env bash

MDBN_ROOT=$( pwd )
export MDBN_ROOT

PYTHONPATH=${PYTHONPATH}:${MDBN_ROOT}/src
export PYTHONPATH

PATH=${MDBN_ROOT}/tools:$PATH
export PATH
