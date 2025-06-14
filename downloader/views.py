import tempfile

from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.views.decorators.http import require_POST
from yt_dlp import YoutubeDL
import os
from django.conf import settings
from urllib.parse import quote
from .models import DownloadHistory
import yt_dlp
from django.http import JsonResponse, HttpResponseBadRequest, FileResponse, Http404
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# Path to cookies file (update this to match your path)
COOKIES_FILE = os.path.join(settings.BASE_DIR, 'cookies', 'cookies.txt')

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
                return JsonResponse({"success": False, "error": "Missing URL or format."}, status=400)

            # Temporary download location
            temp_dir = tempfile.mkdtemp()
            ydl_opts = {
                'format': f'{itag}+bestaudio/best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',
                'quiet': True,
                'noplaylist': True,
                'cookies': COOKIES_FILE,
                'quiet': True,
                'noplaylist': True,
                # Replace with actual path to cookies.txt if needed
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            if not os.path.exists(filename):
                raise Http404("Download failed.")

            response = FileResponse(open(filename, 'rb'), as_attachment=True, filename=os.path.basename(filename))
            return response

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)


@csrf_exempt
def fetch_video_info(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

    try:
        data = json.loads(request.body)
        url = data.get("youtube_url")

        if not url:
            return JsonResponse({'success': False, 'error': 'URL is required'}, status=400)

        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'cookies': COOKIES_FILE,  # ✅ Use cookies
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []

            for f in info.get("formats", []):
                if f.get("vcodec") != "none":  # keep video-only and video+audio
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
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_POST
def delete_history(request, id):
    """Delete a download history record by ID."""
    item = get_object_or_404(DownloadHistory, id=id)
    item.delete()
    return redirect('download_history')  # Replace with your actual history page's URL name