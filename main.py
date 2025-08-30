import json
import os
import shutil
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from twitter_utils import *

root_dir = 'json-test'

weird_types = set()


def make_image_md(url, caption='', zoom_click=True, figure=True):
    if caption:
        caption = f'<figcaption>{caption}</figcaption>'

    zoom_md = f'onclick="openFullscreen(this, \'{url}\')"' if zoom_click else ''

    base_url = url.rsplit('.', maxsplit=1)[0]

    if 'png' in url.rsplit('.', maxsplit=1)[1]:
        print('FOUND PNG', url)

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


def make_event(event_date, posts: list[Post]):
    out = f"""---
slug: \"{event_date}\"
date: {datetime.strptime(event_date, "%y%m%d")}
---

# {event_date}

"""

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

def make_index(events):
    sorted_events = sorted(events)

    out = ""

    for e in sorted_events:
        out += f"""
* [{e}](./events/{e})
"""

    with open('docs/index.md', 'w', encoding='utf-8') as txt:
        txt.writelines(out)

    # posts_by_event = gather_events(root_dir)
    # for event, posts in posts_by_event.items():


def main():
    if os.path.exists('docs/events'):
        shutil.rmtree('docs/events')
    os.makedirs('docs/events')

    # json_data, all_posts = gather_json_data(root_dir)


    posts_by_event = gather_posts_by_event(root_dir)

    print(f'Generating {len(posts_by_event)} events')

    make_index(posts_by_event.keys())

    i = 0
    for event, posts in posts_by_event.items():
        make_event(event, posts)
        # for p in posts:
        #     make_post(event, p)

        # i += 1
        # if i > 20:
        #     break

    # write_all_tags(json_data, 'docs/twitter/tags.md')

    # files = os.listdir(root_dir)  #  # shutil.rmtree('docs/twitter/posts')  # os.makedirs('docs/twitter/posts')  #  # for f in files:  #     if f.endswith('.json') and f.startswith('final'):  #         path = f'{root_dir}/{f}'  #         with open(path, 'r', encoding='utf-8') as file:  #             json_data = json.load(file)  #  #             json_data = filter_data(json_data)  #  #             for data in json_data:  #                 if data['content']['entryType'] != 'TimelineTimelineItem':  #                     weird_types.add(data['content']['entryType'])  #                     continue  #  #  #                 if get_media(data):  #                     make_post(data)  #  #                 print(data)  #  #                 # break  #  #             print(list(weird_types))  #             # return


if __name__ == '__main__':
    main()

    # json_data, all_posts = gather_json_data(root_dir)
    # download_all_media(all_posts)
