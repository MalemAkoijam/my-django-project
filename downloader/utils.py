from pytube import YouTube
import os

def download_video(youtube_url, download_path='downloads/'):
    yt = YouTube(youtube_url)
    stream = yt.streams.get_highest_resolution()

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    file_path = stream.download(output_path=download_path)
    return yt.title, file_path
