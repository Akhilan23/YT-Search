from django.shortcuts import render, redirect
from django.conf import settings
from app.models import VideoModel
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.core.cache import cache
from datetime import datetime, timezone, date
from isodate import parse_duration
from functools import reduce
from math import ceil

import requests
import time, threading
import json
import operator
import logging

global syncJobRef
logger = logging.getLogger("ytsearch")

class RepeatedTimer(object):
  def __init__(self, interval, function, *args, **kwargs):
    self._timer = None
    self.interval = interval
    self.function = function
    self.args = args
    self.kwargs = kwargs
    self.is_running = False
    self.start()

  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)

  def start(self):
    if not self.is_running:
      self._timer = threading.Timer(self.interval, self._run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    self._timer.cancel()
    self.is_running = False

def home(request):
  startSyncJob()
  return render(request, 'index.html')

def startSyncJob():
  updateApiKey()
  # Runs syncVideoMetadataInBackground every 10 seconds
  syncJobRef = RepeatedTimer(settings.SYNC_INTERVAL, syncVideoMetadataInBackground)
  # jobRef.stop() to stop this job anytime

# Background process that takes care of syncing
def syncVideoMetadataInBackground():
  latestVideoIds = fetchLatestVideoIds()
  videoModels = buildVideoModels(latestVideoIds)
  builtObjs = VideoModel.objects.bulk_create(videoModels, ignore_conflicts = True)
  print(f'Sync done - added { str(len(builtObjs)) }\n')

'''
  Fetches latest video ids since last fetch time using YouTubeAPI.
  Number of returned ids between 0 & 50 inclusive (50 being maximum limit).
  Params - None
  Returns - List of videoIds
'''
def fetchLatestVideoIds():
  latestVideoIds = []
  lastFetchDateTime = datetime.utcnow().isoformat("T", 'seconds') + "Z"
  try:
    searchParams =  {
      'part': 'snippet',
      'maxResults': settings.SEARCH_LIMIT,
      'order': 'date',
      'type': 'video',
      'publishedAfter': lastFetchDateTime,
      'key': cache.get(settings.CURRENT_API_KEY),
      'q': settings.BASE_SEARCH_TERM
    }  
    if cache.has_key(settings.LAST_DT_KEY):
      lastFetchDateTime = cache.get(settings.LAST_DT_KEY)  
    
    requestObject = requests.get(settings.YOUTUBE_SEARCH_URL, params = searchParams)
    results = requestObject.json()['items']
    for result in results:
      latestVideoIds.append(result['id']['videoId'])    
    
    if not cache.has_key(settings.NEXT_PAGE_TOKEN_KEY):
      cache.set(settings.NEXT_PAGE_TOKEN_KEY, requestObject.json()['nextPageToken'])
    if len(latestVideoIds) <= int(settings.PAGE_LIMIT/2) and cache.has_key(settings.NEXT_PAGE_TOKEN_KEY):
      saveVideosFromNextPage()    
  except Exception as e:
    updateApiKey()
    logger.debug(f'Exception at fetchLatestVideoIds {e.__class__}')
  finally:
    cache.set(settings.LAST_DT_KEY, lastFetchDateTime)
    return latestVideoIds

'''
  Fetches video information of provided video ids using YouTubeAPI and builds VideoModel instances.
  Params - List of videoIds
  Returns - List of VideoModel
'''
# Fetches all videos' metadata with YouTubeAPI and returns list of VideoModel instances
def buildVideoModels(videoIds):
  videoModels = []
  try:
    videoSearchParams = {
      'part': 'snippet,contentDetails',
      'key': cache.get(settings.CURRENT_API_KEY),
      'id': ','.join(videoIds)
    }
    requestObject = requests.get(settings.YOUTUBE_VIDEO_SEARCH_URL, params = videoSearchParams)
    results = requestObject.json()['items']
    for video in results:
      videoModel = VideoModel(
        video_id = video['id'],
        title = video['snippet']['title'],
        description = video['snippet']['description'],
        thumbnail_url = video['snippet']['thumbnails']['high']['url'],
        duration = parse_duration(video['contentDetails']['duration']).total_seconds(),
        published_at = video['snippet']['publishedAt']
      )
      videoModels.append(videoModel)
  except Exception as e:
    updateApiKey()
    logger.debug(f'Exception at buildVideoModels {e.__class__}')
  finally:
    return videoModels

'''
  Saves video information of nextPageToken, if any.
  Params - None
  Returns - None
'''
def saveVideosFromNextPage():
  try:
    videoIds = []
    pageToken = cache.get(settings.NEXT_PAGE_TOKEN_KEY)
    lastFetchDateTime = cache.get(settings.LAST_DT_KEY)
    searchParams =  {
      'part': 'snippet',
      'maxResults': settings.SEARCH_LIMIT,
      'order': 'date',
      'type': 'video',
      'pageToken': pageToken,
      'publishedBefore': lastFetchDateTime,
      'key': cache.get(settings.CURRENT_API_KEY),
      'q': settings.BASE_SEARCH_TERM
    }
    requestObject = requests.get(settings.YOUTUBE_SEARCH_URL, params = searchParams)
    results = requestObject.json()['items']
    for result in results:
      videoIds.append(result['id']['videoId'])
    cache.set(settings.NEXT_PAGE_TOKEN_KEY, requestObject.json()['nextPageToken'])
    videoModels = buildVideoModels(videoIds)
    builtObjs = VideoModel.objects.bulk_create(videoModels, ignore_conflicts = True)
    logger.debug(f'Saved { str(len(builtObjs)) } from page: {pageToken}\n')
  except Exception as e:
    updateApiKey()
    logger.debug(f'Exception at saveVideosFromNextPage  {e.__class__}')

'''
  Returns a list of VideoModels & pagination details as json for given page number and search query (search query is optional).
  Params - pageNumber, seacrhTerm(optional)
  Returns - {videos, totalPages, isNextPageAvailable, isPreviousPageAvailable}
'''
def getVideos(request, pageNumber, searchTerm = ''):
  offset = settings.PAGE_LIMIT * pageNumber
  limit = settings.PAGE_LIMIT + offset  
  allVideoModels = VideoModel.objects.all().order_by('-published_at')
  filteredVideoModels = allVideoModels[offset:limit]
  
  totalPages = ceil(len(allVideoModels)/settings.PAGE_LIMIT)
  isNextPageAvailable = int(len(allVideoModels)/settings.PAGE_LIMIT) > pageNumber
  isPreviousPageAvailable = pageNumber > 0

  if len(searchTerm) > 0:
    searchTerms = searchTerm.split()
    titleSubQuery = reduce(operator.and_, (Q(title__icontains = term) for term in searchTerms))
    descriptionSubQuery = reduce(operator.and_, (Q(description__icontains = term) for term in searchTerms))
    filteredVideoModels = allVideoModels.filter(titleSubQuery | descriptionSubQuery).order_by('-published_at')
    isNextPageAvailable = int(len(filteredVideoModels)/settings.PAGE_LIMIT) > pageNumber
    totalPages = ceil(len(filteredVideoModels)/settings.PAGE_LIMIT)
    filteredVideoModels = filteredVideoModels[offset:limit]

  videos = []
  for videoModel in filteredVideoModels:
    videoData = {}
    videoData['video_id'] = videoModel.video_id
    videoData['title'] = videoModel.title
    videoData['description'] = videoModel.description
    videoData['duration'] = videoModel.getFormattedDuration()
    videoData['thumbnail_url'] = videoModel.thumbnail_url
    videoData['published_at'] = videoModel.getFormattedPublishedAt()
    videoData['video_url'] = videoModel.getVideoWatchUrl()
    videos.append(videoData)

  dataJson = {
    'videos' : videos,
    'totalPages': totalPages,
    'isNextPageAvailable': isNextPageAvailable,
    'isPreviousPageAvailable': isPreviousPageAvailable
  }
  return JsonResponse(dataJson)

def updateApiKey():
  if cache.has_key(settings.CURRENT_API_KEY):
    currentKey = cache.get(settings.CURRENT_API_KEY)
    cache.delete(settings.CURRENT_API_KEY)
    usedKeys = []
    if cache.has_key(settings.USED_APIS_KEY):
      usedKeys = cache.get(settings.USED_APIS_KEY)
    usedKeys.append(currentKey)
    cache.set(settings.CURRENT_API_KEY, usedKeys)
  if not cache.has_key(settings.CURRENT_API_KEY):
    allKeys = settings.YOUTUBE_DATA_API_KEYS
    usedKeys = cache.get(settings.USED_APIS_KEY)
    leftOutKeys = allKeys
    if usedKeys is not None:
      leftOutKeys =list(set(allKeys) - set(usedKeys))
    if len(leftOutKeys) == 0:
      logger.debug(f'Ending sync due to no keys')
      syncJobRef.cancel()
    else :
      currentKey = random.choice(leftOutKeys)
      logger.debug(f'exhausted switching to {currentKey}')
      cache.set(settings.CURRENT_API_KEY, currentKey)