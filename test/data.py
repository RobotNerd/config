#!/usr/bin/python3
import os
import shutil

BASE_PATH='./unittest_data'


def reset():
    if os.path.isdir(BASE_PATH):
        shutil.rmtree(BASE_PATH)
    os.mkdir(BASE_PATH)
