from django.db import models
from datetime import datetime, timezone, date
import pytz

class VideoModel(models.Model):
  video_id = models.CharField(primary_key=True, max_length=500)
  title = models.CharField(max_length=500)
  description = models.TextField(blank=True, null=True)
  thumbnail_url = models.CharField(max_length=100, blank=True, null=True)
  duration = models.BigIntegerField()
  published_at = models.DateTimeField()

  # Gets whole video url
  def getVideoWatchUrl(self):
    return f'https://www.youtube.com/watch?v={ self.video_id }'

  # Formats duration to proper representation
  def getFormattedDuration(self):
    durationInSeconds = int(self.duration)
    duartionInMinutes = int(durationInSeconds // 60)
    durationInHours = int(duartionInMinutes // 60)
    if durationInHours > 1:
      return str(durationInHours) + " hrs"
    elif durationInHours == 1:
      return str(durationInHours) + " hr"
    else:
      if duartionInMinutes > 1:
        return str(duartionInMinutes) + " mins"
      elif duartionInMinutes == 1:
        return str(duartionInMinutes) + " min"
      else:
        return str(durationInSeconds) + " secs"
    return ""

  # Formats published_at to proper representation
  def getFormattedPublishedAt(self):
    currentDate = date.today()
    parsedDateTime = datetime.strptime(str(self.published_at), "%Y-%m-%d %H:%M:%S%z")
    
    daysDiff = int((currentDate.day - parsedDateTime.date().day))
    monthsDiff = int((currentDate.month - parsedDateTime.date().month))
    yearsDiff = int((currentDate.year - parsedDateTime.date().year))

    if yearsDiff > 1:
      return str(yearsDiff)+ " years ago"
    elif yearsDiff == 1:
      return str(yearsDiff)+ " year ago"
    else:
      if monthsDiff > 1:
        return str(monthsDiff)+ " months ago"
      elif monthsDiff == 1:
        return str(monthsDiff)+ " month ago"
      else:
        if daysDiff > 1:
          return str(daysDiff)+ " days ago"
        elif daysDiff == 1:
          return str(daysDiff)+ " day ago"
        else:
          currentDateTime = datetime.now(pytz.utc)
          durationDiffInSeconds = (currentDateTime - parsedDateTime).total_seconds()
          diffInHours = int(divmod(durationDiffInSeconds, 3600)[0])
          if diffInHours <= 1:
            return "Less than an hour ago"
          else :
            return str(diffInHours)+ " hours ago"