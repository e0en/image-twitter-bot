#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from pathlib import Path
import random
import time
import os

import yaml
import twitter


PWD = Path(__file__).parents[0].resolve()

with open('settings.yml') as fp:
    SETTING = yaml.load(fp.read())

ROOT_DIR = Path.home() / SETTING['root_folder']
LOG_FILE = PWD / SETTING['log_file']


DIR_TO_TXT = dict()
for (folder, caption) in SETTING['folder_captions']:
    DIR_TO_TXT[folder] = caption


def write_log(msg):
    with open(LOG_FILE, 'a') as fp:
        ts = time.time()
        fp.write(f'{ts}\t{msg}\n')


if __name__ == '__main__':
    with open(PWD.joinpath('twitter-api-key.json')) as fp:
        twitter_key = json.loads(fp.read())
    api = twitter.Api(**twitter_key)

    with open(PWD.joinpath('used_files.txt'), 'r') as fp:
        used_files = fp.read().split('\n')

    candidates = []
    for d in DIR_TO_TXT:
        for f in os.listdir(d):
            candidates += [(d / f, DIR_TO_TXT[d])]

    filename = None
    while str(filename) in used_files or filename is None:
        filename, caption = random.choice(candidates)
        filename = str(filename)

    with open(filename, 'rb') as fp:
        write_log(f'Posting {filename} with caption {caption}')
        api.PostUpdate(caption, media=fp)
        write_log('Posting complete')

    with open(PWD.joinpath('used_files.txt'), 'a') as fp:
        fp.write(filename + '\n')
        write_log('Used image list update complete')
