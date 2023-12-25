import os.path, re
from collections import defaultdict

from common import ARGS, APP, help_args, get_url_data, read_text, write_lines


args = []
for a in ARGS:
    a = a.strip('/')
    if a:
        args.append(a)

if not args or help_args():
    print()
    print(os.path.basename(APP), 'file [file ...]')
    print()
    print('ERROR: Need a file as parameter!')
    exit()

list_url_data = get_url_data()

dic_url_data = defaultdict(set)
for url in list_url_data:
    tbl = url.split('/')[:7]
    if 'r' in tbl and len(tbl) >= 7:
        dic_url_data[tbl[4]].add(tbl[6])

total_line = set()
for file in args:
    print(f'Analyze "{file}"...')
    lines = []
    
    text = read_text(file, '')
    for m in re.finditer(r'href="https?://www.reddit.com/r/(\w+)/comments/(\w+)(?:/[^"]*)?"', text):
        subreddit = m.group(1)
        post_id = m.group(2)
        if subreddit in dic_url_data and post_id not in dic_url_data[subreddit]:
            lines.append(f'https://www.reddit.com/r/{subreddit}/comments/{post_id}/')
    
    lines = set(lines)
    total_line.update(lines)
    print(f'Data extracted from "{file}".', 'Post found:', len(lines))


write_lines('search-HTML-post.txt', sorted(total_line))
print('Links not in sheet:', len(total_line))
