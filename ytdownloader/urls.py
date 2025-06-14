"""
URL configuration for ytdownloader project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from downloader import views
from downloader.views import history_view
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # 👈 this is required!
    path('download/', views.download_video, name='download'),    # Home page (main form)
    path('history.html/', views.history_view, name='history'),  # History page
    path('fetch_info/', views.fetch_video_info, name='fetch_info'),  # History page
    path('delete_history/<int:id>/', views.delete_history, name='delete_history'),# ✅ This must match,  # History page
    path('history.html/', views.history_view, name='download_history'),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

