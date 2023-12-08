import os.path, time, random
from collections import defaultdict

from common import (
    ARGS, APP, DOMAIN_EXCLUDE, DOMAIN_STORY_HOST, SUBREDDITS,
    help_args, requests, run_animation, write_lines, read_lines,
    parse_exclude, parse_body, parse_awards, PostEntry,
)


args = []
for a in ARGS:
    a = a.strip('/')
    if a:
        args.append(a)

if not args or help_args():
    print(os.path.basename(APP), 'file [file ...]')
    print()
    print('ERROR: Need a author as parameter!')
    exit()



for file in args:
    print()
    basename = os.path.splitext(file)[0]
    lines = []
    all_post = defaultdict(dict)
    
    lst_invalide_link = set()
    
    all_link = set(read_lines(file, []))
    lenght = len(all_link)
    
    # get all posts of author
    async def read_all_link():
        for idx, base_url in enumerate(all_link, 1):
            i = random.randint(8,22)
            run_animation.extra = f'{idx}/{lenght} (waiting {i} seconds to appease reddit)'
            
            if 'reddit.com' not in base_url:
                continue
            
            for suffix in ['/', '.json']:
                if not base_url.endswith(suffix):
                    base_url += suffix
            
            reponse = requests.get(base_url, timeout=1000).json()
            if isinstance(reponse, list) and reponse:
                r = reponse[0]['data']['children'][0]['data']
                
                parse_exclude(r)
                parse_body(r, 'md')
                parse_awards(r)
                
                r['permalink'] = 'https://www.reddit.com' + r['permalink']
                
                if r['subreddit'] in SUBREDDITS:
                    all_post[r['subreddit']][r['name']] = {k:r[k] for k in sorted(r.keys())}
            else:
                lst_invalide_link.add(base_url)
                write_lines(f'{basename}-invalide-link.txt', sorted(lst_invalide_link))
            
            time.sleep(i+round(random.random(),1))
    
    run_animation(read_all_link, f'Reading links in "{file}"')
    
    # filtre posts
    for subreddit in SUBREDDITS:
        self_domain = f'self.{subreddit}'
        for item in reversed(all_post.get(subreddit, {}).values()):
            if item.get('created_utc', 0) < 1649689768:
                continue
            
            if subreddit == 'NatureofPredators' and (item['link_flair_text'] or '').lower() not in ['', 'fanfic', 'nsfw']:
                continue
            
            link_redirect = ''
            domain = item.get('domain', self_domain)
            if domain in DOMAIN_STORY_HOST:
                link_redirect = item['url_overridden_by_dest']
            elif domain in DOMAIN_EXCLUDE:
                if item.get('selftext'):
                    pass
                else:
                    continue
            elif domain != self_domain:
                continue
            
            lines.append(PostEntry(item))
    
    # write posts
    lines.sort(key=lambda x:x.created)
    lines = [e.to_string() for e in lines]
    
    write_lines(f'{basename}.csv', lines)
    
    print(f'Data extracted from "{file}".', 'Post found:', len(lines),'Invalide link:',len(lst_invalide_link))
