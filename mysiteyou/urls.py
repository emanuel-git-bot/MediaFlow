from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get-video-info/', views.get_video_info_view, name='get_video_info'),
    path('download/', views.download, name='download'),
    path('download_progress/', views.download_progress, name='download_progress'),
    path('downloads/<str:filename>', views.download_file, name='download_file'),
    path('download-desktop/', views.download_desktop_app, name='download_desktop_app'),
]
