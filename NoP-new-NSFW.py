import os.path

from common import APP, ARGS, help_args, read_subreddit

if help_args():
    print()
    print(os.path.basename(APP), '[id_post]')
    print()
    print('  id_post (optional) id of the oldest post to check back')
    exit()

oldest_post = ARGS[0] if ARGS else None

if oldest_post:
    print()
    if not oldest_post.startswith('t3_'):
        oldest_post = 't3_'+oldest_post
    print('Oldest post to check', oldest_post)

print()

oldest_post, lines = read_subreddit(
    subreddit='NatureOfPredatorsNSFW',
    oldest_post=oldest_post,
    exclude_url=True,
)

with open('- NoP-NSFW new subreddit.csv', 'at', newline='\n', encoding='utf-8') as f:
    if lines:
        f.write('\n')
        f.write('\n'.join([e.to_string() for e in lines]))
        f.write('\n')
