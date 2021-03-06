#
# TODO:
# Scrub global variables for unneeded stuff
# Port HD Content Archive
# Photo items (Image of the Day) don't display
# Audio podcast playback
# Official NASA TV channel icons are horrendous
# NASA TV Mobile channel hangs

import re,string
import random

####################################################################################################

NASA_VIDEO_PREFIX       = "/video/nasa"
NASA_AUDIO_PREFIX       = "/music/nasa"
NASA_PHOTO_PREFIX       = "/photos/nasa"

NASA_URL                = "http://www.nasa.gov"
RSS_INDEX               = "http://www.nasa.gov/rss/index.html"
# PODCAST_INDEX           = "http://www.nasa.gov/multimedia/podcasting/index.html"
# VIDEO_GALLERY           = "http://www.nasa.gov/multimedia/videogallery/index.html"
# MOST_WATCHED            = "http://www.nasa.gov/templateimages/redesign/baynote/mostwatched/baynotejs.js"
VIDEO_ARCHIVES          = "http://www.nasa.gov/multimedia/videogallery/Video_Archives_Collection_archive_1.html"
# NASA_TV                 = "http://www.nasa.gov/multimedia/nasatv/index.html"
NASA_IMAGE_OF_THE_DAY   = "http://www.nasa.gov/multimedia/imagegallery/iotdxml.xml"

RSS_VIDEO_URL           = "http://www.nasa.gov/rss/%s_videos.xml"
USTREAM_CHANNEL_URL     = "http://www.ustream.tv/channel/%s"
NASA_SINGLE_VID_URL     = "http://www.nasa.gov/multimedia/videogallery/index.html?media_id=%s"
VMIX_JSON_URL           = "http://cdn-api.vmixcore.com/apis/media.php?action=getMediaList&class_id=1&get_count=1&order_method=DESC&order=date_published_start&start=%s&limit=15&metadata=1&alltime=1&external_genre_ids=131&export=JSONP&atoken=cf15596810c05b64c422e071473549f4"

NASA_ONDEMAND           = 'http://www.nasa.gov/multimedia/nasatv/on_demand_video.html?param='

MEDIA_NAMESPACE         = {'media':'http://search.yahoo.com/mrss/'}
ITUNES_NAMESPACE        = {'itunes':'http://www.itunes.com/dtds/podcast-1.0.dtd'}

IMAGE_COUNT             = 20 # Number of images to display on a page

DEBUG_XML_RESPONSE      = False
CACHE_RSS               = 3200
CACHE_GALLERY           = CACHE_RSS
CACHE_ARCHIVES          = CACHE_RSS
CACHE_NASATV            = CACHE_RSS
CACHE_RSS_INDEX         = 72000
CACHE_PHOTO_METADATA    = 691200

ART = "art-default.jpg"
ICON = "icon-default.png"
SEARCH = "icon-search.png"

#USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5"

####################################################################################################

def Start():

  # Plugin.AddPrefixHandler(NASA_VIDEO_PREFIX, MainMenuVideo, L('nasa'), ICON, ART)
  # Plugin.AddPrefixHandler(NASA_AUDIO_PREFIX, MainMenuAudio, L('nasa'), ICON, ART)
  # Plugin.AddPrefixHandler(NASA_PHOTO_PREFIX, MainMenuPhoto, L('nasa'), ICON, ART)

  #Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  # Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  # Plugin.AddViewGroup("Pictures", viewMode="Pictures", mediaType="photos")

  ObjectContainer.title1 = L("nasa")
  ObjectContainer.art = R(ART)
  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  VideoClipObject.thumb = R(ICON)
  VideoClipObject.art = R(ART)
  
####################################################################################################

# def UpdateCache():

#   HTTP.Request(RSS_INDEX, cacheTime=CACHE_RSS_INDEX)


####################################################################################################

@handler(NASA_VIDEO_PREFIX, L('nasa'))

def MainMenu():
  oc = ObjectContainer()
  oc.add(DirectoryObject(key=Callback(NASATV), title=L('nasatv') + ' - ' + L('live_channels')))
  oc.add(DirectoryObject(key=Callback(FeaturedContent, feature='recent'), title=L('recent')))
  oc.add(DirectoryObject(key=Callback(FeaturedVideoMenu), title=L('featured')))
  oc.add(DirectoryObject(key=Callback(PodcastChooser, mediaType='video'), title=L('podcasts')))
  # dir.Append(Function(DirectoryObject(HDContent, title=L('HD'))))
  oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.nasa", title="Search...", prompt="Search NASA for...", thumb=R(SEARCH), art=R(ART)))
  
  return oc

####################################################################################################

@handler(NASA_AUDIO_PREFIX, L('nasa'))

def MainMenuAudio():

  return PodcastChooser(mediaType='audio')

####################################################################################################

@handler(NASA_PHOTO_PREFIX, L('nasa'))

def MainMenuPhoto():
  oc = ObjectContainer()
  oc.add(DirectoryObject(key=Callback(ImageOfTheDay, order='mostrecent'), title=L('recent_photos')))
  oc.add(DirectoryObject(key=Callback(ImageOfTheDay, order='random'), title=L('random')))

  return oc

  # dir.Append(Function(DirectoryObject(ImageOfTheDay, title=L('mostrecent')), order='mostrecent'))
  # dir.Append(Function(DirectoryObject(ImageOfTheDay, title=L('random')), order='random'))

  # return dir


####################################################################################################
  
def FeaturedVideoMenu():
  oc = ObjectContainer()
  oc.add(DirectoryObject(key=Callback(FeaturedContent, feature='recent'), title=L('recent')))
  oc.add(DirectoryObject(key=Callback(FeaturedContent, feature='popular'), title=L('popular')))
  oc.add(DirectoryObject(key=Callback(FeaturedContent, feature='top_rated'), title=L('top_rated')))
  
  return oc

####################################################################################################

def PodcastChooser(mediaType):
  oc = ObjectContainer(title2=L('podcasts'))
  
  page = HTML.ElementFromURL(RSS_INDEX, cacheTime=CACHE_RSS_INDEX)

  if mediaType == 'video':
    xpath = '//table//td[position()=2]/a'
  else:
    xpath = '//table//td[position()=4]/a'

  for feed in page.xpath(xpath):
    url = NASA_URL + feed.get('href')
    title = feed.xpath("./../preceding-sibling::td")[0].text
    title = title.strip()
    podcast = RSS.FeedFromURL(url, cacheTime=CACHE_RSS)
    thumb = podcast.feed.image.href

    # if mediaType == 'video' and 'This Week @NASA' in title:
    #   # Skip this podcast for now -- PMS doesn't like it (possibly due to bad MIME type from server)
    #   pass
    # else:
    oc.add(DirectoryObject(key=Callback(PodcastEpisodes, title=title, url=url), title=title, thumb=Callback(Thumb, url=thumb)))
    
  return oc

    # We use the image from the podcast as the thumbnail, storing it in the dictionary after the first time
    # if not ('podthumb-'+url) in Dict:
    #   Dict['podthumb-'+url] = thumb
    # else:
    #   thumb = Dict['podthumb-'+url]

    #dir.Append(Function(DirectoryObject(PodcastEpisodes, title=title, thumb=thumb), title=title, url=url))

  # dir.Append(Function(DirectoryObject(OtherPodcastChooser, title=L('otherpodcasts'))))
  # return dir

####################################################################################################

def PodcastEpisodes(title, url):
  # Shows available episodes in the selected podcast

  Log('Listing PodcastEpisodes for URL: ' + url)

  podcast = XML.ObjectFromURL(url, cacheTime=CACHE_RSS)

  try:
    t2 = podcast.xpath('/rss/channel/').get('title')
  except:
    t2 = title

  oc = ObjectContainer(title1=L('podcasts'), title2=t2)    

  try:  
    thumb = podcast.xpath('/rss/channel/itunes:image', namespaces=ITUNES_NAMESPACE).get('href')
  except:
    thumb = R(ICON)
  
  for entry in podcast.xpath('//rss/channel/item'):
    title = entry.xpath('./title')[0].text
    url = entry.xpath('./enclosure')[0].get('url')
    try:
     summary = HTML.ElementFromString(entry.description)[0].text_content()
    except:
      summary = ''
    try:
      date = Datetime.ParseDate(entry.date).strftime('%a %b %d, %Y')
    except:
      date = None
    
    # Durations appear to be bogus on these items...
    # try:
    #   duration = int(entry.enclosures[0].length)
    # except:
    #   duration = 0

    duration = 0
    
    if (url.count('mp3') > 0) :
      oc.add(TrackObject(url=url, title=title, summary=summary, duration=duration, thumb=thumb))
    else:
      # if 'This Week @ NASA' in title:
      #   # Skip this podcast for now -- PMS doesn't like it (possibly due to bad MIME type from server)
      #   pass
      # else:
      oc.add(VideoClipObject(url=url, title=title, summary=summary, duration=0, thumb=thumb))

  return oc

####################################################################################################

def FeaturedContent(feature, pg=0):
  oc = ObjectContainer(title2=L(feature))
  
  if feature == 'recent':
    json = JSON.ObjectFromURL(VMIX_JSON_URL % str(pg * 15))
    for item in json['media']:
      oc.add(VideoClipObject(
                 url = NASA_SINGLE_VID_URL % item['id'],
                 title = item['title'],
                 summary = item['description'],
                 thumb = Callback(Thumb, url=item['thumbnail'][0]['url'])
              ))
    oc.add(DirectoryObject(key=Callback(FeaturedContent, feature='recent', pg=pg+1), title=L('more_recent')))
  
  else:
    rss = XML.ElementFromURL(RSS_VIDEO_URL % feature)
    for item in rss.xpath('//item'):
      oc.add(VideoClipObject(
              url=item.xpath('./link')[0].text,
              title = item.xpath('./title')[0].text, 
              summary = item.xpath('./description')[0].text, 
              thumb = Callback(Thumb, url=item.xpath('./image')[0].text),
              duration = int(item.xpath('./duration')[0].text)*1000
              ))

  return oc

####################################################################################################

def Archives(sender, url=VIDEO_ARCHIVES, pageNumber=1):

  dir = ObjectContainer(replaceParent = True)
  if pageNumber == 1:
    dir.title2 = L('archives')
  else:
    dir.title1 = L('archives')
    dir.title2 = L('page') + " " + str(pageNumber)

  page = HTML.ElementFromURL(url, cacheTime=CACHE_ARCHIVES)

  videos = page.xpath("//div[@id='browseArchive']/ul/li")
  
  if pageNumber != 1:
    prevPageUrl = NASA_URL + page.xpath("//a[@class='archive_backward']")[0].get('href')
    dir.Append(Function(DirectoryObject(Archives, title=L('previouspage')), url=prevPageUrl, pageNumber=str(int(pageNumber) - 1)))

  for video in videos:

    title = video.xpath("./h3/a")[0].text
    thumb = video.xpath(".//img")[0].get('src')
    if thumb.count(NASA_URL) == 0: 
      thumb = NASA_URL + thumb
    summary = video.xpath("./p")[0].text
    urlJS = video.xpath("./a")[0].get('href')
    try:
      url = re.search (r"(http://[^']+)'", urlJS).group(1)
    except:
      url = NASA_ONDEMAND + re.search (r"\('([^']+)'", urlJS).group(1)
    #Log(url)
    
    if (url.count('asx') > 0) :
      dir.Append(WindowsMediaVideoClipObject(url, title=title, summary=summary, duration=str(0), thumb=thumb))
    else:
      dir.Append(VideoClipObject(url, title=title, summary=summary, duration=str(0), thumb=thumb))

  # Check for next page link

  nextPageUrl = NASA_URL + page.xpath("//a[@class='archive_forward']")[0].get('href')
  lastPageUrl = NASA_URL + page.xpath("//a[@class='archive_end']")[0].get('href')
  if nextPageUrl != lastPageUrl:
    pageNumber = str(int(pageNumber) + 1)
    dir.Append(Function(DirectoryObject(Archives, title=L('nextpage')), url=nextPageUrl, pageNumber=pageNumber))

  return dir

####################################################################################################

def NASATV():

  oc = ObjectContainer(title2=L('nasatv'))

  oc.add(URLService.MetadataObjectForURL(USTREAM_CHANNEL_URL % 'nasa-hd-tv'))
  oc.add(URLService.MetadataObjectForURL(USTREAM_CHANNEL_URL % 'live-iss-stream'))
  oc.add(URLService.MetadataObjectForURL(USTREAM_CHANNEL_URL % 'nasa-educational'))
  oc.add(URLService.MetadataObjectForURL(USTREAM_CHANNEL_URL % 'nasa-media-channel'))
  # The mobile stream is hanging both rtmpdump and PMS, so I'm commenting it out for now.
  # oc.add(URLService.MetadataObjectForURL(USTREAM_CHANNEL_URL % 'nasa-mobile'))
  return oc

####################################################################################################

def ImageOfTheDay(order, start=0):
  oc = ObjectContainer(title2=L(order))

  xml = XML.ElementFromURL(NASA_IMAGE_OF_THE_DAY, cacheTime = 0)
  all_images = xml.xpath("//ig")
  #images = []

  if order == 'random':
    images = random.sample(all_images, IMAGE_COUNT)
  else:
    images = all_images[start:IMAGE_COUNT]

  # We need to pull the meta data for each image, for speed lets thread it
  result = {}
  @parallelize
  def GetImagesMetadata():
    
    for num in range(len(images)):
      image = images[num]      
      
      @task
      def GetImageMetadata(num=num, result=result, image=image):
        metadata_url = NASA_URL + image.xpath('./ap')[0].text + '.xml'
        metadata = XML.ElementFromURL(metadata_url, cacheTime = CACHE_PHOTO_METADATA)
        thumbnail_url = NASA_URL + metadata.xpath("//gallery_main")[0].text
        description = StripHTML(metadata.xpath("//channel/description")[0].text, paragraphsToNewLines=True)
        title = metadata.xpath('//channel/title')[0].text
        fullsize_url = NASA_URL + metadata.xpath('//size[contains(type, "Full_Size")]/href')[0].text
        #Log('fullsize url -----> ' + fullsize_url)
        result[num] = PhotoObject(url=fullsize_url, title=title, summary=description, thumb=thumbnail_url)

  keys = result.keys()
  keys.sort()

  for key in keys:
    oc.add(result[key])

  return oc  

####################################################################################################

def StripHTML(stringToStrip,paragraphsToNewLines=False):
  # Srips HTML tags from a string
  if paragraphsToNewLines:
    stringToStrip = re.sub(r'<\s*/p>', r'\n\n', stringToStrip)
  stringToStrip = re.sub(r'<[^>]*>', r'', stringToStrip)
  return stringToStrip

####################################################################################################

def Thumb(url):
  if url:
    try:
      data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
      return DataObject(data, 'image/jpeg')
    except:
      return Redirect(R('icon-default.png'))
  return None



##########################################################################################
#
#  TODO and other junk below here
#


# def HDContent(sender, page = None, pagenum = 0):
    
#   dir = ObjectContainer(replaceParent = (pagenum!=0))
#   if page == None:
#     if pagenum == 0:
#       page = 'http://www.nasa.gov/multimedia/hd/index.html'
#     else:
#       dir.Append(Function(DirectoryObject(HDContent,title="Previous Page"),pagenum = pagenum-1))

#       page = 'http://www.nasa.gov/multimedia/hd/HDGalleryCollection_archive_%s.html'%pagenum
      
#   content = HTML.ElementFromURL(page)
#   for c in content.xpath("//div[@id='hdgallery']"):
#     url = c.xpath("li//a")[0].get("href")
#     title = c.xpath("li//h3")[0].text
#     thumb = 'http://www.nasa.gov/' + c.xpath("li//img")[0].get("src")
#     if url.endswith('.html') == True:
#       dir.Append(Function(DirectoryObject(HDContent,title=title,thumb=thumb),page = 'http://www.nasa.gov'+url))
#     else:
#       dir.Append(VideoClipObject(url,title=title,thumb=thumb))
#       for url in c.xpath("parent::li//a/img"):
#          dir.Append(VideoClipObject(url.get('href'),title="    "+url.xpath('./img')[0].get('title'),thumb=thumb))
  
#   if pagenum == 0:
#     dir.Append(Function(DirectoryObject(HDContent,title='HD Archives'),pagenum = 1))
#   else:
#     if pagenum < 5:
#       dir.Append(Function(DirectoryObject(HDContent,title='Next Page'),pagenum = pagenum+1))

#   return dir 
  
# def ParseJSON(sender = None, url= None, pagenum = 0, total_pages = 5, videos_per_page = 15):
#   dir = ObjectContainer(replaceParent = (pagenum>0))

#   if (pagenum >0):
#     dir.Append(Function(DirectoryObject(ParseJSON,title='Previous Page'),url = url,pagenum = pagenum-1))

#   jsondata = JSON.ObjectFromURL(url%((total_pages*videos_per_page),(pagenum*videos_per_page)))
#   for item in jsondata['media']:
#     Log(item['token'])
#     dir.Append(Function(VideoClipObject(GetVideoFromToken,title=item['title'], thumb=item['thumbnail'][0]['url'],duration=int(item['duration'])*1000),token=item['token']))

#   if (pagenum <total_pages):
#     dir.Append(Function(DirectoryObject(ParseJSON,title='Next Page'),url = url,pagenum = pagenum+1))
  
#   return dir   
  
# def SearchContent(sender, query = None):
 
#   url = 'http://cdn-api.vmixcore.com/apis/media.php?action=searchMedia&export=JSONP&atoken=cf15596810c05b64c422e071473549f4&fields=title,description&limit=%s&start=%s&query='+query
#   return ParseJSON(url=url)








# def OtherPodcastChooser(sender):
#   # List podcasts in the Other NASA Podcasts section

#   dir = ObjectContainer()
#   dir.title1=L('podcasts')
#   dir.title2=L('otherpodcasts')

#   page = HTML.ElementFromURL(PODCAST_INDEX, cacheTime=CACHE_RSS_INDEX)

#   feeds = page.xpath("//h2[text()='Other NASA Podcasts']/..//div[@id='ullitags']//a")

#   for feed in feeds:
#     # We ignore 'hd' feeds as no one could stream them fast enough in testing (server too slow...)
    
#     url = feed.get('href')
    
#     #prophylactic
#     if url.count('/irrelevant')>0 :
#       url = "http://spitzer.caltech.edu/resource_list/4-IRrelevant-Astronomy?format=xml"
      
#     title = feed.text
#     if title.count('HD') > 0 or title.count('Spanish') > 0: # The spanish link is not a podcast
#       continue 
#     title = title[2:len(title)] # Remove first 2 characters - The bullet marks
#     title = title.strip()
#     if not ('podthumb-'+url) in Dict:
#       podcast = RSS.FeedFromURL(url, cacheTime=CACHE_RSS)
#       try:
#         thumb = podcast.feed.image.href
#       except:
#         thumb = R(ICON)
#       Dict['podthumb-'+url] = thumb
#     else:
#       thumb = Dict['podthumb-'+url]
#     dir.Append(Function(DirectoryObject(PodcastEpisodes, title=title, thumb=thumb), title=title, url=url))

#   return dir


# def GetVideoFromToken(sender,token):
#       HTTP.Request('http://cdn-media.vmixcore.com/vmixcore/play/uvp?token=%s&player_name=unified_video_player&output=xml'%token)
#       Element = XML.ElementFromURL('http://cdn-media.vmixcore.com/vmixcore/play/uvp?token=%s&player_name=unified_video_player&output=xml'%token) 
#       smil = Element.xpath('//play_url')[0].text
#       height = Element.xpath('//height')[0].text
#       width = Element.xpath('//width')[0].text
#       return Redirect (VideoClipObject(smil,width = width,height = height))
