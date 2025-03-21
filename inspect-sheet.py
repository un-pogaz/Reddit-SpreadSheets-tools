import argparse
from collections import defaultdict
from datetime import datetime, timedelta

from common import init_spreadsheets, write_lines

def check_positive(value):
    try:
        value = int(value)
    except:
        raise argparse.ArgumentTypeError(f'invalid positive int value: {repr(value)}')
    if value < 0:
        raise argparse.ArgumentTypeError(f'invalid positive int value: {value}')
    return value

args = argparse.ArgumentParser(description='Inspect the spreadsheets to look up invalide data')
args.add_argument('--write-authors', action='store_true', help='Write the authors files')
args.add_argument(
    '--entry-older', nargs='?', type=check_positive, metavar='INT', default=False,
    help='Analyze if post "On going" are to old (in month). If no parameter, default is 6 month.'
)
args = args.parse_args()

spreadsheets = init_spreadsheets()

print('Google Sheets: retrieve data...')

def write_authors_list(sheet_name) -> set[str]:
    data = spreadsheets.get(sheet_name+'!D:D')
    
    rslt = []
    for d in data[1:]:
        if not d:
            continue
        d = d[0]
        if d:
            rslt.extend([a.split('(')[0].strip() for a in d.split('&')])
    rslt = set(rslt)
    
    if args.write_authors:
        write_lines(f'authors_{sheet_name}.txt', sorted(rslt))
    
    return rslt

authors_full = write_authors_list('data')
authors_various = write_authors_list('various')
table = spreadsheets.get('data')

print()
print('Total data rows:', len(table))

authors_common = sorted(authors_various.intersection(authors_full))
if args.write_authors:
    write_lines('authors_common.txt', authors_common)

authors_difference = sorted(authors_various.difference(authors_full))
if args.write_authors:
    write_lines('authors_difference.txt', authors_difference)

map_count = {
    'Authors':authors_full,
    'Various':authors_various,
    'Common':authors_common,
    'Difference':authors_difference,
}
print()
print(*[k+': '+str(len(v))+'.' for k,v in map_count.items()])


#############
#parsing data
not_fulled_row = defaultdict(list)
url_map = defaultdict(list)
url_wrong = {}
url_params = {}
url_shared = {}
authors_date = {}
for idx, r in enumerate(table, 1):
    if idx <= 2:
        continue
    lr = len(r)
    
    def cell_is_empty(cell, text):
        if lr < cell or not bool(r[cell-1]):
            not_fulled_row[idx].append(text)
    
    if r:
        cell_is_empty(1, 'date')
        cell_is_empty(2, 'timeline')
        cell_is_empty(3, 'title')
        cell_is_empty(4, 'authors')
        cell_is_empty(7, 'link')
    else:
        not_fulled_row[idx] = 'empty row'
    
    if lr > 6:
        url = r[6]
        url_map[url].append(idx)
        if '.reddit' in url:
            if 'www.reddit' not in url:
                url_wrong[idx] = url
            if '/s/' in url:
                url_shared[idx] = url
        if '?' in url:
            url_params[idx] = url
    
    if args.entry_older and lr > 5 and r[0] and r[5] == 'On going':
        date = datetime.strptime(r[0], '%m/%d/%Y')
        for a in r[3].split('&'):
            a = a.strip()
            if a not in authors_date or authors_date[a] < date:
                 authors_date[a] = date

url_duplicate = {k:v for k,v in url_map.items() if len(v)>1}

print()
if not_fulled_row:
    print('Row not fulled:')
else:
    print('All rows are fulled.')

for l in sorted(not_fulled_row.keys()):
    if isinstance(not_fulled_row[l], str):
        msg = not_fulled_row[l]
    else:
        msg = 'missing: '+ ', '.join(not_fulled_row[l])
    print(f' {l}:{l} <{msg}>')

# print url errors
has_url_errors = bool(url_duplicate or url_wrong or url_params or url_shared)

def uprint(*args, **kargs):
    print()
    print(*args, **kargs)

if url_duplicate:
    uprint('Duplicate url:')
elif has_url_errors:
    uprint('No duplicate url.')

for url,lines in url_duplicate.items():
    print(url)
    for l in lines:
        print(f' {l}:{l}')

if url_wrong:
    uprint('Wrong reddit url:')
elif has_url_errors:
    uprint('No wrong reddit url.')

for l,url in url_wrong.items():
    print(f' {l}:{l} => {url}')

if url_params:
    uprint('Parameter in reddit url:')

for l,url in url_params.items():
    print(f' {l}:{l} => {url}')

if url_shared:
    uprint('Shared reddit url:')

for l,url in url_shared.items():
    print(f' {l}:{l} => {url}')

if not has_url_errors:
    uprint('All url are valid.')

if args.entry_older:
    print()
    
    old = datetime.now() - timedelta(days=30*args.entry_older)
    authors_date = {k:v for k,v in authors_date.items() if v < old}
    
    if authors_date:
        print(f'Entry older that {args.entry_older} month:')
    else:
        print(f'No entry older that {args.entry_older} month.')
        
    for k,v in sorted(authors_date.items(), key=lambda x:x[1]):
        print(f' {k} [last post: {v:%Y/%m/%d}]')
