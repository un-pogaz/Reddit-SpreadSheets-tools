import os.path, time, random
from collections import defaultdict

from common import (
    ARGS, APP, DOMAIN_EXCLUDE, DOMAIN_STORY_HOST, SUBREDDITS,
    help_args, ini_spreadsheets, HttpError, requests, run_animation,
    write_lines, read_lines, datetime, date_from_utc,
    replace_entitie, parse_exclude, parse_body, parse_awards,
)


args = []
for a in ARGS:
    a = a.strip('/')
    if a:
        args.append(a)

authors_file = 'authors_others.txt'
authors_count = 10
if not args or help_args():
    print(os.path.basename(APP), 'author [author ...]')
    print()
    print('ERROR: Need a author as parameter!')
    print(f"  pass - as first argument to exclude url's already present on the sheet")
    print(f'  pass ? to read {authors_count} lines from {authors_file}')
    print(f'  pass * to read all lines from {authors_file}')
    exit()

exclude = args[0] == '-'
if exclude:
    args = args[1:]
special = args[0] if args and args[0] in ['*','?'] else None

authors_lst = []
list_url_data = []
list_authors_empty = []
list_authors_error = []

if special == '?':
    authors_lst = read_lines(authors_file, [])
    args = authors_lst[:authors_count]

elif special == '*':
    args = read_lines(authors_file, [])

if special and not args:
    print(f'{authors_file} is empty.')
    exit()

if exclude and args:
    print('Google Sheets: retrive all url of present post...')
    spreadsheets = ini_spreadsheets()
    try:
        list_url_data = spreadsheets.get('data!G:G')[1:]
        list_url_data = set(r[0] for r in list_url_data if r)
    except HttpError as err:
        list_url_data = []
        print(err)
        input()

args_length = len(args)
for args_idx in range(args_length):
    print()
    author = args[args_idx]
    
    lines = []
    all_post = defaultdict(dict)
    
    # get all posts of author
    async def get_all_post():
        base_url = f'https://www.reddit.com/user/{author}/submitted/.json'
        params = {'sort':'new', 'limit':100}
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
                    
                    parse_exclude(r)
                    parse_body(r, 'md')
                    parse_awards(r)
                    
                    r['permalink'] = 'https://www.reddit.com' + r['permalink']
                    
                    if r['subreddit'] in SUBREDDITS:
                        all_post[r['subreddit']][r['name']] = {k:r[k] for k in sorted(r.keys())}
                    
                    params['after'] = r['name']
            else:
                loop = False
            time.sleep(1)
    
    run_animation(get_all_post, f'Loading Reddit post for {author}'+ (f' [{args_idx+1}/{args_length}]' if args_length > 1 else '') )
    
    # filtre posts
    for subreddit in SUBREDDITS:
        self_domain = f'self.{subreddit}'
        for item in reversed(all_post.get(subreddit, {}).values()):
            if item.get('created_utc', 0) < 1649689768:
                continue
            
            link_post = item['permalink']
            if link_post in list_url_data:
                continue
            
            if subreddit == 'NatureofPredators' and (item['link_flair_text'] or '').lower() not in ['fanfic', 'nsfw']:
                continue
            
            link_redirect = ''
            domain = item.get('domain', self_domain)
            if domain in DOMAIN_STORY_HOST:
                link_redirect = item['url_overridden_by_dest']
            elif domain in DOMAIN_EXCLUDE:
                if item.get('selftext'):
                    pass
                else:
                    continue
            elif domain != self_domain:
                continue
            
            cw = 'Mature' if item['over_18'] or (item['link_flair_text'] or '').lower() == 'nsfw' else ''
            if cw and subreddit == 'NatureOfPredatorsNSFW':
                cw = 'Adult'
            
            lines.append([
                datetime(item['created_utc']),
                date_from_utc(item['created_utc']),
                'Fan-fic NoP1',
                replace_entitie(item['title']),
                author,
                cw,
                '',
                link_post,
                link_redirect,
            ])
    
    # write posts
    lines.sort(key=lambda x:x[0])
    for idx in range(len(lines)):
        lines[idx] = '\t'.join(lines[idx][1:])
    
    if special == '*':
        subdir = 'multi-authors'
    else:
        subdir = '.'
    os.makedirs(subdir, exist_ok=True)
    
    if lines or not special:
        write_lines(os.path.join(subdir, f'{author}.csv'), lines)
    else:
        if not all_post:
            lst = list_authors_error
            filename = f'! ERROR author.txt'
        else:
            lst = list_authors_empty
            filename = f'- empty author.txt'
        lst.append(author)
        write_lines(os.path.join(subdir, filename), lst)
    
    msg = '' if all_post else '!!ERROR!!'
    print(f'Data extracted u/{author}.', 'Post found:', len(lines), msg)
    
    if special == '*':
        i = random.randint(8,22)
        msg = f'Waiting {i} seconds (to appease reddit)...'
        print(msg, end='\r')
        time.sleep(i+round(random.random(),1))
        print(' '*len(msg), end='\r')

if special == '?':
    write_lines(authors_file, authors_lst[authors_count:])
