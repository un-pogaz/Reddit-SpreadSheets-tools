import os.path
from common import (
    ARGS, APP, DOMAIN_EXCLUDE, DOMAIN_STORY_HOST,
    help_args, ini_spreadsheets, HttpError, requests, run_animation,
    parse_exclude, parse_body, parse_awards, PostEntry,
)


if help_args():
    print(os.path.basename(APP), '[id_post]')
    print()
    print('ERROR: Need a author as parameter!')
    print('  id_post (optional) id of the oldest post to check back')
    exit()

spreadsheets = ini_spreadsheets()

####################
# get oldest_post

oldest_post = ARGS[0] if ARGS else None
oldest_post_cell = "pending!A2"

if oldest_post:
    print()
    if not oldest_post.startswith('t3_'):
        oldest_post = 't3_'+oldest_post
    print('Oldest post to check', oldest_post)
else:
    try:
        print('Google Sheets: retrive the oldest post to check')
        rslt = spreadsheets.get(oldest_post_cell)
        
        try:
            while not isinstance(rslt, str):
                rslt = rslt[0]
        except:
            rslt = ''
        rslt = rslt.strip()
        
        if rslt:
            oldest_post = rslt
            print('Google Sheets: oldest post to check', oldest_post)
        else:
            print('Google Sheets: retrive last post')
        
    except HttpError as err:
        print(err)
        input()

try:
    list_url_data = spreadsheets.get('data!G:G')[1:]
    list_url_data = set(r[0] for r in list_url_data if r)
except HttpError as err:
    list_url_data = []
    print(err)
    input()

print()

####################
# read subreddit

all_post = {}
async def read_subreddit():
    import time
    base_url = 'https://www.reddit.com/r/NatureofPredators/new/.json'
    params = {'sort':'new', 'limit':100, 'after':'', 'before':oldest_post}
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
                
                all_post[r['name']] = {k:r[k] for k in sorted(r.keys())}
                
                params['after'] = r['name']
        
        if len(tbl) < params['limit']:
            loop = False
        time.sleep(1)

run_animation(read_subreddit, 'Loading new post on post r/NatureofPredators')
all_post = {k:all_post[k] for k in sorted(all_post.keys())}
print('Total new post to analyze:', len(all_post))

####################
# analyze posts

lines: list[PostEntry] = []
for item in all_post.values():
    
    link_post = item['permalink']
    if link_post in list_url_data:
        continue
    
    if (item['link_flair_text'] or '').lower() not in ['', 'fanfic', 'nsfw']:
        continue
    
    link_redirect = ''
    self_domain = 'self.NatureofPredators'
    domain = item.get('domain', self_domain)
    if domain != self_domain:
        if domain in ['self.NatureofPredators', 'self.HFY', 'self.NatureOfPredatorsNSFW']:
            link_post = 'https://www.reddit.com' + item['url_overridden_by_dest']
        elif domain in DOMAIN_STORY_HOST:
            link_redirect = item['url_overridden_by_dest']
        elif domain in DOMAIN_EXCLUDE:
            if item.get('selftext'):
                pass
            else:
                continue
        
        else:
            print('Crossposted', domain)
            print('===============================')
            print(item)
            print('===============================')
            input()
    
    lines.append(PostEntry(item))
    
    oldest_post = item['name']

##with open('- NoP new subreddit.csv', 'at', newline='\n', encoding='utf-8') as f:
##    if lines:
##        f.write('\n'.join(['\t'.join(l) for l in lines]))
##        f.write('\n')

print('Data extracted from r/NatureofPredators.', 'New lines added:', len(lines))

if not lines:
    exit()

lines = [e.to_list() for e in lines]

####################
# update Google Sheets

try:
    print()
    print('Google Sheets: send', len(lines), 'new entry to pending.')
    
    start = len(spreadsheets.get(f"pending!A:H"))+1
    lines.insert(0, [''])
    end = start+len(lines)
    
    spreadsheets.update(f"pending!{start}:{end}", lines)
    spreadsheets.update(oldest_post_cell, [[oldest_post]])
    
    print('Google Sheets: update completed')
    
except HttpError as err:
    print(err)
    input()

