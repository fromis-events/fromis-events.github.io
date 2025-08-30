import json
import os
import shutil
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from twitter_utils import *

root_dir = 'raw/data'

weird_types = set()


def make_image_md(url, caption='', zoom_click=True, figure=True):
    if caption:
        caption = f'<figcaption>{caption}</figcaption>'

    zoom_md = 'onclick="openFullscreen(this)' if zoom_click else ''

    if figure:
        return f"""\
<figure markdown="1">
![]({url}){{ loading=lazy {zoom_md}"}}{caption}
</figure>"""
    else:
        return f'![]({url + '?type=e1920'}){{ loading=lazy {zoom_md}"}}{caption}'


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


def make_media_md(data):
    elems = []
    if media := get_media(data):
        for m in media:
            image_url = m['media_url_https']
            # if not image_url.endswith('.jpg'):
            #     breakpoint()
            if video_info := m.get('video_info'):
                varients = video_info['variants']
                # for v in varients:
                #     if v['content_type'] == 'video/mp4':
                #         # video_url = v['url']
                if video_url := get_video_url(data):
                    elems.append(make_video_md(video_url, image_url, 'video/mp4'))
            else:
                elems.append(make_image_md(image_url))
    return '\n'.join(elems)


def make_post(post: Post):
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

{make_media_md(post.data)}
</div>
</div>

<div style="text-align: right;" markdown="1">
<a href="https://twitter.com/realfromis_9/status/{post.post_id}" style="text-align: right;">:material-share:{{.big-emoji}}</a>
</div>
---
"""

    # if media := get_media(data):
    #     for m in media:

    dir = 'docs/twitter/posts'
    out_path = f'{dir}/{post.post_id}.md'

    with open(out_path, 'w', encoding='utf-8') as txt:
        txt.writelines(out)


def main():
    shutil.rmtree('docs/twitter/posts')
    os.makedirs('docs/twitter/posts')

    json_data, all_posts = gather_json_data(root_dir)

    i = 0
    for p in all_posts:
        make_post(p)

        i += 1
        if i > 20:
            break

    # write_all_tags(json_data, 'docs/twitter/tags.md')

    # files = os.listdir(root_dir)  #  # shutil.rmtree('docs/twitter/posts')  # os.makedirs('docs/twitter/posts')  #  # for f in files:  #     if f.endswith('.json') and f.startswith('final'):  #         path = f'{root_dir}/{f}'  #         with open(path, 'r', encoding='utf-8') as file:  #             json_data = json.load(file)  #  #             json_data = filter_data(json_data)  #  #             for data in json_data:  #                 if data['content']['entryType'] != 'TimelineTimelineItem':  #                     weird_types.add(data['content']['entryType'])  #                     continue  #  #  #                 if get_media(data):  #                     make_post(data)  #  #                 print(data)  #  #                 # break  #  #             print(list(weird_types))  #             # return


if __name__ == '__main__':
    # main()

    json_data, all_posts = gather_json_data(root_dir)
    download_all_media(all_posts)
