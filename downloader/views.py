from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.views.decorators.http import require_POST
from yt_dlp import YoutubeDL

from .models import DownloadHistory
from .utils import download_video
from .models import DownloadHistory
import yt_dlp
from django.http import JsonResponse, HttpResponseBadRequest, FileResponse
import json
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import platform
import zipfile
import urllib.request

class URLForm(forms.Form):
    youtube_url = forms.URLField(label="YouTube URL", widget=forms.URLInput(attrs={'class': 'form-control'}))

def index(request):
    return render(request, 'index.html')

def history_view(request):
    history = DownloadHistory.objects.all().order_by('-downloaded_at')
    return render(request, 'history.html', {'history': history})

@csrf_exempt
def download_video(request):
    if request.method == "POST":
        try:
            url = request.POST.get("youtube_url")
            itag = request.POST.get("resolution")

            if not url or not itag:
                return JsonResponse({"success": False, "error": "Missing URL or format."})

            output_dir = os.path.join(settings.MEDIA_ROOT, "downloads")
            os.makedirs(output_dir, exist_ok=True)

            ydl_opts = {
                'format': f'{itag}+bestaudio/best',  # 🔥 Automatically merges video+audio if needed
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',
                'quiet': True,
                'noplaylist': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title")
                filename = ydl.prepare_filename(info)

            # Save to download history
            relative_path = os.path.relpath(filename, settings.MEDIA_ROOT)
            DownloadHistory.objects.create(
                title=title,
                url=url,
                file_path=os.path.join(settings.MEDIA_URL, relative_path)
            )

            return JsonResponse({"success": True, "message": "Download complete."})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})



@csrf_exempt
def fetch_video_info(request):
    if request.method == "POST":
        try:

            # ensure_ffmpeg_installed()  # <== Important

            data = json.loads(request.body)
            url = data.get("youtube_url")

            ydl_opts = {
                'quiet': True,
                'skip_download': True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = []

                for f in info.get("formats", []):
                    if f.get("vcodec") != "none":  # allow both video-only and video+audio
                        filesize = f.get("filesize") or f.get("filesize_approx") or 0
                        formats.append({
                            'itag': f['format_id'],
                            'ext': f.get('ext'),
                            'format_note': f.get('format_note') or f.get('resolution'),
                            'resolution': f.get('resolution'),
                            'filesize': filesize,
                            'has_audio': f.get("acodec") != "none"
                        })

                return JsonResponse({
                    'success': True,
                    'title': info.get('title'),
                    'thumbnail': info.get('thumbnail'),
                    'formats': formats
                })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})




FFMPEG_DIR = os.path.join(os.getcwd(), "ffmpeg")

def ensure_ffmpeg_installed():
    ffmpeg_path = os.path.join(FFMPEG_DIR, "bin", "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg")

    # Already installed
    if os.path.isfile(ffmpeg_path):
        os.environ["PATH"] += os.pathsep + os.path.join(FFMPEG_DIR, "bin")
        return

    # Download FFmpeg for Windows
    if platform.system() == "Windows":
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = os.path.join(FFMPEG_DIR, "ffmpeg.zip")

        os.makedirs(FFMPEG_DIR, exist_ok=True)

        print("Downloading FFmpeg...")
        urllib.request.urlretrieve(url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if member.endswith('ffmpeg.exe'):
                    zip_ref.extract(member, FFMPEG_DIR)
            zip_ref.extractall(FFMPEG_DIR)

        # Move `bin` folder
        for root, dirs, files in os.walk(FFMPEG_DIR):
            if 'ffmpeg.exe' in files:
                bin_path = os.path.dirname(os.path.join(root, 'ffmpeg.exe'))
                os.environ["PATH"] += os.pathsep + bin_path
                break

        os.remove(zip_path)

@require_POST
def delete_history(request, id):
    """Delete a download history record by ID."""
    item = get_object_or_404(DownloadHistory, id=id)
    item.delete()
    return redirect('download_history')  # Replace with your actual history page's URL name