#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from pathlib import Path
import random
import time
import os

import yaml
import twitter
import dropbox


PWD = Path(__file__).parents[0].resolve()

with open(PWD / 'settings.yml') as fp:
    SETTING = yaml.load(fp.read())

ROOT_DIR = SETTING['root_folder']
LOG_FILE = PWD / SETTING['log_file']
DROPBOX_TOKEN = SETTING['dropbox_token']

DIR_TO_TXT = dict()
for folder_to_caption in SETTING['folder_captions']:
    DIR_TO_TXT.update(**folder_to_caption)


def write_log(msg):
    with open(LOG_FILE, 'a') as fp:
        ts = time.time()
        fp.write(f'{ts}\t{msg}\n')


def list_dropbox_files(dirname):
    files = [x.path_display for x in dbx.files_list_folder(dirname).entries
             if type(x) != dropbox.files.FolderMetadata]
    return files


if __name__ == '__main__':
    with open(PWD / 'twitter-api-key.json') as fp:
        twitter_key = json.loads(fp.read())

    twitter_api = twitter.Api(**twitter_key)
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)

    with open(PWD / 'used_files.txt', 'r') as fp:
        used_files = fp.read().split('\n')

    candidates = []
    for d in DIR_TO_TXT:
        for f in list_dropbox_files(ROOT_DIR + d):
            candidates += [(f, DIR_TO_TXT[d])]

    filename = None
    while str(filename) in used_files or filename is None:
        filename, caption = random.choice(candidates)
        filename = str(filename)

    try:
        md, res = dbx.files_download(filename)
    except dropbox.exceptions.HttpError:
        write_log(f'Failed to download {filename} from dropbox')
        exit(1)

    tmp_filename = PWD.joinpath(filename.split('/')[-1])
    with open(tmp_filename, 'wb') as fp:
        fp.write(res.content)

    with open(tmp_filename, 'rb') as fp:
        write_log(f'Posting {filename} with caption {caption}')
        twitter_api.PostUpdate(caption, media=fp)
        write_log('Posting complete')

    with open(PWD.joinpath('used_files.txt'), 'a') as fp:
        fp.write(filename + '\n')
        write_log('Used image list update complete')

    os.remove(tmp_filename)
