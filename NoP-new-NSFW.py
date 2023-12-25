import os.path

from common import (
    ARGS, APP, ini_spreadsheets, HttpError,
    help_args, read_subreddit,
)


if help_args():
    print()
    print(os.path.basename(APP), '[id_post]')
    print()
    print('  id_post (optional) id of the oldest post to check back')
    exit()

spreadsheets = ini_spreadsheets()

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

oldest_post, lines = read_subreddit('NatureOfPredatorsNSFW', oldest_post, list_url_data)

with open('- NoP-NSFW new subreddit.csv', 'at', newline='\n', encoding='utf-8') as f:
    if lines:
        f.write('\n')
        f.write('\n'.join([e.to_string() for e in lines]))
        f.write('\n')
