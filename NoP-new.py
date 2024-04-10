import argparse

from common import HttpError, init_spreadsheets, read_subreddit

args = argparse.ArgumentParser(description='Retrive the data from r/NatureofPredators, and push it to the spreadsheets')
args.add_argument('-u', '--url', '--dont-exclude-url', dest='exclude_url', action='store_false', help="Don't exclude where the url post is already in the spreadsheets")
grps = args.add_mutually_exclusive_group()
grps.add_argument('--csv', action='store_true', default=None, help='Output into a CSV file')
grps.add_argument('--csv-file', type=str, dest='csv', help='Path of the CSV file to output')
args.add_argument('oldest_post_id', type=str, nargs='?', help='id of the oldest post to check. If empty, go to the limit of the reddit API (1000 posts).')
args = args.parse_args()

####################
# oldest_post

def get_oldest_post() -> str:
    spreadsheets = init_spreadsheets()
    
    print('Google Sheets: retrieve the oldest post to check...')
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
    else:
        print('ERROR: No last-post line found')


if args.oldest_post_id:
    args.oldest_post_id = args.oldest_post_id.strip()
    if not args.oldest_post_id.startswith('t3_'):
        args.oldest_post_id = 't3_'+args.oldest_post_id
    print('Oldest post to check', args.oldest_post_id)
else:
    rslt = get_oldest_post()
    
    if rslt:
        if not rslt.startswith('t3_'):
            rslt = 't3_'+rslt
        args.oldest_post_id = rslt
        print('Google Sheets: oldest post to check', args.oldest_post_id)
    else:
        print('Google Sheets: no oldest post to check')

print()

oldest_post, lines = read_subreddit(
    subreddit='NatureofPredators',
    oldest_post=args.oldest_post_id,
    exclude_url=args.exclude_url,
)

if args.csv:
    if args.csv is True:
        args.csv = '- NoP new subreddit.csv'
    
    with open(args.csv, 'at', newline='\n', encoding='utf-8') as f:
        if lines:
            f.write('\n')
            f.write('\n'.join([e.to_string() for e in lines]))
            f.write('\n')
    exit()

if not lines:
    exit()

lines = [e.to_list() for e in lines]

####################
# update Google Sheets

try:
    print()
    spreadsheets = init_spreadsheets()
    print('Google Sheets: send', len(lines), 'new entry to pending.')
    
    start = len(spreadsheets.get('pending'))+2
    end = start+len(lines)
    
    spreadsheets.update(f"pending!{start}:{end}", lines)
    set_oldest_post(oldest_post)
    
    print('Google Sheets: update completed')
    
except HttpError as err:
    print(err)
    input()
