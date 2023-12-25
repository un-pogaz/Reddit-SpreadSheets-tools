import requests as _requests

from google_api_client import SpreadSheetsClient, HttpError

# The ID of the spreadsheet.
SAMPLE_SPREADSHEET_ID = "1nOtYmv_d6Qt1tCX_63uE2yWVFs6-G5x_XJ778lD9qyU"

def ini_spreadsheets() -> SpreadSheetsClient:
    if hasattr(ini_spreadsheets, '_client'):
        rslt = ini_spreadsheets._client
    else:
        ini_spreadsheets._client = rslt = SpreadSheetsClient(
            'credentials.json',
            'token.json',
        ).new_spread_sheets(SAMPLE_SPREADSHEET_ID)
    
    return rslt

requests = _requests.Session()
requests.headers.update({'User-Agent':'un_pogaz/NatureofPredators:sheet:new_posts'})

ARGS = (lambda :(__import__("sys").argv[1:]))()
APP = (lambda :(__import__("sys").argv[0]))()

def help_args() -> bool:
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
SUBREDDITS_DOMAIN = [f'self.{e}' for e in SUBREDDITS]


def make_dirname(path):
    import os.path
    dir = os.path.dirname(path)
    if dir: os.makedirs(dir, exist_ok=True)

def read_json(path, default=None) -> dict|list:
    try:
        with open(path, 'rb') as f:
            return load_json(f.read(), default=default)
    except Exception as ex:
        print(ex)
        return default

def write_json(path: str, obj, ensure_ascii=False):
    import json
    make_dirname(path)
    with open(path, 'wt', newline='\n', encoding='utf-8') as f:
        f.write(json.dumps(obj, indent=2, ensure_ascii=ensure_ascii))

def load_json(data, default=None) -> dict|list:
    import json
    try:
        return json.loads(data)
    except Exception as ex:
        print(ex)
        return default

def read_lines(path: str, default=None) -> list[str]:
    try:
        with open(path, 'rt', encoding='utf-8') as f:
            return f.read().splitlines(False)
    except Exception as ex:
        print(ex)
        return default

def write_lines(path: str, *lines: list[str]):
    if len(lines) == 1 and not isinstance(lines[0], str):
        lines = lines[0]
    
    write_text(path, '\n'.join(lines))

def read_text(path: str, default=None) -> str:
    try:
        with open(path, 'rt', encoding='utf-8') as f:
            return ''.join(f.readlines())
    except Exception as ex:
        print(ex)
        return default

def write_text(path: str, text: str):
    make_dirname(path)
    with open(path, 'wt', newline='\n', encoding='utf-8') as f:
        f.write(text)


def run_animation(awaitable, text_wait: str, text_end: str=None):
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


exclude_items = [
    'preview',
    'user_reports', 'mod_reports', 'removal_reason', 'mod_reason_by', 'num_reports', 'report_reasons', 'removed_by', 'mod_note', 'mod_reason_title',
    'approved_at_utc', 'approved_by', 'can_mod_post',
    'media', 'media_embed', 'secure_media', 'secure_media_embed', 'media_metadata', 'gallery_data',
    
    'awarders', 'quarantine', 'likes', 'wls', 'pwls', 'clicked', 'visited',
    'is_crosspostable', 'num_crossposts', 'crosspost_parent', 'crosspost_parent_list',
    'subreddit_subscribers', 'stickied', 'parent_whitelist_status', 'whitelist_status', 'contest_mode',
    'is_robot_indexable', 'no_follow', 'view_count', 'suggested_sort', 'allow_live_comments',
    'link_flair_richtext', 'link_flair_template_id', 'hide_score', 'is_created_from_ads_ui',
    'is_original_content', 'is_reddit_media_domain', 'removed_by_category',
    
    'gilded', 'gildings', 'can_gild', 'treatment_tags', 'post_hint', 'thumbnail_height', 'thumbnail_width',
    'author_flair_background_color', 'author_flair_css_class', 'author_flair_richtext', 'author_flair_template_id',
    'author_flair_text', 'author_flair_text_color', 'author_flair_type', 'author_premium',
    'link_flair_background_color', 'link_flair_css_class', 'link_flair_text_color', 'link_flair_type',
    
    'replies',
]

def parse_exclude(post: dict) -> dict:
    for d in exclude_items:
        if d in post:
            del post[d]
    
    return post

def parse_body(post: dict, keep_body: bool|None) -> dict:
    if isinstance(keep_body, str):
        keep_body = keep_body.lower()
    
    def del_md():
        return keep_body is False or keep_body and not (keep_body is True or 'md' in keep_body or 'markdown' in keep_body)
    
    def del_html():
        return keep_body is False or keep_body and not (keep_body is True or 'html' in keep_body)
    
    if 'body' in post:
        if del_md():
            del post['body']
        else:
            post['body'] = parse_rawhtml(post['body'])
    
    if 'selftext' in post:
        if del_md():
            del post['selftext']
        else:
            post['selftext'] = parse_rawhtml(post['selftext'])
    
    if 'body_html' in post:
        if del_html():
            del post['body_html']
        else:
            post['body_html'] = parse_rawhtml(post['body_html'])
    
    if 'selftext_html' in post:
        if del_html():
            del post['selftext_html']
        else:
            post['selftext_html'] = parse_rawhtml(post['selftext_html'])
        
    return post

awards_filter = ['name', 'description', 'award_type' ,'icon_url', 'static_icon_url']

def parse_awards(post: dict) -> dict:
    awards = []
    for d in post.get('all_awardings', []):
        awards.append({k:d[k] for k in awards_filter})
    
    if awards:
        post['all_awardings'] = awards
    
    return post

def parse_content(post: dict) -> str:
    parse_exclude(post)
    parse_body(post, 'md')
    parse_awards(post)
    
    if not post['permalink'].startswith('https://www.reddit.com'):
        post['permalink'] = 'https://www.reddit.com' + post['permalink']
    
    return post

def replace_entitie(text: str) -> str:
    return text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&#39;', "'")

def parse_rawhtml(text: str) -> str:
    import re
    
    if not text:
        return text
    html = replace_entitie(text).replace('\n\n', '\n').replace('<br>', '<br/>').replace('<hr>', '<hr/>')
    html = html.removeprefix('<!-- SC_OFF -->').removesuffix('<!-- SC_ON -->')
    return re.sub(r'<a href="https://preview.redd.it/([^"]+)">https://preview.redd.it/\1</a>', r'<img src="https://preview.redd.it/\1"/>', html)


class PostEntry():
    
    DATETIME_FORMAT = '%m/%d/%Y'
    
    def __init__(self, post_item: dict):
        from datetime import datetime
        
        if post_item.get('domain', None) in DOMAIN_STORY_HOST:
            link_redirect = post_item['url_overridden_by_dest']
        else:
            link_redirect = ''
        
        cw = 'Mature' if post_item['over_18'] or (post_item['link_flair_text'] or '').lower() == 'nsfw' else ''
        if cw and post_item['subreddit'] == 'NatureOfPredatorsNSFW':
            cw = 'Adult'
        
        self._post_item = post_item
        self.created = datetime.fromtimestamp(post_item['created_utc'])
        self.timeline = ''
        self.title = replace_entitie(post_item['title'])
        self.authors = post_item['author']
        self.content_warning = cw
        self.statue = ''
        self.link = post_item['permalink']
        self.description = link_redirect
    
    def to_list(self) -> list[str]:
        return [
            self.created.strftime(self.DATETIME_FORMAT),
            self.timeline,
            self.title,
            self.authors,
            self.content_warning,
            self.statue,
            self.link,
            self.description,
        ]
    
    def to_string(self) -> str:
        return '\t'.join(self.to_list())
    
    def __str__(self) -> str:
        return self.__class__.__name__+'('+','.join([self.created.isoformat(), repr(self.title), repr(self.link)])+')'

def post_is_to_old(post_item: dict) -> bool:
    return post_item['created_utc'] < 1649689768

def get_filtered_post(source_data: list[dict], exclude_url: list[str]) -> list[PostEntry]:
    rslt = []
    
    for item in source_data:
        if post_is_to_old(item):
            continue
        
        if item['subreddit'] not in SUBREDDITS:
            continue
        
        parse_content(item)
        
        if item['permalink'] in exclude_url:
            continue
        
        subreddit = item['subreddit']
        if subreddit == 'NatureofPredators' and (item['link_flair_text'] or '').lower() not in ['', 'fanfic', 'nsfw']:
            continue
        
        domain = item['domain']
        if domain in SUBREDDITS_DOMAIN or domain in DOMAIN_STORY_HOST:
            pass
        elif domain != f'self.{subreddit}':
            if item.get('selftext'):
                pass
            else:
                continue
        
        entry = PostEntry(item)
        if subreddit == 'HFY' or subreddit == 'NatureofPredators' and (item['link_flair_text'] or '').lower() in ['fanfic', 'nsfw']:
            entry.timeline = 'Fan-fic NoP1'
        if not entry.timeline:
            entry.timeline = 'none'
        
        rslt.append(entry)
    
    rslt.sort(key=lambda x:x.created)
    return rslt

def read_subreddit(subreddit: str, oldest_post: str|None, exclude_url: list[str]) -> tuple[list[PostEntry], str]:
    all_post = []
    base_url = f'https://www.reddit.com/r/{subreddit}/new/.json'
    
    async def read_posts():
        import time
        params = {'sort':'new', 'limit':100, 'before':oldest_post}
        count = 0
        loop = True
        
        while loop:
            tbl = requests.get(base_url, params=params, timeout=1000).json().get('data', {}).get('children', {})
            if tbl:
                count = count + len(tbl)
                run_animation.extra = str(count)
                loop = True
                
                for r in tbl:
                    r = r['data']
                    all_post.append(r)
                    params['after'] = r['name']
            
            if len(tbl) < params['limit']:
                loop = False
            time.sleep(1)
    
    run_animation(read_posts, f'Loading new post on post r/{subreddit}')
    print('Total new post to analyze:', len(all_post))
    
    recent_post = all_post[0]['name']
    self_domain = f'self.{subreddit}'
    for item in all_post:
        domain = item['domain']
        if domain != self_domain and domain in SUBREDDITS_DOMAIN:
            item['permalink'] = item['url_overridden_by_dest']
    
    lines = get_filtered_post(all_post, exclude_url)
    print(f'Data extracted from r/{subreddit}.', 'New lines added:', len(lines))
    
    return recent_post, lines
