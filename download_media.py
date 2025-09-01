from twitter_utils import *

def download_all_media(posts: list[Post]):
    images = []
    videos = []
    for p in posts:
        images += [(p, i) for i in p.get_images()]
        videos += [(p, v) for v in p.get_videos()]  # if len([(p, v) for v in p.get_videos()]) > 1:  #     print('MULTIPLE VIDS', p.link)

        # if len(p.get_images()) > 1:  #     print(p.data)  #     breakpoint()  # if len(p.get_videos()) > 1:  #     print(p.data)  #     breakpoint()

    # print('imgs', len(images))
    # print('vids', len(videos))

    id_check = set()
    for index, (p, i) in enumerate(images):
        image_id = i['id_str']
        image_url = i['media_url_https']
        image_ext = get_img_ext(image_url)
        image_url = image_url + f'?format={image_ext}&name=orig'
        image_path = f'raw/media/images/{image_id}.{image_ext}'

        result = download_file(image_url, image_path, p.date)
        print(f'{index}/{len(images)}')
        if result != 0:
            time.sleep(random.randrange(8, 15))

    print('Total imgs', len(images))

    # return
    for p, v in videos:
        video_id = v['id_str']
        thumb = v['media_url_https']
        # id = get_video_id(v)
        if video_id in id_check:
            print('HUH', video_id)
            breakpoint()

        # id_check.add(id)
        # print(len(id))

        # download_thumb
        thumb_path = f'raw/media/videos/{video_id}.{get_img_ext(thumb)}'
        result = download_file(thumb, thumb_path, p.date)
        if result == 1:
            time.sleep(random.randrange(8, 15))
        elif result == -1:
            print('failed to download image', p.link)

        # print('Downloading ', p.link, thumb, thumb_path)

        # download_video

        video_url = get_video_url(v)
        video_ext = get_video_ext(video_url)
        video_path = f'raw/media/videos/{video_id}.{video_ext}'  # print('Downloading ', p.link, url, video_path)
        result = download_file(video_url, video_path, p.date, 120)
        if result == 1:
            time.sleep(random.randrange(20, 30))
        elif result == -1:
            print('failed to download video', p.link)

        # if ext != 'mp4':  #     breakpoint()
    print(len(videos))


if __name__ == '__main__':
    events_dict = get_events_dict()
    posts_by_event = gather_posts_by_event(['json2', 'json'], events_dict)

    all_posts = []
    for e, ps in posts_by_event.items():
        all_posts += ps
        # print(ps)

    # this doesn't download the events!!!
    download_all_media(all_posts)
