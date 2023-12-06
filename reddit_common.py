import time, re
from collections import defaultdict

from common import requests, run_animation, read_json, write_json


exclude_items = [
    'preview',
    'user_reports', 'mod_reports', 'removal_reason', 'mod_reason_by', 'num_reports', 'report_reasons', 'removed_by', 'mod_note', 'mod_reason_title',
    'approved_at_utc', 'approved_by', 'can_mod_post',
    'media', 'media_embed', 'secure_media', 'secure_media_embed', 'media_metadata', 'gallery_data',
    
    'awarders', 'quarantine', 'likes', 'wls', 'pwls', 'clicked', 'visited',
    'is_crosspostable', 'num_crossposts', 'crosspost_parent', 'crosspost_parent_list',
    'subreddit_subscribers', 'stickied', 'parent_whitelist_status', 'whitelist_status', 'contest_mode',
    'is_robot_indexable', 'no_follow', 'view_count', 'suggested_sort', 'allow_live_comments',
    'link_flair_richtext', 'link_flair_template_id', 'hide_score', 'is_created_from_ads_ui',
    'is_original_content', 'is_reddit_media_domain', 'removed_by_category',
    
    'gilded', 'gildings', 'can_gild', 'treatment_tags', 'post_hint', 'thumbnail_height', 'thumbnail_width',
    'author_flair_background_color', 'author_flair_css_class', 'author_flair_richtext', 'author_flair_template_id',
    'author_flair_text', 'author_flair_text_color', 'author_flair_type', 'author_premium',
    'link_flair_background_color', 'link_flair_css_class', 'link_flair_text_color', 'link_flair_type',
    
    'replies',
]

def parse_exclude(post):
    for d in exclude_items:
        if d in post:
            del post[d]
    
    return post

def parse_body(post, keep_body):
    if isinstance(keep_body, str):
        keep_body = keep_body.lower()
    
    def del_md():
        return keep_body is False or keep_body and not (keep_body is True or 'md' in keep_body or 'markdown' in keep_body)
    
    def del_html():
        return keep_body is False or keep_body and not (keep_body is True or 'html' in keep_body)
    
    if 'body' in post:
        if del_md():
            del post['body']
        else:
            post['body'] = parse_rawhtml(post['body'])
    
    if 'selftext' in post:
        if del_md():
            del post['selftext']
        else:
            post['selftext'] = parse_rawhtml(post['selftext'])
    
    if 'body_html' in post:
        if del_html():
            del post['body_html']
        else:
            post['body_html'] = parse_rawhtml(post['body_html'])
    
    if 'selftext_html' in post:
        if del_html():
            del post['selftext_html']
        else:
            post['selftext_html'] = parse_rawhtml(post['selftext_html'])
        
    return post

awards_filter = ['name', 'description', 'award_type' ,'icon_url', 'static_icon_url']

def parse_awards(post):
    awards = []
    for d in post.get('all_awardings', []):
        awards.append({k:d[k] for k in awards_filter})
    
    if awards:
        post['all_awardings'] = awards
    
    return post


def replace_entitie(text):
    return text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&#39;', "'")

def parse_rawhtml(text):
    if not text:
        return text
    html = replace_entitie(text).replace('\n\n', '\n').replace('<br>', '<br/>').replace('<hr>', '<hr/>')
    html = html.removeprefix('<!-- SC_OFF -->').removesuffix('<!-- SC_ON -->')
    return re.sub(r'<a href="https://preview.redd.it/([^"]+)">https://preview.redd.it/\1</a>', r'<img src="https://preview.redd.it/\1"/>', html)
