import os.path, time, random

from common import (
    ARGS, APP, help_args, requests, run_animation,
    write_lines, read_lines, get_filtered_post, parse_content,
)


args = []
for a in ARGS:
    a = a.strip('/')
    if a:
        args.append(a)

if not args or help_args():
    print(os.path.basename(APP), 'file [file ...]')
    print()
    print('ERROR: Need a file as parameter!')
    exit()



for file in args:
    print()
    basename = os.path.splitext(file)[0]
    lines = []
    all_post = []
    
    lst_invalide_link = set()
    
    all_link = set(read_lines(file, []))
    lenght = len(all_link)
    
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
                parse_content(r)
                all_post.append(r)
            else:
                lst_invalide_link.add(base_url)
                write_lines(f'{basename}-invalide-link.txt', sorted(lst_invalide_link))
            
            time.sleep(i+round(random.random(),1))
    
    run_animation(read_all_link, f'Reading links in "{file}"')
    
    lines = [e.to_string() for e in get_filtered_post(source_data=all_post, exclude_url=False, special_timelines=True)]
    
    write_lines(f'{basename}.csv', lines)
    
    print(f'Data extracted from "{file}".', 'Post found:', len(lines),'Invalide link:',len(lst_invalide_link))
