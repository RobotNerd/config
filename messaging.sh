#!/usr/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

function info {
  echo -e "${GREEN}$1${NC}"
}

function error {
  echo -e "${RED}$1${NC}"
}
