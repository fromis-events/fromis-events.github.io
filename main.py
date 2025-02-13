import json
import os
import shutil
import re
from datetime import datetime
from zoneinfo import ZoneInfo

root_dir = 'raw'

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
        return f'![]({url+'?type=e1920'}){{ loading=lazy {zoom_md}"}}{caption}'

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

def get_video_url(data):
    out_url = None
    if media := get_media(data):
        for m in media:
            if video_info := m.get('video_info'):
                variants = video_info['variants']
                max = 0
                for v in variants:
                    if v['content_type'] == 'video/mp4':
                        bitrate = int(v['bitrate'])
                        if bitrate > max:
                            max = bitrate
                            out_url = v['url']
                return out_url
    return None

def make_media_md(data):
    elems = []
    if media := get_media(data):
        for m in media:
            image_url = m['media_url_https']
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

def get_legacy(data):
    return data['content']['itemContent']['tweet_results']['result']['legacy']

def get_datetime(data):
    created_at = get_legacy(data)['created_at']
    date_format = "%a %b %d %H:%M:%S %z %Y"
    return datetime.strptime(created_at, date_format)

def get_full_text(data):
    full_text = get_legacy(data)['full_text']

    if media := get_media(data):
        for m in media:
            # print('searching for ', m['url'])
            full_text = full_text.replace(m['url'], '')

    if urls := get_urls(data):
        for url in urls:
            full_text = full_text.replace(url['url'], f'[{url['expanded_url']}]({url['expanded_url']})')

    pattern = r'(#[\w\uAC00-\uD7A3]+)'
    full_text = re.sub(pattern, r'[\1](www.google.com)', full_text)

    # .replace('#', '\\#')
    return full_text.replace('\n', '<br>\n').strip()

def get_media(data):
    return get_legacy(data)['entities'].get('media')

def get_urls(data):
    return get_legacy(data)['entities'].get('urls')

def get_post_id(data):
    return data['content']['itemContent']['tweet_results']['result']['rest_id']

def make_post(data):
    post_id = get_post_id(data)
    post_fulltext = get_full_text(data)
    post_date = get_datetime(data)
    post_media = get_media(data)

    out = f"""---
slug: \"{post_id}\"
date: {post_date}
---

# {post_id}

<div class="post-container" markdown="1">
<div class="content-container md-sidebar__scrollwrap" markdown="1">
{post_fulltext}

{make_media_md(data)}
</div>
</div>

<div style="text-align: right;" markdown="1">
<a href="https://twitter.com/realfromis_9/status/{post_id}" style="text-align: right;">:material-share:{{.big-emoji}}</a>
</div>
---
"""

    # if media := get_media(data):
    #     for m in media:

    dir = 'docs/twitter/posts'
    id = get_post_id(data)
    out_path = f'{dir}/{id}.md'

    with open(out_path, 'w', encoding='utf-8') as txt:
        txt.writelines(out)

def filter_data(json_data):
    out = []

    for data in json_data:
        if data['content']['entryType'] != 'TimelineTimelineItem':
            weird_types.add(data['content']['entryType'])
            continue

        # if get_post_id(data) != "901017675274436609":
        #     continue

        if not get_media(data):
            continue

        out.append(data)

    return out

def main():
    files = os.listdir(root_dir)

    shutil.rmtree('docs/twitter/posts')
    os.makedirs('docs/twitter/posts')

    for f in files:
        if f.endswith('.json') and f.startswith('final'):
            path = f'{root_dir}/{f}'
            with open(path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)

                json_data = filter_data(json_data)

                for data in json_data:
                    if data['content']['entryType'] != 'TimelineTimelineItem':
                        weird_types.add(data['content']['entryType'])
                        continue


                    if get_media(data):
                        make_post(data)

                    print(data)

                    # break

                print(list(weird_types))
                # return

if __name__ == '__main__':
    main()
