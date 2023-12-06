import requests

from google_api_client import SpreadSheetsClient

# The ID of the spreadsheet.
SAMPLE_SPREADSHEET_ID = "1nOtYmv_d6Qt1tCX_63uE2yWVFs6-G5x_XJ778lD9qyU"

def ini_spreadsheets() -> SpreadSheetsClient:
    return SpreadSheetsClient(
        'credentials.json',
        'token.json',
    ).new_spread_sheets(SAMPLE_SPREADSHEET_ID)

requests = requests.Session()
requests.headers.update({'User-Agent':'un_pogaz/NatureofPredators:sheet:new_posts'})

ARGS = (lambda :(__import__("sys").argv[1:]))()
APP = (lambda :(__import__("sys").argv[0]))()

def help_args():
    for h in ['-h', '--help', '/?']:
        if h in ARGS:
            return True
    
    return False


DOMAIN_EXCLUDE = [
    'reddit.com',
    'i.redd.it',
    'v.redd.it',
    'imgur.com',
    'i.imgur.com',
    'v.imgur.com',
    'forms.gle',
    'youtube.com',
    'i.kym-cdn.com',
]

DOMAIN_STORY_HOST = [
    'archiveofourown.org',
    'www.archiveofourown.org',
    'royalroad.com',
    'www.royalroad.com',
]

SUBREDDITS = ['HFY', 'NatureofPredators', 'NatureOfPredatorsNSFW']



def datetime(timestamp):
    from datetime import datetime
    return datetime.fromtimestamp(timestamp)

def date_from_utc(utc_time):
    return datetime(utc_time).strftime('%m/%d/%Y')

def make_dirname(path):
    import os.path
    dir = os.path.dirname(path)
    if dir: os.makedirs(dir, exist_ok=True)

def read_json(path, default=None) -> dict:
    try:
        with open(path, 'rb') as f:
            return load_json(f.read(), default=default)
    except Exception as ex:
        print(ex)
        return default

def write_json(path, obj, ensure_ascii=False):
    import json
    make_dirname(path)
    with open(path, 'wt', newline='\n', encoding='utf-8') as f:
        f.write(json.dumps(obj, indent=2, ensure_ascii=ensure_ascii))

def load_json(data, default=None):
    import json
    try:
        return json.loads(data)
    except Exception as ex:
        print(ex)
        return default

def read_lines(path, default=None) -> list[str]:
    try:
        with open(path, 'rt', encoding='utf-8') as f:
            return f.read().splitlines(False)
    except Exception as ex:
        print(ex)
        return default

def write_lines(path, *lines):
    if len(lines) == 1 and not isinstance(lines[0], str):
        lines = lines[0]
    
    write_text(path, '\n'.join(lines))

def read_text(path, default=None) -> str:
    try:
        with open(path, 'rt', encoding='utf-8') as f:
            return ''.join(f.readlines())
    except Exception as ex:
        print(ex)
        return default

def write_text(path, text):
    make_dirname(path)
    with open(path, 'wt', newline='\n', encoding='utf-8') as f:
        f.write(text)


def run_animation(awaitable, text_wait, text_end=None):
    import asyncio, time
    global animation_run, msg_last
    run_animation.extra = ''
    msg_last = ''
    
    def start_animation():
        global animation_run, msg_last
        idx = 0
        while animation_run:
            msg = ' '.join([text_wait, run_animation.loop[idx % len(run_animation.loop)], run_animation.extra])
            print(msg + ' '*(len(msg_last)-len(msg)), end="\r")
            msg_last = msg
            idx += 1
            if idx == len(run_animation.loop): idx == 0
            time.sleep(0.2)
    
    from threading import Thread
    
    animation_run = True
    t = Thread(target=start_animation)
    t.start()
    asyncio.run(awaitable())
    animation_run = False
    msg = ' '.join([text_wait, text_end or '> OK'])
    print(msg+' '*(len(msg_last)-len(msg)))
    time.sleep(0.2)
    run_animation.extra = None
    del t
run_animation.extra = None
run_animation.loop = ['|','/','—','\\']
























