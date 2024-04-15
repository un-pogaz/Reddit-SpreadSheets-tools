import argparse

from common import append_new_entrys, get_oldest_post_id, parse_post_id, read_subreddit

args = argparse.ArgumentParser(description='Retrive the data from r/NatureOfPredatorsNSFW, and push it to the spreadsheets')
args.add_argument('-u', '--url', '--dont-exclude-url', dest='exclude_url', action='store_false', help="Don't exclude where the url post is already in the spreadsheets")
grps = args.add_mutually_exclusive_group()
grps.add_argument('--csv', action='store_true', default=None, help='Output into a CSV file')
grps.add_argument('--csv-file', type=str, dest='csv', help='Path of the CSV file to output')
args.add_argument('oldest_post_id', type=str, nargs='?', help='id of the oldest post to check. If empty, go to the limit of the reddit API (1000 posts).')
args = args.parse_args()

if args.oldest_post_id:
    args.oldest_post_id = parse_post_id(args.oldest_post_id)
    print('Oldest post to check', args.oldest_post_id)
else:
    rslt = get_oldest_post_id(nsfw=True)
    
    if rslt:
        args.oldest_post_id = rslt
        print('Google Sheets: oldest post to check', args.oldest_post_id)
    else:
        print('Google Sheets: no oldest post to check found')
print()

oldest_post, lines = read_subreddit(
    subreddit='NatureOfPredatorsNSFW',
    oldest_post=args.oldest_post_id,
    exclude_url=args.exclude_url,
)

if args.csv:
    if args.csv is True:
        args.csv = '- NoP-NSFW new subreddit.csv'
    
    with open(args.csv, 'at', newline='\n', encoding='utf-8') as f:
        if lines:
            f.write('\n')
            f.write('\n'.join([e.to_string() for e in lines]))
            f.write('\n')
    exit()

if not lines:
    exit()

append_new_entrys(
    new_posts=lines,
    oldest_post=oldest_post,
    nsfw=True,
)
