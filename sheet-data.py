import argparse
import random
import time

from common import (
    SUBREDDITS,
    get_filtered_post,
    parse_content,
    post_is_to_old,
    requests,
    run_animation,
    write_lines,
)

args = argparse.ArgumentParser(description='Retrive the data from authors')
args.add_argument('-u', '--url', '--exclude-url', dest='exclude_url', action='store_true', help='Exclude where the url post is already in the spreadsheets')
args.add_argument('author', type=str, nargs='+', help='Authors to retrive')
args = args.parse_args()

authors_lst = []
list_authors_empty = []
list_authors_error = []

args_length = len(args.author)
for args_idx in range(args_length):
    print()
    author = args.author[args_idx]
    
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
        exclude_url=args.exclude_url,
    )
    lines = [e.to_string() for e in lines]
    
    if lines:
        write_lines(f'{author}.csv', lines)
    else:
        if not all_post:
            lst = list_authors_error
            filename = f'! ERROR author.txt'
        else:
            lst = list_authors_empty
            filename = f'- empty author.txt'
        lst.append(author)
        write_lines(filename, lst)
    
    msg = '' if all_post else '!!ERROR!!'
    print(f'Data extracted u/{author}.', 'Post found:', len(lines), msg)
    
    if args_length > 10:
        i = random.randint(8,22)
        msg = f'Waiting {i} seconds (to appease reddit)...'
        print(msg, end='\r')
        time.sleep(i+round(random.random(),1))
        print(' '*len(msg), end='\r')
