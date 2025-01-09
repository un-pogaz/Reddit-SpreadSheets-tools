import argparse

from common import get_config_settings, read_subreddit, parse_post_id, update_local_user_data, get_local_user_data

args = argparse.ArgumentParser(description='Retrive the data from a subreddit, and push it to the spreadsheets')
args.add_argument('-a', '--all', '--dont-exclude-url', dest='exclude_url', action='store_false', help="Retrive all entry, don't exclude where the url of the post is already in the spreadsheets")
args.add_argument('-csv', '--csv', type=str, nargs='?', default=False, help='Output into a CSV file')
args.add_argument('-id', '--id', '--oldest-post-id', dest='oldest_post_id', type=str, help='id of the oldest post to check. If not specified, used the id stored on the spreadsheets.')
args.add_argument('-c', '--config', type=str, default='main', help='Use the specified setting in the config file. If not specified, use "main"')
args = args.parse_args()


config, last_post_name = get_config_settings(args.config)
if not config:
    print(f'The setting "{args.config}" is not in the config file.')
    exit()


def get_oldest_post_id() -> str:
    try:
        return parse_post_id(get_local_user_data(last_post_name))
    except Exception as err:
        print('ERROR: get_oldest_post_id():', err)
        return None

def set_oldest_post_id(oldest_post: str):
    try:
        update_local_user_data(last_post_name, oldest_post)
    except Exception as err:
        print('ERROR: set_oldest_post_id():', err)

if args.oldest_post_id:
    args.oldest_post_id = parse_post_id(args.oldest_post_id)
    print('Oldest post to check', args.oldest_post_id)
else:
    rslt = get_oldest_post_id()
    
    if rslt:
        args.oldest_post_id = rslt
        print('Oldest post to check', args.oldest_post_id)
    else:
        print('No oldest post to check found')
print()

all_csv_path = 'all-subreddit.csv'
if args.exclude_url:
    try:
        with open(all_csv_path, 'rt', newline='\n', encoding='utf-8') as f:
            data = f.read()
        data = [l.split('\t') for l in data.splitlines(False) if len()]
        args.exclude_url = [l[6] for l in data if len(l)>=6]
    except:
        args.exclude_url = []

kargs = dict(
    allow_poll=True,
    allow_empty_text=True,
    
    subreddit_and_flairs={},
    subreddit_flair_statue={},
    subreddit_adult=[],
    
    title_timelines={},
    chapter_inside_post=[],
    check_links_map={},
    check_links_search={},
    domain_story_host=[],
    additional_regex=[],
    chapter_regex=[],
    status_regex=[],
    timeline_key_words={},
    co_authors={},
    comics=[],
)
lines = read_subreddit(
    subreddit=config['name'],
    subreddit_is_user=config['is_user'],
    oldest_post=args.oldest_post_id,
    exclude_url=args.exclude_url,
    max_old_post=get_local_user_data('max-old-post'),
    
    **(kargs | config['kargs']),
)

if not lines:
    exit()

if args.csv is None:
    args.csv = '- new subreddit.csv'
if args.csv is False:
    args.csv = all_csv_path

with open(args.csv, 'at', newline='\n', encoding='utf-8') as f:
    f.write('\n'.join([e.to_string() for e in lines]))
    f.write('\n')

set_oldest_post_id(lines[-1].post_id)
