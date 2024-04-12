from collections import defaultdict

from common import HttpError, init_spreadsheets, write_lines

spreadsheets = init_spreadsheets()

try:
    print('Google Sheets: retrieve data...')
    
    def write_authors_list(sheet_name) -> list[str]:
        data = spreadsheets.get(sheet_name+'!D:D')
        
        rslt = []
        for d in data[1:]:
            if not d:
                continue
            d = d[0]
            if d:
                rslt.extend([a.split('(')[0].strip() for a in d.split('&')])
        rslt = list(set(rslt))
        
        write_lines(f'authors_{sheet_name}.txt', sorted(rslt))
        
        return rslt
    
    authors_full = set(write_authors_list('data'))
    authors_pending = set(write_authors_list('pending'))
    table = spreadsheets.get('data')
    print()
    
    #############
    #parsing data
    
    authors_common = sorted(authors_pending.intersection(authors_full))
    write_lines('authors_common.txt', authors_common)
    
    authors_difference = sorted(authors_pending.difference(authors_full))
    write_lines('authors_difference.txt', authors_difference)
    
    map_count = {
        'Authors':authors_full,
        'Pending':authors_pending,
        'Common':authors_common,
        'Difference':authors_difference,
    }
    print(*[k+': '+str(len(v))+'.' for k,v in map_count.items()])
    
    print()
    print('Total data rows:', len(table))
    
    print()
    not_fulled_row = defaultdict(list)
    url_map = defaultdict(list)
    url_wrong = {}
    for idx, r in enumerate(table, 1):
        
        def cell_is_empty(cell, text):
            if len(r) < cell or not bool(r[cell-1]):
                not_fulled_row[idx].append(text)
        
        if r:
            cell_is_empty(1, 'date')
            cell_is_empty(2, 'timeline')
            cell_is_empty(3, 'title')
            cell_is_empty(4, 'authors')
            cell_is_empty(7, 'link')
        else:
            not_fulled_row[idx] = 'empty row'
        
        if len(r) > 6:
            url = r[6]
            url_map[url].append(idx)
            if 'new.reddit' in url or 'old.reddit' in url:
                url_wrong[idx] = url
    
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
    
    print()
    url_duplicate = {k:v for k,v in url_map.items() if len(v)>1}
    
    if url_duplicate:
        print('Duplicate url:')
    else:
        print('No duplicate url.')
    
    for url,lines in url_duplicate.items():
        print(url)
        for l in lines:
            print(f' {l}:{l}')
    
    print()
    
    if url_wrong:
        print('Wrong reddit url:')
    else:
        print('No wrong reddit url.')
    
    for l,url in url_wrong.items():
        print(f' {l}:{l} => {url}')
    
    print()

except HttpError as err:
    print(err)
    input()
