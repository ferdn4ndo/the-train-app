#!/usr/bin/env sh

echo "Removing logs..."
rm logs/* -r -v -f

echo "Removing results..."
rm data/results/* -r -v -f

echo "Removing profiler data..."
rm data/profiler/* -r -v -f

echo "Removing temp..."
rm temp/* -r -v -f

echo "Clearing cache..."
rm data/cache/* -r -v -f
