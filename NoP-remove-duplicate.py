import os.path

from common import ARGS, APP, help_args, init_spreadsheets, HttpError


if help_args():
    print()
    print(os.path.basename(APP), '[option]')
    print()
    print("  -y --yes-duplicate     Don't ask to delete duplicate rows")
    exit()

spreadsheets = init_spreadsheets()

ask_duplicate = '-y' in ARGS or '--yes-duplicate' in ARGS

try:
    
    def list_url(sheet_name):
        data = spreadsheets.get(sheet_name+'!G:G')
        
        rslt = [d for d in data]
        for idx in range(len(rslt)):
            l = rslt[idx]
            if l:
                rslt[idx] = l[0]
            else:
                rslt[idx] = None
        return rslt
    
    print('Google Sheets: analyze data...')
    list_url_data = list_url('data')[1:]
    list_url_pending = list_url('pending')[3:]
    
    line_to_delete = []
    for idx, link in enumerate(list_url_pending, 4):
        if link and link in list_url_data:
            line_to_delete.append(idx)
    
    if len(line_to_delete) == 0:
        print('No update need.')
        exit()
    
    print()
    print('', len(line_to_delete), 'lines to delete.')
    if not ask_duplicate:
        print('Update of the sheets?')
        r = input('>')
        if not r or not r.lower()[0] == 'y':
            print('Aborted.')
            exit()
    
    print('Google Sheets: deleting lines...')
    spreadsheets.batchClear([f'pending!{l}:{l}' for l in line_to_delete])
    print('Google Sheets: update completed')
    
except HttpError as err:
    print(err)
    input()
