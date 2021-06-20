var currentPage = 0, totalPages = 0, isSearch = false;

$(document).ready(() => {
  $('#input-search').on('input change', function() {
    if($(this).val().trim().length == 0) {
      isSearch = false;
      fetchVideos();
    }
  });
  fetchVideos();
});

function fetchVideos() {
  let url = "/api/videos/page=" + currentPage;
  if(isSearch) {
    url = url + "&query=" + $('#input-search').val().trim();
  }
  $.ajax({
    url: url,
    type: 'GET',
    dataType: 'json',
    success: function(res) {
      totalPages = res.totalPages;
      updatePageNumber();
      if(res.isNextPageAvailable) {
        $('#next-btn').removeAttr('disabled');
      } else {
        $('#next-btn').attr('disabled', 'disabled');
      }
      if(res.isPreviousPageAvailable) {
        $('#previous-btn').removeAttr('disabled');
      } else {
        $('#previous-btn').attr('disabled', 'disabled');
      }
      videos = res.videos;
      $('#empty-message').remove();
      $('#video-list').remove();
      if(videos.length == 0) {
        $('#main-content').append('<span id="empty-message" class="text-muted w-100 mt-4 d-flex justify-content-center">No videos to display!</span>');
      } else {
        $('#main-content').append('<div id="video-list"></div>');
        videos.forEach((video, index) => {
          $('#video-list').append(
            '<div id="video-' + index + '" class="video-item">'
              + '<img class="video-thumbnail" src="' + video.thumbnail_url + '" preserveAspectRatio="xMidYMid slice">'
              + '<div class="video-details">'
                + '<span class="video-title">' + video.title + '</span>'
                + '<div class="d-flex mx-0 align-items-center w-100">'
                  + '<span class="video-duration">'+ video.duration + '</span>'
                  + '<div class="divider-v"></div>'
                  + ' <span class="video-published-at">' + video.published_at + '</span>'
                  + '<a type="button" target="_blank" href="' + video.video_url + '" class="btn btn-primary">Watch</a>'
                +'</div>'
              +'</div>'
            + '</div>'
          );
        });
      }
    }
  });
}

function clearSearch() {
  currentPage = 0;
  isSearch = false;
  $('#input-search').val('').trigger('change');
}

function nextPage() {
  currentPage+=1;
  fetchVideos();
}

function previousPage() {
  currentPage-=1;
  if(currentPage <= 0) { currentPage = 0 };
  fetchVideos();
}

function updatePageNumber() {
  if(totalPages > 0) {
    $('#span-page').html('Page: '+(currentPage+1)+'/'+totalPages);
  } else {
    $('#next-btn').removeAttr('disabled');
    $('#previous-btn').attr('disabled', 'disabled');
    $('#span-page').html('Page: 0/0');
  }
}