import os.path
import random
import time

from common import (
    APP,
    ARGS,
    SUBREDDITS,
    get_filtered_post,
    help_args,
    parse_content,
    post_is_to_old,
    read_lines,
    requests,
    run_animation,
    write_lines,
)

args = []
for a in ARGS:
    a = a.strip('/')
    if a:
        args.append(a)

authors_file = 'authors_others.txt'
authors_count = 10
if not args or help_args():
    print()
    print(os.path.basename(APP), 'author [author ...]')
    print()
    print('ERROR: Need a author as parameter!')
    print(f"  pass - as first argument to exclude url's already present on the sheet")
    print(f'  pass ? to read {authors_count} lines from {authors_file}')
    print(f'  pass * to read all lines from {authors_file}')
    exit()

exclude = args[0] == '-'
if exclude:
    args = args[1:]
special = args[0] if args and args[0] in ['*','?'] else None

authors_lst = []
list_authors_empty = []
list_authors_error = []

if special == '?':
    authors_lst = read_lines(authors_file, [])
    args = authors_lst[:authors_count]

elif special == '*':
    args = read_lines(authors_file, [])

if special and not args:
    print(f'{authors_file} is empty.')
    exit()

args_length = len(args)
for args_idx in range(args_length):
    print()
    author = args[args_idx]
    
    all_post = []
    base_url = f'https://www.reddit.com/user/{author}/submitted/.json'
    
    # get all posts of author
    async def get_all_post():
        params = {'sort':'new', 'limit':100}
        count = 0
        loop = True
        
        while loop:
            tbl = requests.get(base_url, params=params, timeout=1000).json().get('data', {}).get('children', {})
            if tbl:
                count += len(tbl)
                run_animation.extra = str(count)
                loop = True
                
                for r in tbl:
                    r = r['data']
                    if post_is_to_old(r) and not r['pinned']:
                        loop = False
                    if r['subreddit'] in SUBREDDITS:
                        parse_content(r)
                        all_post.append(r)
                    params['after'] = r['name']
            else:
                loop = False
            time.sleep(1)
    
    run_animation(get_all_post, f'Loading Reddit post for {author}'+ (f' [{args_idx+1}/{args_length}]' if args_length > 1 else '') )
    
    lines = get_filtered_post(
        source_data=all_post,
        exclude_url=exclude,
    )
    lines = [e.to_string() for e in lines]
    
    # write posts
    if special == '*':
        subdir = 'multi-authors'
    else:
        subdir = '.'
    os.makedirs(subdir, exist_ok=True)
    
    if lines or not special:
        write_lines(os.path.join(subdir, f'{author}.csv'), lines)
    else:
        if not all_post:
            lst = list_authors_error
            filename = f'! ERROR author.txt'
        else:
            lst = list_authors_empty
            filename = f'- empty author.txt'
        lst.append(author)
        write_lines(os.path.join(subdir, filename), lst)
    
    msg = '' if all_post else '!!ERROR!!'
    print(f'Data extracted u/{author}.', 'Post found:', len(lines), msg)
    
    if special == '*':
        i = random.randint(8,22)
        msg = f'Waiting {i} seconds (to appease reddit)...'
        print(msg, end='\r')
        time.sleep(i+round(random.random(),1))
        print(' '*len(msg), end='\r')

if special == '?':
    write_lines(authors_file, authors_lst[authors_count:])
