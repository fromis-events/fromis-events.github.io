import csv
from io import StringIO

import pandas as pd

import json
import os
import time
import re
import random

import filedate
import requests
from datetime import datetime

weird_types = set()


def get_img_ext(url: str):
    return url.rsplit('?')[0].rsplit('.')[-1]


def get_video_ext(url: str):
    return url.rsplit('?')[0].rsplit('.')[-1]


def get_video_id(url: str):
    clean_url = url.removeprefix('https://video.twimg.com/amplify_video/').removeprefix('https://video.twimg.com/ext_tw_video/')
    return clean_url.split('/')[0]


def get_tags(p):
    pattern = r'(#[\w\uAC00-\uD7A3]+)'
    full_text = p.full_text # get_legacy(data)['full_text']
    matches = re.findall(pattern, full_text)
    return [m for m in matches if not m.removeprefix('#').isdigit()]


def write_all_tags(posts_by_event, path):
    print('write all tags?')
    out = set()
    for e, ps in posts_by_event.items():
        for p in ps:
            for t in get_tags(p):
                out.add(t.removeprefix('#'))

    with open(path, 'w', encoding='utf-8') as tag_file:
        tag_file.write('''# Tags

[TAGS]
''')
        tag_file.write('\n'.join(out))


def get_full_text(data):
    full_text = get_legacy(data)['full_text']

    if media := get_media(data):
        for m in media:
            # print('searching for ', m['url'])
            full_text = full_text.replace(m['url'], '')

    if urls := get_urls(data):
        for url in urls:
            full_text = full_text.replace(url['url'], f'[{url['expanded_url']}]({url['expanded_url']})')

    # pattern = r'(#[\w\uAC00-\uD7A3]+)'
    pattern = r'(?<![\w/])#([\w\uAC00-\uD7A3]+)'
    # full_text = re.sub(pattern, r'[\1](tags/\1)', full_text)
    full_text = re.sub(pattern, r'[\#\1](https://x.com/hashtag/\1)', full_text)

    at_pattern = r'(?<![\w/])(@[\w\uAC00-\uD7A3]+)'
    full_text = re.sub(at_pattern, r'[\1](https://x.com/\1)', full_text)

    # full_text.replace('#', '\\#')

    return full_text.replace('\n', '<br>\n').strip()


def get_media(data):
    if result := get_legacy(data)['entities'].get('media'):
        return result

    return []


def get_urls(data):
    out_urls = get_legacy(data)['entities'].get('urls')
    if out_urls:
        return out_urls
    elif url := get_legacy(data)['entities'].get('url'):
        return url.get('urls')

    return None


def get_result(data):
    # if is_retweet(data):
    #     return data['content']['itemContent']['tweet_results']['result']['legacy']['retweeted_status_result']['result']

    tweet_results = data['content']['itemContent']['tweet_results']
    # if 'result' in tweet_results:
    return tweet_results['result']
    # return tweet_results['core']['user_results']['result']

    # return data['content']['itemContent']['tweet_results']['result']


def get_post_id(data):
    return data['entryId'].split('-')[1]


def is_retweet(data):
    result = data['content']['itemContent']['tweet_results']['result']
    if tweet := result.get('tweet'):
        return 'retweeted_status_result' in tweet['legacy']
    else:
        return 'retweeted_status_result' in result['legacy']


def get_legacy(data):
    result = get_result(data)
    if tweet := result.get('tweet'):
        return tweet['legacy']
    else:
        return result['legacy']

    # return get_result(data)['legacy']


def get_datetime(data):
    created_at = get_legacy(data)['created_at']
    date_format = "%a %b %d %H:%M:%S %z %Y"
    return datetime.strptime(created_at, date_format)

def get_core(data):
    result = get_result(data)
    if core := result.get('core'):
        return core

    return result['tweet']['core']

def get_author(data):
    return get_core(data)['user_results']['result']['core']['screen_name']

def get_video_url(media):
    out_url = None
    if video_info := media.get('video_info'):
        variants = video_info['variants']
        largest = 0
        for v in variants:
            if v['content_type'] == 'video/mp4':
                bitrate = int(v['bitrate'])
                if bitrate > largest:
                    largest = bitrate
                    out_url = v['url']
    return out_url

def is_tweet(data):
    if data['content']['__typename'] != 'TimelineTimelineItem':
        return False

    if len(data['content']['itemContent']['tweet_results']) == 0:
        return False

    return True

class Post:
    def __init__(self, data):
        self.data = data
        self.full_text = get_full_text(data)
        self.media = get_media(data)
        self.post_id = get_post_id(data)
        self.date = get_datetime(data)
        self.event_date = None
        self.author = get_author(data)
        self.link = f'https://x.com/{self.author}/status/{self.post_id}'

    def get_images(self):
        if self.media:
            return [m for m in self.media if m['type'] == 'photo']
        return []

    def get_videos(self):
        if self.media:
            return [m for m in self.media if m['type'] == 'video']  # return [result for m in self.media if (result := get_video_url(m)) is not None]
        return []

    def has_media(self):
        return len(self.get_images()) > 0 or len(self.get_videos()) > 0


def download_file(url, file_path, date, timeout=10, skip_exists=True):
    if skip_exists and os.path.exists(file_path):
        print('FILE EXISTS', file_path)
        return 0

    try:
        # Send a GET request to the URL
        print(f"Downloading {file_path} {url}")
        response = requests.get(url, timeout=timeout)

        # Check if the request was successful
        if response.status_code == 200:
            # Open a file in binary write mode to save the image
            with open(file_path, "wb") as file:
                file.write(response.content)

                if date:
                    edit_creation_date(file_path, date)

            return 1  # Exit the loop if download is successful
        else:
            print(f"Failed to download file. Status code: {response.status_code}")  # time.sleep(10)  # Optional: Wait before retrying
    except Exception as e:
        print(f"An error occurred: {e}")  # time.sleep(10)  # Optional: Wait before retrying

    return -1


def edit_creation_date(file_path, new_date: datetime):
    # print('Set ', full_path, ' to ', file_date)
    file = filedate.File(file_path)
    file.created = new_date
    file.modified = new_date
    file.accessed = new_date


def filter_data(json_data):
    out = []

    for data in json_data:
        if data['content']['entryType'] != 'TimelineTimelineItem':
            weird_types.add(data['content']['entryType'])
            continue

        # if get_post_id(data) != '935786439920332800':
        #     continue


        # if not get_media(data):
        #     continue

        # print(data)
        out.append(data)

    return out

def filter_posts(posts: list[Post]):
    out = []

    for p in posts:
        # if not is_retweet(p.data):
        #     continue

        out.append(p)

    return out

def gather_events(root_dir):
    files = os.scandir(root_dir)
    out = []
    for file in files:
        if file.is_file():
            event_date = file.name.split('.')[0]
            out.append(event_date)
    return out

def gather_posts_by_event(dirs, events_dict):
    out_dict = dict()
    files = []

    for d in dirs:
        files += os.scandir(d)

    # for f in files:
    #     print(f.name)
    # return out_dict

    # with open('invalid.txt', 'r') as file:
    #     ignored_auth = set(file.read().split())

    ignored_auth = get_invalid_authors()

    seen = set()
    for file in files:
        if file.is_file():
            event_date = file.name.split('.')[0]

            if event_date not in events_dict:
                print('WARNING skipping event not found in database', event_date)
                continue

            # event_data = events_dict[event_date]

            with open(file.path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            out_dict.setdefault(event_date, [])

            for d in json_data:
                if not is_tweet(d):
                    continue

                post = Post(d)
                if post.author in ignored_auth:
                    # print('Ignored', post.author)
                    continue

                if post.post_id in seen:
                    # print('FOUND DUPE', post.post_id)
                    continue

                seen.add(post.post_id)
                out_dict[event_date].append(post)

    return out_dict


def gather_json_data(root_dir):
    files = os.listdir(root_dir)

    post_dict = dict()

    for f in files:
        if f.endswith('.json'):
            path = f'{root_dir}/{f}'
            with open(path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)

                json_data = filter_data(json_data)

                for d in json_data:
                    post = Post(d)

                    if post.post_id in post_dict:
                        print('FOUND DUPE', post.post_id)
                        continue

                    post_dict[post.post_id] = post

                all_posts = list(sorted(post_dict.values(), key=lambda p: p.date))

                all_posts = filter_posts(all_posts)

            # return json_data, all_posts


                # for data in json_data:  #     if data['content']['entryType'] != 'TimelineTimelineItem':  #         weird_types.add(data['content']['entryType'])  #         continue  #  #     print(data)  #  #     # break  #  # print(list(weird_types))  # return

    # print('Total posts', len(all_posts))

def get_authors():
    url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRPT5wfb1Eh7r7RqGXJNtXeUhbAlokMvIiZdB6PdAQZoRb4JkwCy5Lw4XylvAwnsr7lmVbqPdPrVsMO/pub?gid=4550570&single=true&output=tsv'
    response = requests.get(url)
    response.encoding = 'utf-8'
    tsv_data = response.text

    out = []

    reader = csv.reader(StringIO(tsv_data), delimiter='\t')

    headers = next(reader)
    for row in reader:
        elem = {}
        for i, h in enumerate(headers):
            elem[h] = row[i]
        # print(elem)
        out.append(elem)

    return out

def get_invalid_authors():
    invalid_auth = set()
    for r in get_authors():
        if r['Download'] == 'n' or r['Deleted'] == 'y':
            print('Invalid auth', r['Name'])
            invalid_auth.add(r['Name'])
    return invalid_auth


def get_events_dict():
    events_sheet = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRPT5wfb1Eh7r7RqGXJNtXeUhbAlokMvIiZdB6PdAQZoRb4JkwCy5Lw4XylvAwnsr7lmVbqPdPrVsMO/pub?gid=1556948653&single=true&output=tsv'

    df = pd.read_csv(events_sheet, sep='\t', header=0)
    df = df.where(pd.notnull(df), None)

    event_dict = dict()

    for r in df.to_dict(orient="records"):
        if r['Ignored']:
            print('Skipping event ', r['Eng Name'])
            continue

        event_dict.setdefault(str(r['Date']), [])
        event_dict[str(r['Date'])].append(r)

    return event_dict
