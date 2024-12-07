import argparse

from common import CONFIG, HttpError, init_spreadsheets, read_subreddit

args = argparse.ArgumentParser(description='Retrive the data from a subreddit, and push it to the spreadsheets')
args.add_argument('-a', '--all', '--dont-exclude-url', dest='exclude_url', action='store_false', help="Retrive all entry, don't exclude where the url of the post is already in the spreadsheets")
args.add_argument('-csv', '--csv', type=str, nargs='?', default=False, help='Output into a CSV file')
args.add_argument('-id', '--id', '--oldest-post-id', dest='oldest_post_id', type=str, help='id of the oldest post to check. If not specified, used the id stored on the spreadsheets.')
args.add_argument('-c', '--config', type=str, default='main', help='Use the specified setting in the config file. If not specified, use "main"')
args.add_argument('--no-emtpy-row', '--no-pending-emtpy-row', dest='no_emtpy_row', action='store_false', help="Don't add emtpy row at the end of the 'data' sheet")
args.add_argument('--no-update-filtre', '--no-update-filtre-view', dest='no_update_filtre', action='store_false', help="Don't update the range of the filtre views")
args = args.parse_args()

settings = {}
for k,v in CONFIG['settings'].items():
    settings[k] = k
    for a in v.get('alias', []):
        settings[a] = k

if args.config not in settings:
    print(f'The setting "{args.config}" is not in the config file.')
    exit()

config = CONFIG['settings'][settings[args.config]]
last_post_name = 'last-post-' + settings[args.config]

def parse_post_id(post_id: str):
    post_id = post_id.strip()
    if not post_id.startswith('t3_'):
        post_id = 't3_'+post_id
    return post_id

def get_oldest_post_id() -> str:
    spreadsheets = init_spreadsheets()
    
    print('Google Sheets: retrieve the oldest post to check...')
    for r in spreadsheets.get('script-user-data'):
        if not r or r[0] != last_post_name:
            continue
        for d in r[1:]:
            if d:
                return parse_post_id(d)
    return None

def set_oldest_post_id(oldest_post: str):
    spreadsheets = init_spreadsheets()
    
    oldest_post_row = None
    oldest_post_idx_row = None
    oldest_post_idx_column = None
    
    for idx_r,r in enumerate(spreadsheets.get('script-user-data'), 1):
        if not r or r[0] != last_post_name:
            continue
        for idx_c,d in enumerate(r[1:], 1):
            if d:
                oldest_post_row = r
                oldest_post_idx_row = idx_r
                oldest_post_idx_column = idx_c
                break
    
    if oldest_post_row:
        oldest_post_row[oldest_post_idx_column] = parse_post_id(oldest_post or '')
        spreadsheets.update(f'script-user-data!{oldest_post_idx_row}:{oldest_post_idx_row}', [oldest_post_row])
    else:
        print(f'ERROR: No {last_post_name} line found')

if args.oldest_post_id:
    args.oldest_post_id = parse_post_id(args.oldest_post_id)
    print('Oldest post to check', args.oldest_post_id)
else:
    rslt = get_oldest_post_id()
    
    if rslt:
        args.oldest_post_id = rslt
        print('Google Sheets: oldest post to check', args.oldest_post_id)
    else:
        print('Google Sheets: no oldest post to check found')
print()


lines = read_subreddit(
    subreddit=config['name'],
    subreddit_is_author=config['is_author'],
    oldest_post=args.oldest_post_id,
    exclude_url=args.exclude_url,
    **config['kargs'],
)

if not lines:
    exit()

if args.csv is None:
    args.csv = '- new subreddit.csv'
if args.csv:
    with open(args.csv, 'at', newline='\n', encoding='utf-8') as f:
        f.write('\n')
        f.write('\n'.join([e.to_string() for e in lines]))
        f.write('\n')
    exit()

try:
    print()
    spreadsheets = init_spreadsheets()
    print('Google Sheets: send {} new entry to pending.'.format(len(lines)))
    
    start = len(spreadsheets.get('pending'))+1
    end = start+len(lines)+1
    
    spreadsheets.update(f"pending!{start}:{end}", [e.to_list() for e in lines]+[['']])
    
    set_oldest_post_id(lines[-1].post_id)
    print('Google Sheets: update pending entry completed')
    print()
    
    if not args.spacepaladin and args.no_emtpy_row:
        # add empty rows at the end of 'data'
        # corresponding to the number of rows into 'pending'
        print('Google Sheets: append pending empty row to data')
        data_start = len(spreadsheets.get('data!A:A'))+1
        data_end = data_start+end
        spreadsheets.update(f"data!{data_start}:{data_end}", [[''] for _ in range(end)])
        print('Google Sheets: pending empty row completed')
        print()
    
    if not args.spacepaladin and args.no_update_filtre:
        # update range of filter views
        print('Google Sheets: update range of filter views')
        requests_filter_views = []
        for sheet in spreadsheets.getSpreadsheetsMetadata().get('sheets', []):
            sheetId = sheet['properties']['sheetId']
            rowCount = sheet['properties']['gridProperties']['rowCount']
            columnCount = sheet['properties']['gridProperties']['columnCount']
            for filter_views in sheet.get('filterViews', []):
                requests_filter_views.append(
                    {"updateFilterView": {
                        "filter": {
                            "filterViewId": filter_views['filterViewId'],
                            "range": {
                                "sheetId": sheetId,
                                "startRowIndex": 0,
                                "endRowIndex": rowCount,
                                "startColumnIndex": 0,
                                "endColumnIndex": columnCount,
                            }
                        },
                        "fields": '*'}
                    },
                )
        
        spreadsheets.batchUpdateSpreadsheets(requests_filter_views)
        print('Google Sheets: filter views range updated')
        print()
    
except HttpError as err:
    print(err)
    input()
