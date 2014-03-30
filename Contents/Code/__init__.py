TITLE = 'VICE'
ART   = 'art-default.jpg'
ICON  = 'icon-default.png'

HTTP_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17"

BASE_URL = "http://www.vice.com/en_us"

##########################################################################################
def Start():
	# Setup the default attributes for the ObjectContainer
	ObjectContainer.title1 = TITLE
	ObjectContainer.art    = R(ART)

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
			show["url"] = item.xpath(".//a/@href")[0]
			
			if ' ' in show["url"]:
				continue
			
			show["img"]  = item.xpath(".//img/@src")[0]
			show["name"] = item.xpath(".//h2//a/text()")[0]
			show["desc"] = ''.join(item.xpath(".//p/text()")).strip()
		
			oc.add(
				DirectoryObject(
					key = Callback(
							Episodes, 
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
@route("/video/vice/Episodes")
def Episodes(showTitle, url, thumb):
	oc = ObjectContainer(title1 = showTitle)
	
	pageElement = HTML.ElementFromURL(BASE_URL + url)
	
	for item in pageElement.xpath("//*[contains(@class, 'story_list')]//*[@class = 'story']"):
		episode = {}
		
		try:
			link            = item.xpath(".//a/@href")[0]
			episode["url"]  = BASE_URL + link
			episode["img"]  = item.xpath(".//img/@src")[0]
			episode["name"] = item.xpath(".//h2//a/text()")[0]
			episode["desc"] = ''.join(item.xpath(".//p/text()")).strip()
			
			if ('-part-' in link or '-episode' in link) and not ' part ' in episode["name"].lower():
				oc.add(
					DirectoryObject(
						key =
							Callback(
								Parts,
								showTitle = showTitle, 
								url = episode["url"],
								title = episode["name"],
								thumb = episode["img"]
							),
						title = episode["name"],
						thumb = episode["img"],
						summary = episode["desc"]
					)
				)
			else:
				oc.add(
					EpisodeObject(
						url = episode["url"],
						title = episode["name"],
						show = showTitle,
						summary = episode["desc"],
						thumb = episode["img"]
					)
				)
			
		except:
			pass
			 
	return oc

##########################################################################################
@route("/video/vice/Parts")
def Parts(showTitle, url, title, thumb):
	oc = ObjectContainer(title1 = showTitle)

	pageElement = HTML.ElementFromURL(url)

	try:
		title = pageElement.xpath("//*[@class='episode-title']/text()")[0].strip()
	except:
		pass
		
	oc.add(
		EpisodeObject(
			url = url,
			title = title,
			show = showTitle,
			thumb = thumb
		)
	)

	for item in pageElement.xpath("//*[@class='related_videos']//*[@id='yw2']//*[@class='item']"):
		part = {}
		
		try:
			link         = item.xpath(".//a/@href")[0]
			part["url"]  = BASE_URL + link
			part["img"]  = item.xpath(".//img/@src")[0]
			part["name"] = item.xpath(".//h3/text()")[0]

			oc.add(
				EpisodeObject(
					url = part["url"],
					title = part["name"],
					show = showTitle,
					thumb = part["img"]
				)
			)
		except:
			pass
	
	oc.objects.sort(key = lambda obj: obj.title)
		
	return oc