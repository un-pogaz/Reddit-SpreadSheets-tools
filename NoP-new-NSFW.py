import argparse

from common import HttpError, init_spreadsheets, read_subreddit

args = argparse.ArgumentParser(description='Retrive the data from r/NatureOfPredatorsNSFW')
args.add_argument('-u', '--url', '--dont-exclude-url', dest='exclude_url', action='store_false', help="Don't exclude exclude where the url post is already in the spreadsheets")
args.add_argument('--csv-file', type=str, nargs='?', default='- NoP-NSFW new subreddit.csv', help='Path of the CSV file to output')
args.add_argument('oldest_post_id', type=str, nargs='?', help='id of the oldest post to check. If empty, go to the limit of the reddit API (1000 posts).')
args = args.parse_args()

oldest_post, lines = read_subreddit(
    subreddit='NatureOfPredatorsNSFW',
    oldest_post=args.oldest_post_id,
    exclude_url=args.exclude_url,
)

with open(args.csv_file, 'at', newline='\n', encoding='utf-8') as f:
    if lines:
        f.write('\n')
        f.write('\n'.join([e.to_string() for e in lines]))
        f.write('\n')
