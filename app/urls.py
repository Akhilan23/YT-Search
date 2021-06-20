from django.urls import path

from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('api/videos/page=<int:pageNumber>', views.getVideos, name='getVideos'),
  path('api/videos/page=<int:pageNumber>&query=<str:searchTerm>', views.getVideos, name='getVideos')
]