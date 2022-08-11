#!/bin/sh
set -e

faust -A src.consumers --datadir=${dataDir} worker -l info