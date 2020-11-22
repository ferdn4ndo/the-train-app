#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

rm -rf "$DIR/data/cache/*"
rm -rf "$DIR/data/results/comparisons/*"

rm -rf "$DIR/logs/comparisons/*"
rm -rf "$DIR/logs/controllers/*"
rm -rf "$DIR/logs/simulations/*"

rm -rf "$DIR/temp/synoptic_panel_frames/*"
