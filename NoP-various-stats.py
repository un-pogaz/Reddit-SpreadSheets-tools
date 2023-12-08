from common import ini_spreadsheets, HttpError, write_lines


spreadsheets = ini_spreadsheets()

try:
    print('Google Sheets: retrive all authors')
    
    print()
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
    
    authors_common = sorted(authors_pending.intersection(authors_full))
    write_lines('authors_common.txt', authors_common)
    
    authors_difference = sorted(authors_pending.difference(authors_full))
    write_lines('authors_difference.txt', authors_difference)
    
    print('All authors has retrived.')
    map_count = {
        'Authors':authors_full,
        'Pending':authors_pending,
        'Common':authors_common,
        'Difference':authors_difference,
    }
    print(*[k+': '+str(len(v))+'.' for k,v in map_count.items()])
    
    print()
    table = spreadsheets.get('data!A:G')
    row_length = len(table[0])
    not_full_row = []
    for idx, r in enumerate(table, 1):
        if len(r) != row_length:
            not_full_row.append(idx)
    
    if not_full_row:
        print('Row not fulled:')
        for r in not_full_row:
            print(f' {r}:{r}')
    else:
        print('All rows are OK.')
    
except HttpError as err:
    print(err)
    input()
