#!/usr/bin/env bash

cd app/tests || exit
python -m unittest discover
