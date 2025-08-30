import json
import os
import shutil
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from twitter_utils import *
import pandas as pd

# root_dir = 'json-test'

events_sheet = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRPT5wfb1Eh7r7RqGXJNtXeUhbAlokMvIiZdB6PdAQZoRb4JkwCy5Lw4XylvAwnsr7lmVbqPdPrVsMO/pub?gid=1556948653&single=true&output=tsv'

weird_types = set()


def make_image_md(url, caption='', zoom_click=True, figure=True):
    if caption:
        caption = f'<figcaption>{caption}</figcaption>'

    zoom_md = f'onclick="openFullscreen(this, \'{url}\')"' if zoom_click else ''

    base_url = url.rsplit('.', maxsplit=1)[0]

    # if 'png' in url.rsplit('.', maxsplit=1)[1]:
    #     print('FOUND PNG', url)

    low_res_url = base_url + '?format=jpg&name=medium'

    if figure:
        return f"""\
<figure markdown="1">
![]({low_res_url}){{ loading=lazy {zoom_md}"}}{caption}
</figure>"""
    else:
        return f'![]({low_res_url}){{ loading=lazy {zoom_md}"}}{caption}'


def make_iframe_md(embed_url, display_url=None):
    if display_url is None:
        return f"""\
<figure class="snippet" markdown="1">
<iframe src="{embed_url}" frameborder="0" allow="fullscreen"></iframe>
</figure>"""
    else:
        return f"""\
<figure class="snippet" markdown="1">
<iframe src="{embed_url}" frameborder="0" allow="fullscreen"></iframe>
<figcaption><a href="{display_url}">{display_url}</a></figcaption>
</figure>"""


def make_video_md(url, thumb_path, content_type):
    # if youtubeVideoId := video_redirects.get(attachment_id):
    #     return make_iframe_md(f'https://www.youtube.com/embed/{youtubeVideoId}')
    # else:
    return f"""
<figure markdown="1">
<video controls="controls" preload="none" poster="{thumb_path}">
<source src="{url}" type="{content_type}">
Your browser does not support the video tag.
</video>
</figure>"""


def make_media_md(post):
    elems = []

    for img in post.get_images():
        image_url = img['media_url_https']
        elems.append(make_image_md(image_url))

    for vid in post.get_videos():
        if video_url := get_video_url(vid):
            elems.append(make_video_md(video_url, vid['media_url_https'], 'video/mp4'))
        else:
            elems.append(vid['media_url_https'])


    # print('Generating media for', data)
    # if media := get_media(data):
    #     for m in media:
    #         image_url = m['media_url_https']
    #         # if not image_url.endswith('.jpg'):
    #         #     breakpoint()
    #
    #         if video_url := get_video_url(data):
    #             print('\tMake video', video_url)
    #             elems.append(make_video_md(video_url, image_url, 'video/mp4'))
    #         # if video_info := m.get('video_info'):
    #         #     varients = video_info['variants']
    #         #     # for v in varients:
    #         #     #     if v['content_type'] == 'video/mp4':
    #         #     #         # video_url = v['url']
    #
    #         else:
    #             print('\tMake img', image_url)
    #             elems.append(make_image_md(image_url))
    return '\n'.join(elems)


def make_post_md(post: Post):
    # tags = get_tags(post.data)
    # tags_md = '\n'.join(['  - ' + t.removeprefix('#') for t in tags])

    out = f"""
<div class="post-container" markdown="1">
<div class="content-container md-sidebar__scrollwrap" markdown="1">
{post.full_text}

{make_media_md(post)}
</div>
</div>

<div style="text-align: right;" markdown="1">
<a href="{post.link}" style="text-align: right;">:material-share:{{.big-emoji}}</a>
</div>
"""
    
    return out

def make_post(event_date, post: Post):
    tags = get_tags(post.data)
    tags_md = '\n'.join(['  - ' + t.removeprefix('#') for t in tags])

    out = f"""---
slug: \"{post.post_id}\"
date: {post.date}
tags:
{tags_md}
---

# {post.post_id}

<div class="post-container" markdown="1">
<div class="content-container md-sidebar__scrollwrap" markdown="1">
{post.full_text}

{make_media_md(post)}
</div>
</div>

<div style="text-align: right;" markdown="1">
<a href="{post.link}" style="text-align: right;">:material-share:{{.big-emoji}}</a>
</div>
---
"""

    # if media := get_media(data):
    #     for m in media:

    dir = f'docs/twitter/events/{event_date}/posts'
    os.makedirs(dir, exist_ok=True)
    out_path = f'{dir}/{post.post_id}.md'

    with open(out_path, 'w', encoding='utf-8') as txt:
        txt.writelines(out)

def make_youtube_md(url):
    embed_url = url.replace('watch?v=', 'embed/')
    return f"""
<figure class="snippet" markdown="1">
<iframe 
    src="{embed_url}"
    title="What is this"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
    allowfullscreen>
</iframe>
<a href="{url}">{url}</a>
</figure>
"""


def make_event(event_date, posts: list[Post], events_dict):
    if len(posts) == 0:
        print('ERROR', event_date, 'has no posts')
    #     return

    events = events_dict[event_date]
    out = f"""---
slug: \"{event_date}\"
date: {datetime.strptime(event_date, "%y%m%d")}
---

# {event_date} {get_event_name(event_date, events_dict)}

"""

    for e in events:
        out += f'**{e['Eng Name']}**\n\n'
        out += f'* [Twitter Search]({e['Twitter']}) | [Youtube Search]({e['YouTube']})\n'

        if cam_1 := e.get('Cam 1'):
            out += make_youtube_md(cam_1) + '\n'

        if cam_2 := e.get('Cam 2'):
            out += make_youtube_md(cam_2) + '\n'

        # out += f'# {e['Eng Name']}'
        # print(e)

    by_author = dict()
    for p in posts:
        if "open.kakao.com" in p.full_text:
            continue

        by_author.setdefault(p.author, [])
        by_author[p.author].append(p)

    by_author = dict(sorted(by_author.items(), key=lambda item: len(item[1]), reverse=True))

    for auth, ps in by_author.items():
        ps = [p for p in ps if p.has_media()]

        if len(ps):
            out += f'## {auth}\n'

            for p in ps:
                if len(p.get_images()) == 0 and len(p.get_videos()) == 0:
                    continue

                post_md = make_post_md(p)
                out += post_md
                out += '\n'

    dir = f'docs/events'
    os.makedirs(dir, exist_ok=True)
    out_path = f'{dir}/{event_date}.md'

    with open(out_path, 'w', encoding='utf-8') as txt:
        txt.writelines(out)

def make_index(events, events_dict):
    sorted_events = sorted(events)

    out = "# Events\n"

    for e in sorted_events:
        out += f"""
* [**{e}** {get_event_name(e, events_dict)}](./events/{e})
"""

    with open('docs/index.md', 'w', encoding='utf-8') as txt:
        txt.writelines(out)

    # posts_by_event = gather_events(root_dir)
    # for event, posts in posts_by_event.items():

def get_events_dict():
    df = pd.read_csv(events_sheet, sep='\t', header=0)
    df = df.where(pd.notnull(df), None)

    # as_dict =
    # print(as_dict)
    event_dict = dict()

    for r in df.to_dict(orient="records"):
        event_dict.setdefault(str(r['Date']), [])
        event_dict[str(r['Date'])].append(r)

    # current_dates = dict()
    # for row in df.values:
    #     if not pd.isna(row[0]):
    #         event_date = str(row[0])
    #         event_name = row[1].replace('>', '').replace('<', '')
    #
    #         current_dates.setdefault(event_date, [])
    #         current_dates[event_date].append(event_name)
    #         # print(row[0], row[1])

    return event_dict

def get_event_name(event, events_dict):
    if events := events_dict.get(event):
        names = [e['Eng Name'] for e in events]
        return ' & '.join(names)
    else:
        print('ERROR failed to find event name for', event)
        return 'Unknown Event'

def main():
    events_dict = get_events_dict()

    if os.path.exists('docs/events'):
        shutil.rmtree('docs/events')
    os.makedirs('docs/events')

    # json_data, all_posts = gather_json_data(root_dir)

    posts_by_event = gather_posts_by_event(['json-test'])

    # these are folders!
    # posts_by_event = gather_posts_by_event(['json2', 'json'])

    print(f'Generating {len(posts_by_event)} events')

    make_index(posts_by_event.keys(), events_dict)

    i = 0
    for event, posts in posts_by_event.items():
        make_event(event, posts, events_dict)
        # for p in posts:
        #     make_post(event, p)

        # i += 1
        # if i > 20:
        #     break

    # write_all_tags(posts_by_event, 'docs/events/tags.md')

    # files = os.listdir(root_dir)  #  # shutil.rmtree('docs/twitter/posts')  # os.makedirs('docs/twitter/posts')  #  # for f in files:  #     if f.endswith('.json') and f.startswith('final'):  #         path = f'{root_dir}/{f}'  #         with open(path, 'r', encoding='utf-8') as file:  #             json_data = json.load(file)  #  #             json_data = filter_data(json_data)  #  #             for data in json_data:  #                 if data['content']['entryType'] != 'TimelineTimelineItem':  #                     weird_types.add(data['content']['entryType'])  #                     continue  #  #  #                 if get_media(data):  #                     make_post(data)  #  #                 print(data)  #  #                 # break  #  #             print(list(weird_types))  #             # return


if __name__ == '__main__':
    main()

    # json_data, all_posts = gather_json_data(root_dir)
    # download_all_media(all_posts)
