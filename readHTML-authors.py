import argparse
import os.path
import re

from common import read_text, write_lines

args = argparse.ArgumentParser(description='Get the authors inside HTML files')
args.add_argument('file', type=str, nargs='+', help='File path of HTML to analyze')
args = args.parse_args()

for file in args.file:
    if not os.path.exists(file):
        print("The path don't exist:", file)
        continue
    if os.path.isdir(file):
        print("The path is a folder:", file)
        continue
    
    print(f'Analyze "{file}"...')
    basename = os.path.splitext(file)[0]
    lines = []
    
    text = read_text(file, '')
    for m in re.finditer(r'href="(?:[^"]*/)?(?:u|user)/([\w\-]+)/?[^"]*"', text):
        lines.append(m.group(1))
    
    lines = set(lines)
    
    write_lines(f'{basename}.txt', lines)
    print(f'Data extracted from "{file}".', 'Authors found:', len(lines))
