import os.path

from common import (
    ARGS, APP, SUBREDDITS_DOMAIN, ini_spreadsheets, HttpError,
    help_args, requests, run_animation, get_filtered_post,
)


if help_args():
    print()
    print(os.path.basename(APP), '[id_post]')
    print()
    print('  id_post (optional) id of the oldest post to check back')
    exit()

spreadsheets = ini_spreadsheets()

####################
# get oldest_post

oldest_post = ARGS[0] if ARGS else None

if oldest_post:
    print()
    if not oldest_post.startswith('t3_'):
        oldest_post = 't3_'+oldest_post
    print('Oldest post to check', oldest_post)

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

all_post = []
async def read_subreddit():
    import time
    base_url = 'https://www.reddit.com/r/NatureOfPredatorsNSFW/new/.json'
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

run_animation(read_subreddit, 'Loading new post on post r/NatureOfPredatorsNSFW')
print('Total new post to analyze:', len(all_post))

if not all_post:
    exit()

####################
# analyze posts

oldest_post = all_post[0]['name']
self_domain = 'self.NatureOfPredatorsNSFW'
for item in all_post:
    domain = item['domain']
    if domain != self_domain and domain in SUBREDDITS_DOMAIN:
        item['permalink'] = item['url_overridden_by_dest']

lines = get_filtered_post(all_post, list_url_data)

with open('- NoP-NSFW new subreddit.csv', 'at', newline='\n', encoding='utf-8') as f:
    if lines:
        f.write('\n'.join([e.to_string() for e in lines]))
        f.write('\n')

print('Data extracted from r/NatureofPredators.', 'New lines added:', len(lines))
