import os
import random
import time

import json
import twitter_utils as utils
from twitter_utils import Post

def main():
    with open('json/180710.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(len(data))
    for d in data:
        if d['content']['__typename'] != 'TimelineTimelineItem':
            # print(d)
            continue

        post = Post(d)
        if len(post.media):
            print(d)
            print(post.post_id, post.link)

        # print('\n')

def download_json():
    files = os.scandir('json')
    for file in files:
        if file.is_file():
            event_date = file.name.split('.')[0]
            with open(file.path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            out_dir = f'media/events/{event_date}'
            os.makedirs(out_dir, exist_ok=True)

            for d in json_data:
                if not utils.is_tweet(d):
                    continue

                post = Post(d)

                # if post.author == 'ondaia':
                #     print(d)
                #
                # if utils.is_retweet(d):
                #     print(d)
                #     continue

                # if post.author in ignored:
                #     continue

                if len(post.get_images()):
                    # print(d)
                    print(post.post_id, len(post.get_images()))
                    for i, img in enumerate(post.get_images()):
                        # image_id = img['id_str']
                        image_url = img['media_url_https']
                        image_ext = utils.get_img_ext(image_url)
                        image_url = image_url + f'?format={image_ext}&name=orig'
                        image_path = f'{out_dir}/{post.author}-{post.post_id}-{i}.{image_ext}'
                        print(i, image_url, image_path)

                        result = utils.download_file(image_url, image_path, post.date)
                        if result != 0:
                            time.sleep(random.randrange(5, 12))

def get_tweets(folder):
    out_dict = dict()
    files = os.scandir(folder)
    for file in files:
        if file.is_file():
            with open(file.path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            event_date = file.name.split('.')[0]

            for d in json_data:
                if utils.is_tweet(d):
                    # print(d)
                    post = Post(d)
                    post.event_date = event_date
                    out_dict[post.post_id] = post
    return out_dict

def log_authors():
    files = os.scandir('json')
    authors = dict()
    latest = dict()
    earliest = dict()
    for file in files:
        if file.is_file():
            event_date = file.name.split('.')[0]
            with open(file.path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            out_dir = f'media/events/{event_date}'
            os.makedirs(out_dir, exist_ok=True)

            for d in json_data:
                if utils.is_tweet(d):
                    # print(d)
                    post = Post(d)
                    if len(post.get_images()) > 0 or len(post.get_videos()) > 0:
                    # print(post.author)
                        authors.setdefault(post.author, 0)
                        authors[post.author] += 1

                        latest.setdefault(post.author, post.date)
                        if post.date > latest[post.author]:
                            latest[post.author] = post.date

                        earliest.setdefault(post.author, post.date)
                        if post.date < earliest[post.author]:
                            earliest[post.author] = post.date

    tuples = authors.items()

    new_tuples = sorted(tuples, key=lambda x: x[1])
    for name, count in new_tuples:
        print(f'{name}\t{count}\t{earliest[name].strftime("%Y-%m-%d")}\t{latest[name].strftime("%Y-%m-%d")}')

def log_authors2(posts):
    authors = dict()
    total_authors = dict()
    latest = dict()
    earliest = dict()

    for post in posts:
        total_authors.setdefault(post.author, 0)
        total_authors[post.author] += 1
        if len(post.get_images()) > 0 or len(post.get_videos()) > 0:
        # print(post.author)
            authors.setdefault(post.author, 0)
            authors[post.author] += 1

            latest.setdefault(post.author, post.date)
            if post.date > latest[post.author]:
                latest[post.author] = post.date

            earliest.setdefault(post.author, post.date)
            if post.date < earliest[post.author]:
                earliest[post.author] = post.date

    tuples = authors.items()

    new_tuples = sorted(tuples, key=lambda x: x[1])
    for name, count in new_tuples:
        print(f'{name}\t{count}\t{total_authors[name]}\t{earliest[name].strftime("%Y-%m-%d")}\t{latest[name].strftime("%Y-%m-%d")}')

def write_combined():
    tweets_1 = get_tweets('json')
    print(len(tweets_1))
    tweets_2 = get_tweets('json2')
    print(len(tweets_2))
    combined = tweets_2 | tweets_1
    d = [c.data for c in combined.values()]

    with open('combined.json', 'w', encoding='utf-8') as f:
        json.dump(d, f)

def get_posts() -> list[Post]:
    out = []
    with open('combined.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for d in data:
        out.append(Post(d))
    return out

def log_downloaded_url(url, log_file="downloaded.txt"):
    with open(log_file, "a") as f:
        f.write(url + "\n")

def get_downloaded(log_file="downloaded.txt"):
    if not os.path.exists(log_file):
        return set()

    with open(log_file, "r") as f:
        return set(line.strip() for line in f)

def download_posts(posts, valid):
    downloaded_set = get_downloaded()

    failed_ids = get_failed_ids()

    for post in posts:
        if post.author not in valid:
            continue

        if post.event_date not in post.full_text:
            continue

        if len(post.get_images()):
            out_dir = f'media/events/{post.event_date}'
            os.makedirs(out_dir, exist_ok=True)

            print(post.post_id, len(post.get_images()))
            for i, img in enumerate(post.get_images()):

                # image_id = img['id_str']
                image_url = img['media_url_https']
                image_ext = utils.get_img_ext(image_url)
                image_url = image_url + f'?format={image_ext}&name=orig'

                if image_url in downloaded_set:
                    continue

                if image_url in failed_ids:
                    print('Skip failed', image_url)
                    continue

                image_path = f'{out_dir}/{post.author}-{post.post_id}-{i}.{image_ext}'
                print(i, image_url, image_path)

                result = utils.download_file(image_url, image_path, post.date)
                if result != -1:
                    log_downloaded_url(image_url)
                else:
                    with open('failed.txt', 'a', encoding='utf-8') as f:
                        f.write(f'{post.event_date}\t{post.author}\t{post.post_id}\t{i}\t{image_url}\n')

                if result != 0:
                    time.sleep(random.randrange(5, 12))

def get_failed_ids():
    failed = set()
    with open('failed.txt', 'r', encoding='utf-8') as failed_file:
        failed_lines = failed_file.read().split('\n')
        for line in failed_lines:
            if line:
                rows = line.split('\t')
                print(rows)
                failed.add(rows[4])
    return failed
        # failed_file.split()


def main():
    rows = utils.get_authors()

    valid = set()
    for r in rows:
        if r['Download'] == 'y' and r['Deleted'] != 'y':
            print(r['Name'])
            valid.add(r['Name'])

    # download_json()
    # log_authors()
    # main()
    # write_combined()

    # posts = get_posts()
    # for p in posts:
    #     if p.author == 'PromisePollen':
    #         print(p.link, '\t', p.full_text)

    tweets_1 = get_tweets('json')
    print(len(tweets_1))
    tweets_2 = get_tweets('json2')
    print(len(tweets_2))
    #
    combined = tweets_2 | tweets_1
    print(len(combined))

    posts = combined.values()
    # log_authors2(posts)

    download_posts(posts, valid)

if __name__ == '__main__':
    main()