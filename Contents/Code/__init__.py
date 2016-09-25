######################################################################################
#                                                                                    #
#                           G2G.fm (BY TEHCRUCIBLE) - v0.11                          #
#                                                                                    #
######################################################################################

TITLE = "g2g.fm"
PREFIX = "/video/g2gfm"

ART = "art-default.jpg"
ICON = "icon-default.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_SERIES = "icon-series.png"
ICON_QUEUE = "icon-queue.png"

######################################################################################
def Start():
    """Set global variables"""

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON_COVER)
    DirectoryObject.art = R(ART)

    InputDirectoryObject.thumb = R(ICON_SEARCH)
    InputDirectoryObject.art = R(ART)

    VideoClipObject.thumb = R(ICON_COVER)
    VideoClipObject.art = R(ART)

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'

    ValidatePrefs()

######################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
    """Menu hierarchy"""

    oc = ObjectContainer()
    oc.add(DirectoryObject(
        key=Callback(ShowCategory, title="Movies", category="/movies", href='/movies/index.php?&page=1'),
        title="Movies", thumb=R(ICON_MOVIES)
        ))
    oc.add(DirectoryObject(
        key=Callback(ShowCategory, title="TV Series", category="/tvseries", href='/tvseries/index.php?&page=1'),
        title="TV Series", thumb=R(ICON_SERIES)
        ))
    oc.add(DirectoryObject(
        key=Callback(ShowCategory, title="Latest Episodes", category="/episodes", href='/episodes/index.php?&page=1'),
        title="Latest Episodes", thumb=R(ICON_SERIES)
        ))
    oc.add(DirectoryObject(
        key=Callback(ShowCategory, title="Latest Videos", category="/latest", href='/index.php?show=latest-topics'),
        title="Latest Videos", thumb=R(ICON_MOVIES)
        ))
    oc.add(DirectoryObject(
        key=Callback(GenreMenu, title="Movie Genres"),
        title="Movie Genres", thumb=R(ICON_LIST)
        ))
    oc.add(PrefsObject(title='Preferences'))
    oc.add(InputDirectoryObject(
        key=Callback(Search), title='Search', prompt='Search G2G for...'
        ))

    return oc

######################################################################################
@route(PREFIX + '/validateprefs')
def ValidatePrefs():

    if (Prefs['site_url'] != Dict['site_url']):
        Dict['site_url'] = Prefs['site_url']
        Dict.Save()

    Log.Debug('*' * 80)
    Dict['domain_test'] = 'Fail'
    try:
        HTTP.ClearCookies()
        if 'prx.proxy' in Dict['site_url']:
            proxy = Dict['site_url'].replace('cyro.se.prx.', '') + '/'
            site_url = Dict['site_url'].split('.prx')[0]
            HTTP.Request(proxy, cacheTime=0).load()
            cookies = HTTP.CookiesForURL(proxy)
            r = Regex(r'csrftoken\=([^\;\s\_]+)').search(cookies)
            csrftoken = r.group(1) if r else ''
            values = {'url': site_url, 'csrfmiddlewaretoken': csrftoken}
            try:
                http_headers = {'Cookie': cookies, 'Referer': proxy}
                req = HTTP.Request(proxy, values=values, follow_redirects=False, headers=http_headers, cacheTime=0).load()
                nurl = proxy[:-1]
            except Ex.RedirectError, e:
                nurl = None
                if 'Location' in e.headers:
                    new_url = e.headers['Location']
                    nurl = new_url if not new_url.endswith('/') else new_url[:-1]
                elif 'location' in e.headers:
                    new_url = e.headers['location']
                    nurl = new_url if not new_url.endswith('/') else new_url[:-1]

            if nurl == Dict['site_url']:
                cookies = '; '.join([c.split(';')[0].strip() for c in e.headers['Set-Cookie'].split(',')]) + '; ' + cookies
                HTTP.Headers['Cookie'] = cookies
                Log.Debug('* Cookies set for \'{}\''.format(Dict['site_url']))
                Log.Debug('* Cookies = \'{}\''.format(cookies))
                Dict['domain_test'] = 'Pass'
            else:
                Log.Error(u"* Cannot verify '{0}'".format(proxy))
        else:
            test = HTTP.Request(Dict['site_url'], cacheTime=0).headers
            Log.Debug('* \"%s\" headers = %s' %(Dict['site_url'], test))
            Dict['domain_test'] = 'Pass'
    except:
        Log.Warn(u"* '{0}' is not a valid domain for this channel.".format(Dict['site_url']))
        Log.Warn('* Please pick a different URL')
    Log.Debug('*' * 80)

    Dict.Save()

######################################################################################
def DomainTest():
    """Setup MessageContainer if Dict[\'domain_test\'] failed"""

    if Dict['domain_test'] == 'Fail':
        message = '%s is NOT a Valid Site URL for this channel.  Please pick a different Site URL.'
        return MessageContainer('Error', message %Dict['site_url'])
    else:
        return False

######################################################################################
@route(PREFIX + "/show/category")
def ShowCategory(title, category, href):
    """Creates page url from category and creates objects from that page"""

    if DomainTest() != False:
        return DomainTest()

    oc = ObjectContainer(title1=title)

    html = html_from_url(clean_url(href))

    for m in media_list(html, category):
        if category != '/tvseries':
            oc.add(DirectoryObject(
                key=Callback(EpisodeDetail, title=m['title'], url=m['url']),
                title=m['title'],
                thumb=Callback(get_thumb, url=m['thumb'])
                ))
        else:
            oc.add(DirectoryObject(
                key=Callback(TVShow, title=m['title'], thumb=m['thumb'], url=m['url']),
                title=m['title'],
                thumb=Callback(get_thumb, url=m['thumb'])
                ))

    nhref = next_page(html)
    if nhref:
        oc.add(NextPageObject(
            key=Callback(ShowCategory, title=title, category=category, href=nhref),
            title="More...",
            thumb=R(ICON_NEXT)
            ))

    if len(oc) != 0:
        return oc

    c = 'TV Series' if category == '/tvseries' else category[1:].title()
    return MessageContainer('Warning', '%s Category Empty' %c)

######################################################################################
@route(PREFIX + "/show")
def TVShow(title, thumb, url):
    """Return episode list if no season info, otherwise return season info"""

    if DomainTest() != False:
        return DomainTest()

    oc = ObjectContainer(title1=title)

    html = html_from_url(clean_url(url))

    info_node = html.xpath('//div[@id="nameinfo"]')
    if info_node:
        new_thumb = html.xpath('//img[@id="nameimage"]/@src')
        thumb = clean_url(new_thumb[0]) if new_thumb else thumb

        text_block = info_node[0].text_content()
        r = Regex(r'(?i)(season\s(\d+))').findall(text_block)
        if r:
            for season, i in r:
                oc.add(DirectoryObject(
                    key=Callback(SeasonDetail, title=season.title(), season=int(i), thumb=thumb, url=url),
                    title=season.title(),
                    thumb=Callback(get_thumb, url=thumb)
                    ))
        else:
            episode_list(oc, info_node, thumb)

    if len(oc) != 0:
        return oc

    return MessageContainer('Warning', 'No Show(s) Found')

######################################################################################
def episode_list(oc, node, thumb, season=None):
    anode = node[0].xpath('./a')
    for i, a in enumerate(anode):
        href = a.get('href')
        if season:
            if int(href.rsplit('/', 2)[1][1:]) == season:
                etitle = a.text_content()
            else:
                continue
        else:
            try:
                s = node[0].xpath('./span')[i]
                etitle = a.text_content() + ' ' + s.text_content()
            except:
                etitle = a.text_content()

        oc.add(DirectoryObject(
            key=Callback(EpisodeDetail, title=etitle, url=href),
            title=etitle,
            thumb=Callback(get_thumb, url=thumb)
            ))
    return

######################################################################################
@route(PREFIX + '/show/season', season=int)
def SeasonDetail(title, season, thumb, url):

    if DomainTest() != False:
        return DomainTest()

    oc = ObjectContainer(title1=title)

    html = html_from_url(clean_url(url))

    info_node = html.xpath('//div[@id="nameinfo"]')
    if info_node:
        episode_list(oc, info_node, thumb, season)

    if len(oc) != 0:
        return oc

    return MessageContainer('Warning', 'No Episode(s) found for Season %i Found' %season)

######################################################################################
@route(PREFIX + "/episode/detail")
def EpisodeDetail(title, url):
    """
    Gets metadata and google docs link from episode page.
    Checks for trailer availablity.
    """

    if DomainTest() != False:
        return DomainTest()

    oc = ObjectContainer(title1=title)

    try:
        html = html_from_url(clean_url(url))
    except Exception as e:
        Log.Critical('* EpisodeDetail Error: %s' %str(e))
        message = 'This media has expired.' if ('HTTP Error' in str(e) and '404' in str(e)) else str(e)
        return MessageContainer('Warning', message)

    ptitle = html.xpath("//title/text()")[0].rsplit(" Streaming",1)[0].rsplit(" Download",1)[0]
    thumb = html.xpath('//img[@id="nameimage"]/@src')
    thumb = (thumb[0] if thumb[0].startswith('http') else clean_url(thumb[0])) if thumb else None

    wpm = html.xpath('//iframe[@id="wpm"]/@src')
    if not wpm:
        return MessageContainer('Warning', 'No Video Source Found.')

    pass_html = html_from_url(clean_url(wpm[0]))
    video_urls = []
    source_iframe = pass_html.xpath('//iframe/@src')
    if source_iframe:
        part = 0
        if pass_html.xpath('//div[starts-with(@id, "part")]'):
            part = 1

        try:
            video_urls.append((part, html_from_url(clean_url(source_iframe[0])).xpath('//iframe/@src')[0]))
        except Exception as e:
            Log.Error('* EpisodeDetail Error: %s' %str(e))
            pass

        if part != 0:
            base_iframe = source_iframe[0].split('.php')[0]
            count = 1
            more = True
            while more and (count < 5):
                count += 1
                try:
                    video_urls.append((count, html_from_url(clean_url(base_iframe + '%i.php' %count)).xpath('//iframe/@src')[0]))
                except Exception as e:
                    Log.Warn('* EpisodeDetail Warning: %s' %str(e))
                    more = False

        cleaned_video_urls = list()
        for p, u in sorted(video_urls):
            if 'prx.proxy' in u:
                u = 'https://docs.google.com/file/' + u.split('/file/')[1]
            cleaned_video_urls.append((p, u))

        vurl="g2g://" + E(JSON.StringFromObject({"title": ptitle, "urls": cleaned_video_urls, "thumb": thumb}))
        try:
            mdo = URLService.MetadataObjectForURL(vurl)
            mdo.thumb=Callback(get_thumb, url=thumb)
            mdo.title=ptitle
            oc.add(mdo)
        except:
            Log.Exception("Error creating MetadataObjectForURL('{}') >>>".format(vurl))
            oc.header = "Warning"
            oc.message = u"Media Offline for '{}'".format(ptitle)

        #oc.add(VideoClipObject(
            #title=ptitle,
            #thumb=Callback(get_thumb, url=thumb),
            #url="g2g://" + E(JSON.StringFromObject({"title": ptitle, "urls": cleaned_video_urls, "thumb": thumb}))
            #))

    trailpm = html.xpath('//iframe[@id="trailpm"]/@src')
    if trailpm:
        thtml = html_from_url(clean_url(trailpm[0]))
        yttrailer = thtml.xpath('//iframe[@id="yttrailer"]/@src')
        if yttrailer:
            yttrailer_url = yttrailer[0] if yttrailer[0].startswith('http') else 'https:' + yttrailer[0]
            if 'prx.proxy' in yttrailer_url:
                yttrailer_url = 'http://www.youtube.com/embed/' + yttrailer_url.split('/embed/')[1]
            oc.add(VideoClipObject(url=yttrailer_url, thumb=R(ICON_SERIES), title="Watch Trailer"))

    if len(oc) != 0:
        return oc

    return MessageContainer('Warning', 'No Media Found')

######################################################################################
@route(PREFIX + "/genre/menu")
def GenreMenu(title):
    """Displays movie genre categories"""

    if DomainTest() != False:
        return DomainTest()

    oc = ObjectContainer(title1=title)

    html = html_from_url(clean_url('/movies/genre.php?showC=27'))
    for m in media_list(html, '/movies', genre=True):
        oc.add(DirectoryObject(
            key=Callback(ShowCategory, title=m['title'], category='/movies', href=m['url']),
            title=m['title'],
            thumb=Callback(get_thumb, url=m['thumb'])
            ))

    if len(oc) != 0:
        return oc

    return MessageContainer('Warning', 'No Genre(s) Found')

######################################################################################
@route(PREFIX + "/search", page=int)
def Search(query='', page=1):
    if DomainTest() != False:
        return DomainTest()

    query = query.strip()
    url = clean_url('/search.php?dayq=%s&page=%i' %(String.Quote(query, usePlus=True), page))

    oc = ObjectContainer(title1='Search for \"%s\"' %query)

    html = html_from_url(url)
    for m in media_list(html, '/search'):
        oc.add(DirectoryObject(
            key=Callback(EpisodeDetail, title=m['title'], url=m['url']),
            title=m['title'],
            thumb=Callback(get_thumb, url=m['thumb'])
            ))

    nhref = next_page(html)
    if nhref:
        oc.add(NextPageObject(
            key=Callback(Search, query=query, page=page+1),
            title="More...",
            thumb=R(ICON_NEXT)
            ))

    if len(oc) != 0:
        return oc

    return MessageContainer('Warning', 'Oops! No results were found. Please try a different word.')

######################################################################################
def media_list(html, category, genre=False):
    """didn't want to write this over-and-over again"""

    info_list = list()
    for each in html.xpath("//td[@class='topic_content']"):
        eid = int(Regex(r'goto\-(\d+)').search(each.xpath("./div/a/@href")[0]).group(1))
        if category == '/latest' or category == '/search':
            url = clean_url("/view.php?id=%i" %eid)
        else:
            url = clean_url("%s/view.php?id=%i" %(category, eid))

        thumb = each.xpath("./div/a/img/@src")[0]
        thumb = thumb if thumb.startswith('http') else clean_url(thumb)

        title = thumb.rsplit("/",1)[1].rsplit("-",1)[0] if genre else each.xpath("./div/a/img/@alt")[0]

        info_list.append({'title': title, 'thumb': thumb, 'url': url})

    return info_list

######################################################################################
def next_page(html):
    """Seperated out next page code just in case"""

    nhref = False
    next_page_node = html.xpath('//a[contains(@href, "&page=")][text()=">"]/@href')
    if next_page_node:
        nhref = next_page_node[0]

    return nhref

######################################################################################
def html_from_url(url):
    """pull down fresh content when site URL changes"""

    if Dict['site_url'] != Dict['site_url_old']:
        Dict['site_url_old'] = Dict['site_url']
        Dict.Save()
        HTTP.ClearCache()
        HTTP.Headers['Referer'] = Dict['site_url']

    return HTML.ElementFromURL(url)

######################################################################################
def clean_url(href):
    """handle href/URL variations and set corrent Site URL"""

    if href.startswith('http') or href.startswith('//'):
        url = Dict['site_url'] + '/' + href.split('/', 3)[-1]
    else:
        url = Dict['site_url'] + (href if href.startswith('/') else '/' + href)

    return url

######################################################################################
@route(PREFIX + '/get_thumb')
def get_thumb(url, fallback_icon=None, fallback_url=None):
    if 'prx.proxy' in url:
        r = HTTP.Request(url, immediate=True, method='GET')
        if r:
            img_data = r.content
            if img_data:
                ext = '.'+url.rsplit('.', 1)[1]
                mime_type = {
                    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
                    '.gif': 'image/gif',  '.tiff': 'image/tiff', '.bmp': 'image/bmp'
                    }.get(ext, '*/*')

                return DataObject(img_data, mime_type)
            else:
                Log.Error(u'* No image data for \'{}\''.format(url))
        else:
            Log.Error(u'* Cannot access \'{}\''.format(url))
    elif url:
        return Redirect(url)

    if fallback_icon:
        return Redirect(R(fallback_icon))
    elif fallback_url:
        return Redirect(fallback_url)

    return Redirect(R(ICON_COVER))
