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

spreadsheets = init_spreadsheets()

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
        print('Google Sheets: retrieve the oldest post to check')
        rslt = spreadsheets.get(oldest_post_cell)
        
        try:
            rslt = rslt[0][0]
            if not rslt.startswith('t3_'):
                rslt = 't3_'+rslt
        except:
            rslt = ''
        rslt = rslt.strip()
        
        if rslt:
            oldest_post = rslt
            print('Google Sheets: oldest post to check', oldest_post)
        else:
            print('Google Sheets: no oldest post to check')
        
    except HttpError as err:
        print(err)
        input()

print()

oldest_post, lines = read_subreddit(
    subreddit='NatureofPredators',
    oldest_post=oldest_post,
    exclude_url=True,
    special_timelines=True,
    special_checks=True,
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
    print('Google Sheets: send', len(lines), 'new entry to pending.')
    
    start = len(spreadsheets.get(f"pending!A:H"))+2
    end = start+len(lines)
    
    spreadsheets.update(f"pending!{start}:{end}", lines)
    spreadsheets.update(oldest_post_cell, [[oldest_post]])
    
    print('Google Sheets: update completed')
    
except HttpError as err:
    print(err)
    input()

