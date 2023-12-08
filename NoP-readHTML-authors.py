import os.path, re

from common import (
    ARGS, APP, help_args,
    read_lines, read_text, write_lines,
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

filename = 'authors_others.txt'
total_lines = set(read_lines(filename))
authors_data_lower = [l.lower() for l in read_lines('authors_data.txt')]

for file in args:
    print(f'Analyze "{file}"...')
    lines = []
    
    text = read_text(file, '')
    for m in re.finditer(r'href="(?:[^"]*/)?(?:u|user)/([\w\-]+)/?[^"]*"', text):
        lines.append(m.group(1))
    
    lines = set(lines)
    total_lines.update(lines)
    
    print(f'Data extracted from "{file}".', 'Authors found:', len(lines))

rslt = []
for l in total_lines:
    if l.lower() not in authors_data_lower:
        rslt.append(l)

write_lines(filename, rslt)
print('Authors not in sheet:', len(rslt))
