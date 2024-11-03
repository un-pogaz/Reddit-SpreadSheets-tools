import re
from collections import defaultdict
from functools import cache

import requests as _requests

from google_api_client import HttpError, SpreadSheetsClient, SpreadSheets

# The ID of the spreadsheet.
SAMPLE_SPREADSHEET_ID = "1nOtYmv_d6Qt1tCX_63uE2yWVFs6-G5x_XJ778lD9qyU"

@cache
def init_spreadsheets() -> SpreadSheets:
    rslt = SpreadSheetsClient(
        credentials_oauth2 = 'credentials.json',
        token_json = 'token.json',
    ).new_spreadsheets(SAMPLE_SPREADSHEET_ID)
    
    return rslt

requests = _requests.Session()
requests.headers.update({'User-Agent':'un_pogaz/NatureofPredators:sheet:new_posts'})


DOMAIN_EXCLUDE = [
    'reddit.com',
    'i.redd.it',
    'v.redd.it',
    'imgur.com',
    'i.imgur.com',
    'v.imgur.com',
    'forms.gle',
    'youtube.com',
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

def write_lines(path: str, lines: list[str]):
    if isinstance(lines, str):
        lines = [lines]
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
    import asyncio
    import time
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


def parse_body(post: dict) -> dict:
    keys = [
        'body',
        'body_html',
        'selftext',
        'selftext_html',
    ]
    for k in keys:
        if k in post:
            post[k] = parse_rawhtml(post[k] or '')
    
    return post

def parse_content(post: dict) -> dict:
    parse_body(post)
    
    post['title'] = replace_entitie(post['title']).strip()
    
    for k in ['permalink', 'url', 'url_overridden_by_dest']:
        if k in post and post[k].startswith('/r/'):
            post[k] = 'https://www.reddit.com' + post[k]
    
    return post

def replace_entitie(text: str) -> str:
    return text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&#39;', "'")

def parse_rawhtml(text: str) -> str:
    if not text:
        return text
    html = replace_entitie(text).replace('\n\n', '\n').replace('<br>', '<br/>').replace('<hr>', '<hr/>')
    html = html.removeprefix('<!-- SC_OFF -->').removesuffix('<!-- SC_ON -->')
    return re.sub(r'<a href="https://preview.redd.it/([^"]+)">https://preview.redd.it/\1</a>', r'<img src="https://preview.redd.it/\1"/>', html)

def numeric_id(text_id) -> int:
    # base 36 / 0123456789abcdefghijklmnopqrstuvwxyz
    if not text_id:
        return -1
    return int(text_id.removeprefix('t3_'), base=36)

def parse_post_id(post_id: str):
    post_id = post_id.strip()
    if not post_id.startswith('t3_'):
        post_id = 't3_'+post_id
    return post_id

class PostEntry():
    
    DATETIME_FORMAT = '%m/%d/%Y'
    
    def __init__(self, post_item: dict):
        from datetime import datetime
        
        test_url = post_item.get('url_overridden_by_dest', '')
        if 'reddit.com/r/' in test_url or 'reddit.com/user/' in test_url:
            permalink = test_url
        else:
            permalink = post_item['permalink']
        
        permalink = re.sub(r'\w+.reddit.com', r'www.reddit.com', permalink)
        permalink = re.sub(r'\?.*', '', permalink)
        
        self._post_item = post_item
        self.created: datetime = datetime.fromtimestamp(post_item['created_utc'])
        self.timeline: str = ''
        self.title: str = post_item['title']
        self.authors: str = post_item['author']
        self.content_warning: str = ''
        self.statue: str = ''
        self.link: str = permalink
        self.description: str = ''
        self.link_redirect: str = ''
        self.post_id: str = post_item['name']
    
    def to_list(self, datetime_format: str=DATETIME_FORMAT) -> list[str]:
        return [
            self.created.strftime(datetime_format).lstrip('0').replace('/0', '/'),
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
    # https://www.reddit.com/r/HFY/comments/u19xpa/the_nature_of_predators/
    return numeric_id(post_item['id']) < numeric_id('u19xpa')

def get_filtered_post(
    source_data: list[dict],
    *,
    exclude_url: list[str]|bool =True,
    
    title_timelines: dict[str, str]|bool =True,
    chapter_inside_post: list[str]|bool =True,
    check_links_map: dict[str, list[str]]|bool =True,
    check_links_search: dict[str, str]|bool =True,
    domain_story_host: list[str]|bool =True,
    additional_regex: list[tuple[str, str]]|bool =True,
    chapter_regex: list[tuple[str, str]]|bool =True,
    status_regex: list[tuple[str, str]]|bool =True,
    timeline_key_words: dict[str, list[str]]|bool =True,
    co_authors: dict[str, list[str]]|bool =True,
    comics: list[str]|bool =True,
    
    dont_fetch_user_data: bool=False,
) -> list[PostEntry]:
    """
    If exclude_url is True, get the exclude_url list from the spreadsheets.
    
    Same for title_timelines, chapter_inside_post, check_links_map, check_links_search,
    domain_story_host, additional_regex, chapter_regex, status_regex, timeline_key_words,
    co_authors, comics.
    
    dont_fetch_user_data disable the retriving of the script-user-data for default values.
    Only inputed values will be used, at the excpetion of exclude_url will be still retriving independantly.
    """
    
    rslt = []
    
    if exclude_url is True:
        exclude_url = get_url_data()
    if hasattr(exclude_url, '__iter__'):
        exclude_url = set(exclude_url)
    else:
        exclude_url = []
    
    
    # title_timelines
    if title_timelines is True and not dont_fetch_user_data:
        title_timelines = get_title_timelines()
    if not isinstance(title_timelines, dict):
        title_timelines = {}
    
    # chapter_inside_post
    if chapter_inside_post is True and not dont_fetch_user_data:
        chapter_inside_post = get_chapter_inside_post()
    if not isinstance(chapter_inside_post, list):
        chapter_inside_post = []
    
    # check_links_map
    if check_links_map is True and not dont_fetch_user_data:
        check_links_map = get_check_links_map()
    if not isinstance(check_links_map, dict):
        check_links_map = {}
    
    # check_links_search
    if check_links_search is True and not dont_fetch_user_data:
        check_links_search = get_check_links_search()
    if not isinstance(check_links_search, dict):
        check_links_search = {}
    
    # domain_story_host
    if domain_story_host is True and not dont_fetch_user_data:
        domain_story_host = get_domain_story_host()
    if not isinstance(domain_story_host, list):
        domain_story_host = []
    
    regex_flags = re.ASCII|re.IGNORECASE
    
    # additional_regex
    if additional_regex is True and not dont_fetch_user_data:
        additional_regex = get_additional_regex()
    if not isinstance(additional_regex, list):
        additional_regex = []
    
    # chapter_regex
    if chapter_regex is True and not dont_fetch_user_data:
        chapter_regex = get_chapter_regex()
    if not isinstance(chapter_regex, list):
        chapter_regex = []
    
    # status_regex
    if status_regex is True and not dont_fetch_user_data:
        status_regex = get_status_regex()
    if not isinstance(status_regex, list):
        status_regex = []
    
    # timeline_key_words
    if timeline_key_words is True and not dont_fetch_user_data:
        timeline_key_words = get_timeline_key_words()
    if not isinstance(timeline_key_words, dict):
        timeline_key_words = {}
    
    # co_authors
    if co_authors is True and not dont_fetch_user_data:
        co_authors = get_co_authors()
    if not isinstance(co_authors, dict):
        co_authors = {}
    
    # comics
    if comics is True and not dont_fetch_user_data:
        comics = get_comics()
    if not isinstance(comics, list):
        comics = []
    
    for item in source_data:
        if post_is_to_old(item):
            continue
        
        subreddit = item['subreddit']
        if subreddit not in SUBREDDITS:
            continue
        
        if subreddit == 'NatureofPredators' and (item['link_flair_text'] or '').lower() not in ['', 'fanfic', 'nsfw', 'roleplay']:
            continue
        
        if item.get('poll_data'):
            continue
        
        parse_content(item)
        
        post_text = (item.get('selftext') or '').strip()
        if not post_text:
            crosspost_parent_list = item.get('crosspost_parent_list', [])
            if crosspost_parent_list:
                post_text = crosspost_parent_list[0].get('selftext', '')
        post_text = (post_text or '').strip()
        
        entry = PostEntry(item)
        if entry.link in exclude_url:
            continue
        
        entry.title = entry.title.replace("´", "’")
        
        def get_entry_text(input: list[str]|dict[str, str], default=None):
            title_lower = entry.title.lower()
            rslt = None
            for title in input:
                if not title:
                    continue
                
                if title.startswith('^') and title_lower.startswith(title.lower()[1:]):
                    rslt = title
                    break
                elif title.lower() in title_lower:
                    rslt = title
                    break
            
            if isinstance(input, dict):
                rslt = input.get(rslt)
            if rslt is None:
                rslt = default
            return rslt
        
        def get_entry_regex(input: list[tuple[str, str]]) -> tuple[str, str]:
            for search,value in input:
                if not search or not value:
                    continue
                if re.search(search, entry.title, flags=regex_flags):
                    return search, value
        
        def parse_space(text):
            return re.sub(r'\s+', ' ', text.strip()).strip()
        
        
        domain = item['domain']
        if domain in SUBREDDITS_DOMAIN or domain in domain_story_host or domain.endswith('reddit.com'):
            pass
        elif get_entry_text(comics):
            pass
        elif not post_text:
            continue
        
        
        if item['over_18'] or (item['link_flair_text'] or '').lower() == 'nsfw':
            entry.content_warning = 'Mature'
        if item['subreddit'] == 'NatureOfPredatorsNSFW':
            entry.content_warning = 'Adult'
        
        if (item['link_flair_text'] or '').lower() == 'roleplay':
            entry.statue = 'Roleplay'
        
        if subreddit == 'HFY' or subreddit == 'NatureofPredators' and (item['link_flair_text'] or '').lower() in ['fanfic', 'nsfw']:
            entry.timeline = 'Fan-fic NoP1'
        
        if not entry.timeline:
            entry.timeline = 'none'
        
        # domain_story_host
        if domain in domain_story_host:
            link_redirect = item['url_overridden_by_dest']
        else:
            link_redirect = ''
        if link_redirect:
            entry.link_redirect = link_redirect
            entry.description = link_redirect
        
        # timeline_key_words
        for timeline,key_words in timeline_key_words.items():
            if not key_words or not timeline:
                continue
            if re.search(r'\s('+'|'.join(key_words)+r')s?[^a-z]', post_text, flags=regex_flags):
                entry.timeline = timeline
        
        # title_timelines
        entry.timeline = get_entry_text(title_timelines, entry.timeline)
        
        # co_authors
        lst_authors = [entry.authors]
        for co_author in get_entry_text(co_authors, []):
            if not co_author:
                continue
            if co_author not in lst_authors:
                lst_authors.append(co_author)
        entry.authors = ' & '.join(lst_authors)
        
        # additional_regex
        search_additional = get_entry_regex(additional_regex)
        if search_additional:
            entry.title = parse_space(re.sub(search_additional[0], ' '+search_additional[1]+' ', entry.title, flags=regex_flags, count=1))
        
        # status_regex
        search_status = get_entry_regex(status_regex)
        if search_status:
            entry.statue = search_status[1]
        
        # chapter_regex
        search_replace = get_entry_regex(chapter_regex)
        if search_replace:
            entry.title = parse_space(re.sub(search_replace[0], ' '+search_replace[1]+' ', entry.title, flags=regex_flags, count=1))
        
        # check_links_map, check_links_search
        for link_name in get_entry_text(check_links_map, []):
            if entry.link_redirect:
                # is a link post, no text to analyze
                break
            if not link_name:
                continue
            url = re.search(check_links_search.get(link_name, ''), post_text, flags=re.ASCII)
            if url:
                url = url.group(0)
            if url:
                if url not in entry.description:
                    entry.description = (entry.description + '\n'+url).strip()
            else:
                entry.title += ' {'+link_name+' link}'
        
        # chapter_inside_post
        if get_entry_text(chapter_inside_post):
            entry.title += ' <chapter inside post>'
        
        entry.title = parse_space(entry.title)
        
        rslt.append(entry)
    
    rslt.sort(key=lambda x:x.created)
    
    index_duplicate = []
    url_duplicate = defaultdict(list)
    for idx,entry in enumerate(rslt):
        url_duplicate[entry.link].append(idx)
    for v in url_duplicate.values():
        if len(v) > 1:
            index_duplicate.extend(v[1:])
    for idx in sorted(index_duplicate, reverse=True):
        del rslt[idx]
    
    return rslt

def read_subreddit(
    subreddit: str,
    oldest_post: str|None,
    *,
    subreddit_is_author: bool =False,
    additional_loading_message: str=None,
    exclude_url: list[str]|bool =True,
    
    title_timelines: dict[str, list[str]]|bool =True,
    chapter_inside_post: list[str]|bool =True,
    check_links_map: dict[str, list[str]]|bool =True,
    check_links_search: dict[str, str]|bool =True,
    domain_story_host: list[str]|bool =True,
    additional_regex: list[tuple[str, str]]|bool =True,
    chapter_regex: list[tuple[str, str]]|bool =True,
    status_regex: list[tuple[str, str]]|bool =True,
    timeline_key_words: dict[str, list[str]]|bool =True,
    co_authors: dict[str, list[str]]|bool =True,
    comics: list[str]|bool =True,
    
    dont_fetch_user_data: bool=False,
) -> list[PostEntry]:
    """
    If exclude_url is True, get the exclude_url list from the spreadsheets.
    
    Same for title_timelines, chapter_inside_post, check_links_map, check_links_search,
    domain_story_host, additional_regex, chapter_regex, status_regex, timeline_key_words, co_authors
    co_authors, comics.
    
    dont_fetch_user_data disable the retriving of the script-user-data for default values.
    Only inputed values will be used, at the excpetion of exclude_url will be still retriving independantly.
    """
    
    all_post = []
    if subreddit_is_author:
        base_url = f'https://www.reddit.com/user/{subreddit}/submitted/.json'
    else:
        base_url = f'https://www.reddit.com/r/{subreddit}/new/.json'
    
    if not oldest_post:
        oldest_post = '0'
    
    async def read_posts():
        import time
        params = {'sort':'new', 'limit':100}
        count = 0
        loop = True
        
        while loop:
            tbl = requests.get(base_url, params=params, timeout=60).json().get('data', {}).get('children', {})
            if tbl:
                count += len(tbl)
                run_animation.extra = str(count)
                loop = True
                
                for r in tbl:
                    r = r['data']
                    if numeric_id(r['name']) <= numeric_id(oldest_post):
                        loop = False
                    else:
                        all_post.append(r)
                    params['after'] = r['name']
            
            if len(tbl) < params['limit'] or count >= 1000:
                loop = False
            time.sleep(1)
    
    if subreddit_is_author:
        msg = f'Loading Reddit post for u/{subreddit}'
    else:
        msg = f'Loading Reddit post on r/{subreddit}'
    if additional_loading_message:
        msg = (msg + additional_loading_message).strip()
    run_animation(read_posts, msg)
    print('Total post to analyze:', len(all_post))
    
    lines = get_filtered_post(
        source_data=all_post,
        exclude_url=exclude_url,
        
        title_timelines=title_timelines,
        chapter_inside_post=chapter_inside_post,
        check_links_map=check_links_map,
        check_links_search=check_links_search,
        domain_story_host=domain_story_host,
        additional_regex=additional_regex,
        chapter_regex=chapter_regex,
        status_regex=status_regex,
        timeline_key_words=timeline_key_words,
        co_authors=co_authors,
        comics=comics,
        
        dont_fetch_user_data=dont_fetch_user_data,
    )
    
    if subreddit_is_author:
        msg = f'Data extracted for u/{subreddit}.'
    else:
        msg = f'Data extracted from r/{subreddit}.'
    print(msg, 'Post found:', len(lines))
    
    return lines


@cache
def get_url_data() -> set:
    spreadsheets = init_spreadsheets()
    print('Google Sheets: retrieve all url of present post...')
    try:
        rslt = spreadsheets.get('data!G:G')[1:]
        rslt = set(r[0] for r in rslt if r)
    except HttpError as err:
        rslt = set()
        print(err)
        input()
    return rslt

@cache
def get_user_data() -> dict[str, list[list[str]]]:
    spreadsheets = init_spreadsheets()
    print('Google Sheets: retrieve the script-user-data...')
    
    try:
        rslt = defaultdict(list)
        for r in spreadsheets.get('script-user-data'):
            if not r:
                continue
            
            t, r = r[0], r[1:]
            if t and r:
                rslt[t].append(r)
        
    except HttpError as err:
        rslt = {}
        print(err)
        input()
    return rslt

def is_fulled_row(row, length):
    if len(row) < length:
        return False
    for idx in range(length):
        if not row[idx]:
            return False
    return True

@cache
def get_title_timelines() -> dict[str, list[str]]:
    rslt = {}
    for r in get_user_data().get('timeline', []):
        if not is_fulled_row(r, 2):
            continue
        rslt[r[0]] = r[1]
    return rslt

@cache
def get_chapter_inside_post() -> list[str]:
    rslt = []
    for r in get_user_data().get('chapter-inside-post', []):
        if not r[0]:
            continue
        rslt.append(r[0])
    return rslt

@cache
def get_check_links_search() -> dict[str, str]:
    rslt = {}
    for r in get_user_data().get('domain-story-host', []):
        if not is_fulled_row(r, 3):
            continue
        rslt[r[1]] = r[2]
    return rslt

@cache
def get_check_links_map() -> dict[str, list[str]]:
    rslt = {}
    for r in get_user_data().get('check-links', []):
        if not r[0]:
            continue
        lst = [e for e in r[1:] if e]
        if not lst:
            continue
        rslt[r[0]] = lst
    return rslt

@cache
def get_domain_story_host() -> list[str]:
    rslt = []
    for r in get_user_data().get('domain-story-host', []):
        if not r[0]:
            continue
        rslt.append(r[0])
    return rslt

@cache
def get_additional_regex() -> list[tuple[str, str]]:
    rslt = []
    for r in get_user_data().get('additional-regex', []):
        if not r:
            continue
        if len(r) < 2:
            r.append(' ')
        rslt.append((r[0], r[1]))
    return rslt

@cache
def get_chapter_regex() -> list[tuple[str, str]]:
    rslt = []
    for r in get_user_data().get('chapter-regex', []):
        if not is_fulled_row(r, 2):
            continue
        rslt.append((r[0], r[1]))
    return rslt

@cache
def get_status_regex() -> list[tuple[str, str]]:
    rslt = []
    for r in get_user_data().get('status-regex', []):
        if not is_fulled_row(r, 2):
            continue
        rslt.append((r[0], r[1]))
    return rslt

@cache
def get_timeline_key_words() -> dict[str, list[str]]:
    rslt = defaultdict(list)
    for r in get_user_data().get('timeline-key-word', []):
        if not is_fulled_row(r, 2):
            continue
        rslt[r[1]].append(r[0])
    return rslt

@cache
def get_co_authors() -> dict[str, list[str]]:
    rslt = defaultdict(list)
    for r in get_user_data().get('co-authors', []):
        if not r[0]:
            continue
        lst = []
        for e in r[1:]:
            lst.extend(e.split('&'))
        lst = [e.strip() for e in lst]
        lst = set([e for e in lst if e])
        if not lst:
            continue
        rslt[r[0]].extend(sorted(lst))
    return rslt

@cache
def get_comics() -> list[str]:
    rslt = []
    for r in get_user_data().get('comics', []):
        if not r[0]:
            continue
        rslt.append(r[0])
    return rslt
