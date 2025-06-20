import os
import yt_dlp
from vk_api import VkApi
my_group_id = -216521493
access_token = os.environ.get("VK_ACCESS_TOKEN")

# Получаем все видео из группы
def get_vk_videos(group_id):
    vk_session = VkApi(token=access_token)
    vk = vk_session.get_api()
    
    videos = []
    offset = 0
    count = 100  # Максимум за 1 запрос
    
    while True:
        response = vk.video.get(owner_id=group_id, offset=offset, count=count)
        if not response['items']:
            break
        videos.extend(response['items'])
        offset += count
    
    return videos
videos = get_vk_videos(my_group_id)

def download_video(url, title):
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip()
    os.makedirs('videos', exist_ok=True)
    
    ydl_opts = {
        'format': 'best',  # Лучшее качество
        'outtmpl': f'videos/{safe_title}.%(ext)s',
        'quiet': True,     # Уменьшаем вывод в консоль
    }
    if not os.path.exists(f"videos/{safe_title}.mp4"):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    else:
        print(f'Уже скачано: {title}!')

for video in videos:
    if 'player' in video:  # Используем embed-ссылку
        print(f"Скачиваем: {video['title']}")
        download_video(video['player'], video['title'])
