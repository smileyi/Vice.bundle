TITLE = 'VICE'
ART   = 'art-default.jpg'
ICON  = 'icon-default.png'

HTTP_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17"

BASE_URL = "http://www.vice.com"

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
    
    pageElement = HTML.ElementFromURL(BASE_URL + '/en_us/shows')
    
    # Add shows by parsing the site
    for item in pageElement.xpath("//*[contains(@class, 'all-shows')]//*[contains(@class, 'items-container')]//li"):        
        try:
            url = item.xpath(".//a/@href")[0]
            
            if not '/series/' in url:
                continue
                
            if not url.startswith('http'):
                url = BASE_URL + url
            
            title = item.xpath(".//a/text()")[0].strip()
        
            oc.add(
                DirectoryObject(
                    key = 
                        Callback(
                            Episodes, 
                            showTitle = title, 
                            url = url
                        ), 
                    title = title
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
def Episodes(showTitle, url):
    oc = ObjectContainer(title2 = showTitle)
    
    pageElement = HTML.ElementFromURL(url)
    
    for item in pageElement.xpath("//*[contains(@class, 'items-container')]//*[@class = 'item']"): 
        link = item.xpath(".//a/@href")[0]
        
        if not link.startswith('http'):
            link = BASE_URL + link
        
        title = item.xpath(".//*[@class='item-title']//a/text()")[0].strip()
        
        try:
            thumb = 'http:' + item.xpath(".//noscript//img/@src")[0]
        except:
            thumb = R(ICON)
        
        try:
            summary = item.xpath(".//*[@class='item-description']//a/text()")[0].strip()
        except:
            summary = None
            
        try:
            originally_available_at = Datetime.ParseDate(item.xpath(".//*[@class='publish-time']/@data-publish-date")[0].split(" ")[0]).date()
        except:
            originally_available_at = None
            
        try:
            duration = item.xpath(".//*[@class='video-duration']//p/text()")[0]
            duration = (int(duration.split(":")[0]) * 60 + int(duration.split(":")[1])) * 1000
        except:
            duration = None
        
        if ('-part-' in link or '-episode' in link) and not ' part ' in title.lower():
            oc.add(
                DirectoryObject(
                    key =
                        Callback(
                            Parts,
                            showTitle = showTitle,
                            url = link,
                            title = title,
                            thumb = thumb,
                            summary = summary
                        ),
                    title = title,
                    thumb = thumb,
                    summary = summary
                )
            )
        else:
            oc.add(
                EpisodeObject(
                    url = link,
                    title = title,
                    show = showTitle,
                    summary = summary,
                    thumb = thumb,
                    originally_available_at = originally_available_at,
                    duration = duration
                )
            )
             
    return oc

##########################################################################################
@route("/video/vice/Parts")
def Parts(showTitle, url, title, thumb, summary):
    oc = ObjectContainer(title2 = showTitle)

    pageElement = HTML.ElementFromURL(url)
        
    try:
        summary = pageElement.xpath("//*[@name='description']/@content")[0].strip()
    except:
        pass

    for item in pageElement.xpath("//*[@class='more-parts-container']//li"):
        try:
            link = item.xpath(".//a/@href")[0]
        except:
            continue
        
        if not link.startswith("http"):
            link = BASE_URL + link
            
        title = item.xpath(".//a/text()")[0].strip()

        oc.add(
            EpisodeObject(
                url = link,
                title = title,
                show = showTitle,
                thumb = thumb,
                summary = summary
            )
        )
        
    return oc