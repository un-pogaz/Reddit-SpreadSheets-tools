import argparse
import random
import time

from common import (
    read_subreddit,
    write_lines,
)

args = argparse.ArgumentParser(description='Retrive the data from authors')
args.add_argument('-u', '--url', '--exclude-url', dest='exclude_url', action='store_true', help='Exclude where the url post is already in the spreadsheets')
args.add_argument('author', type=str, nargs='+', help='Authors to retrive')
args = args.parse_args()

authors_lst = []
list_authors_error = []

args_length = len(args.author)
for args_idx in range(args_length):
    print()
    author = args.author[args_idx]
    
    lines = read_subreddit(
        subreddit=author,
        oldest_post=None,
        subreddit_is_author=True,
        additional_loading_message=(f' [{args_idx+1}/{args_length}]' if args_length > 1 else ''),
        exclude_url=args.exclude_url,
    )
    
    if lines:
        write_lines(f'{author}.csv', [e.to_string() for e in lines])
    else:
        list_authors_error.append(author)
        write_lines('- empty-error authors.txt', list_authors_error)
    
    
    if args_length > 10:
        i = random.randint(8,22)
        msg = f'Waiting {i} seconds (to appease reddit)...'
        print(msg, end='\r')
        time.sleep(i+round(random.random(),1))
        print(' '*len(msg), end='\r')
