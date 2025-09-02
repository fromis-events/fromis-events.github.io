from pathlib import Path

import json
import os
import shutil
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from twitter_utils import *
import pandas as pd

# root_dir = 'json-test'

weird_types = set()

era_dates = [
    [250625, "From Our 20's"],
    [240812, 'Supersonic'],
    [230518, 'Unlock My World'],
    [220608, 'from our Memento Box'],
    [200911, 'My Little Society'],
    [220103, 'Midnight Guest'],
    [210828, 'Talk & Talk'],
    [210507, '9 Way Ticket'],
    [200911, 'My Little Society'],
    [190522, 'Fun Factory'],
    [180930, 'From.9'],
    [180601, 'To. Day'],
    [180112, 'To. Heart'],
    [171130, 'Glass Shoes'],
    [170629, 'Idol School'],
    [0, 'Pre-Debut'],
]


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
![]({low_res_url}){{ loading=lazy {zoom_md} class="post-image""}}{caption}
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

    grid = '<div class="invisible-grid" markdown="1">\n'
    grid += '\n'.join(elems)
    grid += '\n</div>'

    # grid += '\n'.join(f'  <div>{e}</div>' for e in elems)
    # grid += '\n'.join(f'  <div>{e}</div>' for e in elems)
    # grid += '\n</div>'
    return grid

    # return '\n'.join(elems)


def make_post_md(post: Post):
    # tags = get_tags(post.data)
    # tags_md = '\n'.join(['  - ' + t.removeprefix('#') for t in tags])

    post_link = f"""
<div class="post-link" style="text-align: right;" markdown="1">
<a href="{post.link}" style="text-align: right;">:material-twitter:{{.big-emoji}}</a>
</div>
"""

    post_text_and_link = f"""
<div class="post-text-container" markdown="1">
{post.full_text}
</div>
"""

    post_media = f"""
<div class="post-media-container" markdown="1">
{make_media_md(post)}
{post_link}
</div>
"""


    out = f"""
<div class="post-container" markdown="1">
<div class="content-container" markdown="1">
{post_text_and_link}
{post_media}
</div>
</div>
"""

    return out

# def make_post(event_date, post: Post):
#     tags = get_tags(post.data)
#     tags_md = '\n'.join(['  - ' + t.removeprefix('#') for t in tags])
#
#     out = f"""---
# slug: \"{post.post_id}\"
# date: {post.date}
# tags:
# {tags_md}
# ---
#
# # {post.post_id}
#
# <div class="post-container" markdown="1">
# <div class="content-container md-sidebar__scrollwrap" markdown="1">
# {post.full_text}
#
# {make_media_md(post)}
# </div>
# </div>
#
# <div style="text-align: right;" markdown="1">
# <a href="{post.link}" style="text-align: right;">:material-share:{{.big-emoji}}</a>
# </div>
# ---
# """
#
#     # if media := get_media(data):
#     #     for m in media:
#
#     dir = f'docs/twitter/events/{event_date}/posts'
#     os.makedirs(dir, exist_ok=True)
#     out_path = f'{dir}/{post.post_id}.md'
#
#     with open(out_path, 'w', encoding='utf-8') as txt:
#         txt.writelines(out)

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

# TODO actually embed the tweet
def make_tweet_md(url):
    return f'<a href="{url}">{url}</a>'



def make_event(event_date, posts: list[Post], events_dict):
    if len(posts) == 0:
        print('ERROR', event_date, 'has no posts')
    #     return

    events = events_dict[event_date]
    out = f"""---
slug: \"{event_date}\"
date: {datetime.strptime(event_date, "%y%m%d")}
hide:
  - navigation
---

# {event_date} {get_event_name(event_date, events_dict)}

"""

    has_alt = False
    for e in events:
        out += f'**{e['Eng Name']}**\n\n'

        twi_search = e['Twitter']
        if alt := e.get('Alt 1'):
            print('Found alt?', alt)
            if 'x.com/search' in alt:
                twi_search = alt
            elif 'x.com' in alt:
                out += f'* {make_tweet_md(alt)}\n'
                has_alt = True

        if alt := e.get('Alt 2'):
            if 'x.com' in alt:
                out += f'* {make_tweet_md(alt)}\n'

        if has_alt:
            continue

        out += f'* [Twitter search]({twi_search}) | [YouTube search]({e['YouTube']})\n'

        if cam_1 := e.get('Cam 1'):
            out += make_youtube_md(cam_1) + '\n'

        if cam_2 := e.get('Cam 2'):
            out += make_youtube_md(cam_2) + '\n'

        out += '\n---\n\n'
        # out += f'# {e['Eng Name']}'
        # print(e)

    by_author = dict()
    for p in posts:
        if "open.kakao.com" in p.full_text:
            continue

        by_author.setdefault(p.author, [])
        by_author[p.author].append(p)

    # by_author = dict(sorted(by_author.items(), key=lambda item: len(item[1]), reverse=True))
    by_author = dict(sorted(by_author.items(), key=lambda item: item[0].lower(), reverse=False))


    if not has_alt:
        first_auth = True
        for auth, ps in by_author.items():
            ps = [p for p in ps if p.has_media()]

            if len(ps):
                if not first_auth:
                    out += '\n</div>\n\n'
                first_auth = False

                out += f'<div class="author-container" markdown="1">\n'
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

    # 1. Start with the table header
    out = f"""---
hide:
  - navigation
---

# Events\n\n
"""

    current_era = None

    for e in sorted_events:
        event_date = int(e)
        event_era = None

        for date, era in era_dates:
            if event_date >= date:
                event_era = era
                break
        # print(e, event_era, event_date)

        if current_era is not event_era:
            if current_era:
                out += '\n\n'

            current_era = event_era

            out += f"## {event_era}\n\n"

            # out += '<div class="center-table">'
            out += "| Thumbnail | Date |  \n"
            out += "|:---:|:---|\n"  # Defines alignment (center for thumb, left for text)


        # Assumes your script runs from the project root, and 'docs' is a subfolder
        thumb_path_for_mkdocs = f'/assets/thumb/{e}.jpg'
        thumb_path_on_disk = f'docs/{thumb_path_for_mkdocs}'

        if not os.path.exists(thumb_path_on_disk):
            print(f'ERROR: No thumbnail found for {thumb_path_on_disk}')
            print(Path(f"./media/events/{e}").absolute().as_uri())
            print(f'http://localhost:8000/events/{e}')
            # print(test.as_uri())

            # You might want to use a placeholder image here
            image_html = '*(No Thumbnail)*'
        else:
            # 2. Use an HTML img tag to control the height
            # image_html = f'<img src="../{thumb_path_for_mkdocs}" alt="Thumbnail for {e}" style="height: 100px;">'
            image_html = f'![*(No Thumbnail)*]({thumb_path_for_mkdocs}){{ width="100" }}'

        # 3. Create the text part with the link
        event_name = get_event_name(e, events_dict)
        link_markdown = f"[**{e}** {event_name}](./{e}){{ loading=lazy }}"

        # 4. Add a new row to the table for this event
        out += f"| {image_html} | {link_markdown} |\n"

    # out += '</div>'
    # return out




#     out = "# Events\n"
#
#     for e in sorted_events:
#         thumb_path = f'assets/thumb/{e}.jpg'
#
#         if not os.path.exists(f'docs/{thumb_path}'):
#             print('ERROR no thumbnail found for ', e)
#
#         out += f"""
# * ![]({thumb_path}) [**{e}** {get_event_name(e, events_dict)}](./events/{e})
# """

    with open('docs/events/index.md', 'w', encoding='utf-8') as txt:
        txt.writelines(out)

    # posts_by_event = gather_events(root_dir)
    # for event, posts in posts_by_event.items():

def get_event_name(event, events_dict):
    if events := events_dict.get(event):
        names = [e['Eng Name'] for e in events]
        return ' & '.join(names)
    else:
        print('ERROR failed to find event name for', event)
        return 'Unknown Event'

def main():
    events_dict = get_events_dict()

    # these are folders!
    posts_by_event = gather_posts_by_event(['json-test'], events_dict)
    # posts_by_event = gather_posts_by_event(['json2', 'json'], events_dict)

    print(f'Generating {len(posts_by_event)} events')

    if os.path.exists('docs/events'):
        shutil.rmtree('docs/events')
    os.makedirs('docs/events')

    make_index(posts_by_event.keys(), events_dict)

    for event, posts in posts_by_event.items():
        make_event(event, posts, events_dict)

if __name__ == '__main__':
    main()

    # json_data, all_posts = gather_json_data(root_dir)
    # download_all_media(all_posts)
