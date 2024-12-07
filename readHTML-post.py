import argparse
import os.path
import re
from collections import defaultdict

from common import get_url_data, read_text, write_lines

args = argparse.ArgumentParser(description='Get any urls for reddit post inside HTML files')
args.add_argument('-u', '--url', '--exclude-url', dest='exclude_url', action='store_true', help='Exclude where the url is already in the spreadsheets')
args.add_argument('file', type=str, nargs='+', help='File path of html containing urls to check')
args = args.parse_args()

if args.exclude_url:
    list_url_data = get_url_data()
else:
    list_url_data = []

dic_url_data = defaultdict(set)
for url in list_url_data:
    tbl = url.split('/')[:7]
    if 'r' in tbl and len(tbl) >= 7:
        dic_url_data[tbl[4]].add(tbl[6])

for file in args.file:
    if not os.path.exists(file):
        print("The path don't exist:", file)
        continue
    if os.path.isdir(file):
        print("The path is a folder:", file)
        continue
    
    print(f'Analyze "{file}"...')
    basename = os.path.splitext(file)[0]
    lines = []
    
    text = read_text(file, '')
    for m in re.finditer(r'href="https?://www.reddit.com/r/(\w+)/comments/(\w+)(?:/[^"]*)?"', text):
        subreddit = m.group(1)
        post_id = m.group(2)
        if subreddit in dic_url_data and post_id not in dic_url_data[subreddit]:
            lines.append(f'https://www.reddit.com/r/{subreddit}/comments/{post_id}/')
    
    lines = set(lines)
    write_lines(f'{basename}.txt', lines)
    print(f'Data extracted from "{file}".', 'Post found:', len(lines))
