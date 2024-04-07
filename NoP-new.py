import os.path

from common import (
    APP,
    ARGS,
    HttpError,
    help_args,
    init_spreadsheets,
    read_subreddit,
)

if help_args():
    print()
    print(os.path.basename(APP), '[id_post]')
    print()
    print('  id_post (optional) id of the oldest post to check back')
    exit()

####################
# oldest_post

oldest_post = ARGS[0] if ARGS else None

def get_oldest_post() -> str:
    spreadsheets = init_spreadsheets()
    
    print('Google Sheets: retrieve the oldest post to check...', oldest_post)
    for r in spreadsheets.get('script-user-data'):
        if not r or r[0] != 'last-post':
            continue
        for d in r[1:]:
            if d:
                return d.strip()
    return None

def set_oldest_post(oldest_post: str):
    spreadsheets = init_spreadsheets()
    
    oldest_post_row = None
    oldest_post_idx_row = None
    oldest_post_idx_column = None
    
    for idx_r,r in enumerate(spreadsheets.get('script-user-data'), 1):
        if not r or r[0] != 'last-post':
            continue
        for idx_c,d in enumerate(r[1:], 1):
            if d:
                oldest_post_row = r
                oldest_post_idx_row = idx_r
                oldest_post_idx_column = idx_c
                break
    
    if oldest_post_row:
        oldest_post_row[oldest_post_idx_column] = (oldest_post or '').strip()
        spreadsheets.update(f'script-user-data!{oldest_post_idx_row}:{oldest_post_idx_row}', [oldest_post_row])


if oldest_post:
    print()
    oldest_post = oldest_post.strip()
    if not oldest_post.startswith('t3_'):
        oldest_post = 't3_'+oldest_post
    print('Oldest post to check', oldest_post)
else:
    rslt = get_oldest_post()
    
    if rslt:
        if not rslt.startswith('t3_'):
            rslt = 't3_'+rslt
        oldest_post = rslt
        print('Google Sheets: oldest post to check', oldest_post)
    else:
        print('Google Sheets: no oldest post to check')

print()

oldest_post, lines = read_subreddit(
    subreddit='NatureofPredators',
    oldest_post=oldest_post,
    exclude_url=True,
)

##with open('- NoP new subreddit.csv', 'at', newline='\n', encoding='utf-8') as f:
##    if lines:
##        f.write('\n')
##        f.write('\n'.join([e.to_string() for e in lines]))
##        f.write('\n')
##exit()

if not lines:
    exit()

lines = [e.to_list() for e in lines]

####################
# update Google Sheets

try:
    print()
    spreadsheets = init_spreadsheets()
    print('Google Sheets: send', len(lines), 'new entry to pending.')
    
    start = len(spreadsheets.get(f"pending!A:H"))+2
    end = start+len(lines)
    
    spreadsheets.update(f"pending!{start}:{end}", lines)
    set_oldest_post(oldest_post)
    
    print('Google Sheets: update completed')
    
except HttpError as err:
    print(err)
    input()

