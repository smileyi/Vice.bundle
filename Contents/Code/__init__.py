TITLE = 'VICE'
ART   = 'art-default.jpg'
ICON  = 'icon-default.png'

HTTP_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17"

BASE_URL = "http://www.vice.com/en_us"

##########################################################################################
def Start():
	Plugin.AddViewGroup("List", viewMode = "List", mediaType = "items")
	Plugin.AddViewGroup("InfoList", viewMode = "InfoList", mediaType = "items")

	# Setup the default attributes for the ObjectContainer
	ObjectContainer.title1     = TITLE
	ObjectContainer.view_group = "List"
	ObjectContainer.art        = R(ART)

	# Setup the default attributes for the other objects
	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art   = R(ART)
	VideoClipObject.thumb = R(ICON)
	VideoClipObject.art   = R(ART)

	HTTP.CacheTime             = CACHE_1HOUR
	HTTP.Headers['User-agent'] = HTTP_USER_AGENT

##########################################################################################
@handler('/video/vice', TITLE, thumb = ICON, art = ART)
def MainMenu():
	oc = ObjectContainer()
	
	pageElement = HTML.ElementFromURL(BASE_URL + '/shows')
	
	# Add shows by parsing the site
	for item in pageElement.xpath("//*[contains(@class, 'shows_grid_list')]//*[contains(@class, 'story')]"):
		show = {}
		
		try:
			show["url"]  = item.xpath(".//a/@href")[0]
			show["img"]  = item.xpath(".//img/@src")[0]
			show["name"] = item.xpath(".//h2//a/text()")[0]
			show["desc"] = item.xpath(".//p/text()")[0].strip()
		
			oc.add(
				DirectoryObject(
					key = Callback(
							Videos, 
							showTitle = show["name"], 
							url = show["url"], 
							thumb = show["img"]), 
					title = show["name"],
					summary = show["desc"],
					thumb = show["img"]
				)
			)
			
		except:
			pass
	
	if len(oc) < 1:
		oc.header  = "Sorry"
		oc.message = "No shows found."
					 
	return oc
	
##########################################################################################
@route("/video/vice/Videos")
def Videos(showTitle, url, thumb):
	oc = ObjectContainer(title1 = showTitle)
	
	pageElement = HTML.ElementFromURL(BASE_URL + url)
	
	for item in pageElement.xpath("//*[contains(@class, 'story_list')]//*[@class = 'story']"):
		video = {}
		
		try:
			video["url"]  = BASE_URL + item.xpath(".//a/@href")[0]
			video["img"]  = item.xpath(".//img/@src")[0]
			video["name"] = item.xpath(".//h2//a/text()")[0]
			video["desc"] = item.xpath(".//p/text()")[0].strip()

			oc.add(
				EpisodeObject(
					url = video["url"],
					title = video["name"],
					show = showTitle,
					summary = video["desc"],
					thumb = video["img"])
			)
			
		except:
			pass
			 
	return oc
