# -*- coding: utf-8 -*-

# xbmc modules
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
# os and lib modules
import os
import sys 
import urllib
import urllib2
import re
# print_exc
from traceback import print_exc  
# parseDOM
import CommonFunctions
common = CommonFunctions
common.plugin = "plugin.video.D8"

__addonID__         = "plugin.video.D8"
__author__          = "JUL1EN094"
__date__            = "10-10-2014"
__version__         = "1.0.6"
__credits__         = ""
__addon__           = xbmcaddon.Addon( __addonID__ )
__settings__        = __addon__
__language__        = __addon__.getLocalizedString
__addonDir__        = __settings__.getAddonInfo( "path" )

# Global Variable
ROOTDIR             = __settings__.getAddonInfo('path')
BASE_RESOURCE_PATH  = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH          = os.path.join( BASE_RESOURCE_PATH, "media" )
ADDON_DATA          = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
CACHEDIR            = os.path.join( ADDON_DATA, "cache")
THUMB_CACHE_PATH    = os.path.join( xbmc.translatePath( "special://profile/" ), "Thumbnails", "Video" )
WEBROOT             = "http://www.d8.tv"
WEBSITE             = WEBROOT + "/replay"
WEBLIVEONGLET       = "http://www.d8.tv/lib/front_tools/ajax/d8/d8_live_onglet.php"
CANAL_VIDEOINFO_URL = "http://service.canal-plus.com/video/rest/getVideosLiees/"        
WEBLIVE             = "http://www.d8.tv/pid5323-d8-live.html"
FANART_PATH         = os.path.join( ROOTDIR, "fanart.jpg" )       
# List of directories to check at startup
dirCheckList        = (CACHEDIR,)


class D8:
    """
    main plugin class
    """
    debug_mode = False # Debug mode
    
    def __init__( self, *args, **kwargs ):
        print "==============================="
        print "  D8 - Version: %s"%__version__
        print "==============================="
        print
        self.set_debug_mode()
        if self.debug_mode:
            print "Python version:"
            print sys.version_info
            print "ROOTDIR: %s"%ROOTDIR
            print "ADDON_DATA: %s"%ADDON_DATA
            print "CACHEDIR: %s"%CACHEDIR  
        params    = self.get_params()
        url       = None
        name      = None
        mode      = None
        iconimage = ''            
        try:
            url=urllib.unquote_plus(params["url"])
        except:
            pass
        try:
            name=urllib.unquote_plus(params["name"])
        except:
            pass
        try:
            mode=int(params["mode"])
        except:
            pass
        try:
            iconimage=urllib.unquote_plus(params["iconimage"])
        except:
            pass            
        if self.debug_mode:
            print "D8 addon : Mode      -> "+str(mode)
            print "D8 addon : URL       -> "+str(url)
            print "D8 addon : Name      -> "+str(name)
            print "D8 addon : Iconimage ->  "+str(iconimage)
 
        # Check if directories in user data exist
        for i in range(len(dirCheckList)):
            self.checkfolder(dirCheckList[i]) 
    
        if mode==None or url==None or len(url)<1:
            if self.debug_mode:
                print "D8 addon : GET_CATEGORIES("+WEBROOT+")"
            self.GET_CATEGORIES(WEBROOT)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
                            
        elif mode==1:
            if self.debug_mode:
                print "D8 addon : GET_EPISODES D8("+url+","+iconimage+")"
            self.GET_EPISODES_D8(url,iconimage,name)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))

        elif mode==2:
            if self.debug_mode:
                print "D8 addon : GET_EMISSIONS : "+url 
            self.GET_EMISSIONS(url)         
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
                    
        elif mode==3:
            if self.debug_mode:
                print "D8 addon : GET_EMISSIONS_DIR("+url+","+iconimage+")"
            self.GET_EMISSIONS_DIR(url,iconimage)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            
        elif mode==4:
            if self.debug_mode:
                print "D8 addon : GET_EPISODES CANAL("+url+","+iconimage+")"
            self.GET_EPISODES_CANAL(url,iconimage)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            
        elif mode==5:
            if self.debug_mode:
                print "D8 addon : PLAY_VIDEO"
            VID_cplus = re.findall("""CANAL PLUS : VID=(.*)""",url)
            VID_d8    = re.findall("""D8 : VID=(.*)""",url)
            VID_live  = re.findall("""LIVE : VID=(.*)""",url)
            if VID_cplus :
                VID = VID_cplus[0]
                print "D8 addon : vid -> "+VID
                video_url = self.GET_VIDEO_CANAL(VID,'cplus/')
            elif VID_d8 :
                VID = VID_d8[0]
                print "D8 addon : vid -> "+VID
                video_url = self.GET_VIDEO_CANAL(VID,'d8/')
            elif VID_live :
                VID = VID_live[0]
                print "D8 addon : vid -> "+VID
                video_url = self.GET_VIDEO_CANAL(VID,'d8/',live=True)
            item = xbmcgui.ListItem(path=video_url) 
            xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=item)

        elif mode==100:
            if self.debug_mode:
                print "D8 addon : GET_LIVE"
            self.GET_LIVE(url)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
        
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_LABEL)

    def GET_CATEGORIES(self,url):
        soup           = self.get_soup(url) 
        html           = soup.decode("iso-8859-1")
        cssn_mainnav_s = common.parseDOM(html,"nav",attrs={"id":"nav","class":u"cssn_mainnav"})
        if cssn_mainnav_s :
            cssn_mainnav = cssn_mainnav_s[0]
            links         = re.findall(u"""<a href="(.*)">(.*)</a>""",cssn_mainnav)
        if links:
            for anchor in links :
                if self.debug_mode:
                    print "D8 addon : categorie -> "+anchor[1].encode("utf-8")
                self.addDir(anchor[1].encode("utf-8"),WEBROOT+(anchor[0].encode("utf-8")),2,"")
        self.addDir('Live',WEBLIVE,100,"")

    def GET_EMISSIONS(self,url):
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        soup       = self.get_soup(url)
        html       = soup.decode("iso-8859-1")
        replay_box = common.parseDOM(html,"div",attrs={"class":u"block-common block-mozaic-programme"})
        for item in replay_box :
            blockcom_illu   = common.parseDOM(item,"a",attrs={"class":u"blockcom-illu parent-cglow parent-fil-mign"},ret="href")[0]
            emission_url    = WEBROOT+(blockcom_illu.encode("utf-8"))
            if self.debug_mode :
                print "D8 addon : emission url   -> "+emission_url
            emission_image  = common.parseDOM(item,"img",ret="src")[0]
            if self.debug_mode :
                print "D8 addon : emission image -> "+emission_image
            emission_titre  = common.parseDOM(item,"h3",attrs={"class":u"bkcc-title bkcc-title-solo a-ch"})[0].encode("utf-8")
            if self.debug_mode :
                print "D8 addon : emission titre -> "+emission_titre
            emission_plot_s = common.parseDOM(item,"p")            
            if emission_plot_s :
                emission_plot = emission_plot_s[0].replace("<br />","\n").replace("<strong>","").replace("</strong>","").encode("utf-8")
            else :
                emission_plot = ''
            if self.debug_mode :
                print "D8 addon : emission plot  -> "+str(emission_plot)
            info            = {'Title':emission_titre,'Plot':emission_plot}
            self.addDir(emission_titre,emission_url,3,emission_image,info)
  
    def GET_EMISSIONS_DIR(self,url,iconimage=''):    # Olala mal de crâne!!
        soup            = self.get_soup(url)
        html            = soup.decode("iso-8859-1")
        ## Ex Direct8 -> migrated Canal
        try :                                     
            cssnt_tabs_clic = common.parseDOM(html,"ul",attrs={"class":u"cssnt-tabs-clic"}) [0]
            li_s            = common.parseDOM(cssnt_tabs_clic,"li")
            for li in li_s :
                titre = common.parseDOM(li,"h3")[0]
                print 'D8 addon : '+str(titre.encode('utf-8'))
                if re.search('Vid.+os?',titre.encode('utf-8'),re.IGNORECASE) or re.search('Live',titre.encode('utf-8'),re.IGNORECASE): 
                    epiCat_s        = common.parseDOM(html,'li',attrs={'id':'liste','class':'current'})
                    if len(epiCat_s)>1 :
                        for epiCat in epiCat_s :
                            print 'D8 addon : '+str(epiCat.encode('utf-8'))
                            titre  = common.parseDOM(epiCat,'h3',attrs={'class':'onglet-title'})[0]
                            self.addDir(titre.encode("utf-8"),url,1,iconimage)
                    else :
                        self.addDir(titre.encode("utf-8"),url,1,iconimage)
        ## CANAL PLUS original style
        except:
            canalplus_list = common.parseDOM(html,"div",attrs={"id":"canalplus"})
            if canalplus_list :                    
                print 'D8 addon : CANALPLUS1'
                canalplus = canalplus_list [0]
                mainSection_pattern = common.parseDOM(canalplus,"div",attrs={"id":"mainSection"}) [0]
                button_plus_pattern = common.parseDOM(mainSection_pattern,"p",attrs={"class":u"button-plus"})
                for item in button_plus_pattern :
                    link = re.findall(u"""<a href="(.*)">(.*)</a>""",item) [0]
                    if link[1].encode("utf-8").endswith("""outes les vidéos""") :
                        web_url_base       = re.findall(u"""<meta property="og:site_name" content="(.*)"/>""",html) [0]
                        web_url            = "http://"+web_url_base.encode("utf-8")+link[0].encode("utf-8")
                        episodes_list_soup = self.get_soup(web_url)
                        episodes_list_html = episodes_list_soup.decode("iso-8859-1")
                        tabs_subtabs       = common.parseDOM(episodes_list_html,"ul",attrs={"class":u"tabs subtabs"}) [0]
                        print "TAB :"+tabs_subtabs.encode("utf-8")
                        tabs_list          = common.parseDOM(tabs_subtabs,"li")
                        for tabs in tabs_list :
                            print tabs.encode("utf-8")
                            tabs_name    = common.parseDOM(tabs,"span")[0]
                            if (tabs_name!=u'Commentaires') and (tabs_name!=u'A propos') and (tabs_name!=u'Concept') and (tabs_name!=u'Commentez') : 
                                tabs_url_end = common.parseDOM(tabs,"a",ret="href") [0]
                                tabs_url     = "http://"+web_url_base.encode("utf-8")+tabs_url_end.encode("utf-8")
                                self.addDir(tabs_name.encode("utf-8"),tabs_url,4,iconimage)
            else : 
                dessous_s = common.parseDOM(html,'li',attrs={'class':'dessous'})
                print 'D8 addon : CANALPLUS2'
                for item in dessous_s :
                    print item.encode('utf-8')
                    item_url   = common.parseDOM(item,'a',ret='href')[0]
                    if item_url[:4]!= 'http' :
                        item_url = WEBROOT + item_url
                    item_image_s = common.parseDOM(item,'img',ret='src')
                    if item_image_s : 
                        item_image = item_image_s[0]
                    else :
                        item_image = ''
                    try :
                        item_name    = common.parseDOM(item,'a')[1].encode('utf-8')
                    except :
                        item_name    = common.parseDOM(item,'a')[0].encode('utf-8')
                    print 'D8 addon : image -> '+str(item_image)
                    print 'D8 addon : name  -> '+str(item_name)
                    print 'D8 addon : url   -> '+str(item_url)
                    self.addDir(item_name,item_url,1,item_image)

    def GET_EPISODES_D8(self,url,fanartimage,name):
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        soup              = self.get_soup(url)
        html              = soup.decode("iso-8859-1")
        epiCat_s          = common.parseDOM(html,'li',attrs={'id':'liste','class':'current'})
        url_allitem_end = ""
        pid    = re.findall('data-pid=\'([0-9]+)\'',html)[0]
        ztid   = re.findall('data-ztidOnglet=\'([0-9]+)\'',html)[0]
        onglet = re.findall('data-iOnglet=\'([0-9]+)\'',html)[0]
        print 'D8 addon : PID ' +str(pid)
        print 'D8 addon : ZTID ' +str(ztid)
        print 'D8 addon : ONGLET ' +str(onglet)
        plus_video_s      = common.parseDOM(html,"a",attrs={"id":"btn-plus-video_[0-9]"},ret="onclick")
        if plus_video_s :
            n = 0
            while (n < len(epiCat_s)) :
                url_allitem_end += "&nbPlusVideos"+str(n)+"=20"
                n += 1
        url_allitem = WEBLIVEONGLET+"?pid="+str(pid)+"&ztid="+str(ztid)+"&onglet="+str(onglet)+url_allitem_end
        print 'D8 addon : URL : '+ url_allitem
        xml_allitem = self.get_soup(url_allitem)
        xml         = xml_allitem.decode("iso-8859-1")
        print 'D8 addon : '+str(xml.encode('utf-8'))
        epiCat_s = common.parseDOM(xml,'li',attrs={'id':'liste','class':'current'})
        Items    = ''
        if len(epiCat_s)>1 :
            for epiCat in epiCat_s :
                titre = common.parseDOM(epiCat,'h3',attrs={'class':'onglet-title'})[0]
                if titre.encode('utf-8') == name :
                    Items = epiCat
        if len(Items)==0 :
            Items = epiCat_s[0]
        li_s = common.parseDOM(Items,'li')
        for li in li_s :
            print "D8 addon : LI : "
            print li.encode("utf-8")
            episode_url   = common.parseDOM(li,"a",ret="href")[0]
            episode_url   = re.findall("""\?vid=(.*)""",episode_url) [0]
            episode_url   = "D8 : VID="+episode_url.encode("utf-8")
            if self.debug_mode :
                print "D8 addon : episode url   -> "+str(episode_url)
            episode_name  = common.parseDOM(li,"h3")[0].encode("utf-8")
            detail        = common.parseDOM(li,'div',attrs={'class':'lv-details'})
            if detail :
                episode_name = '%s - [I]%s[/I]' %(episode_name,detail[0].encode("utf-8"))
            if self.debug_mode :
                print "D8 addon : episode name  -> "+str(episode_name)
            try :
                episode_image = re.findall("""style=\"background-image: url\((.*)\)""",li)[0]
            except :
                episode_image = re.findall("""style=\"background-image: url\(\'(.*)\'\)""",li)[0]
            if self.debug_mode :
                print "D8 addon : episode image -> "+str(episode_image)
            self.addLink(episode_name,episode_url,5,episode_image,fanart=fanartimage)                
                    
    def GET_EPISODES_CANAL(self,url,fanartimage):
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        soup                 = self.get_soup(url)
        html                 = soup.decode("iso-8859-1")
        div_content_pattern  = common.parseDOM(html,"div",attrs={"class":u"tabs_content"}) [0]
        unit_gallery_li      = common.parseDOM(div_content_pattern,"ul",attrs={"class":u"unit-gallery2"}) 
        if unit_gallery_li :
            target_pattern = unit_gallery_li [0]
            episode_list_pattern = common.parseDOM(target_pattern,"li")
            for episode_pattern in episode_list_pattern :
                if episode_pattern.encode("utf-8") != "" :                
                    image_episode_pattern = common.parseDOM(episode_pattern,"img", ret="src") [0]
                    image_episode         = image_episode_pattern.encode("utf-8")
                    if self.debug_mode :
                        print "image_episode : "+str(image_episode)
                    msH4_txt_pattern      = common.parseDOM(episode_pattern,"div",attrs={"class":u"msH4 txt "}) [0]
                    emission_name_pattern = common.parseDOM(msH4_txt_pattern,"a") [0]
                    emission_name         = emission_name_pattern.encode("utf-8")
                    p_pattern             = common.parseDOM(episode_pattern,"p") [0]
                    episode_name_pattern  = common.parseDOM(p_pattern,"a") [0]
                    episode_name          = episode_name_pattern.encode("utf-8")
                    episode_name_full     = emission_name+" : "+episode_name
                    if self.debug_mode :
                        print "episode_name_full : "+str(episode_name_full)
                    episode_url_pattern   = common.parseDOM(p_pattern,"a",ret="href") [0]
                    episode_url           = re.findall("""\?vid=(.*)""",episode_url_pattern) [0]
                    episode_url           = "CANAL PLUS : VID="+episode_url
                    if self.debug_mode :
                        print "episode_url : "+str(episode_url)
                    self.addLink(episode_name_full,episode_url,5,image_episode,fanart=fanartimage)
        elif not unit_gallery_li :
            target_pattern_list = common.parseDOM(div_content_pattern,"li") 
            if target_pattern_list :
                target_pattern = target_pattern_list [0]
                episode_list_pattern = common.parseDOM(target_pattern,"li")
                for episode_pattern in episode_list_pattern :
                    print "PATERN :"+episode_pattern.encode("utf-8")
                    image_episode_pattern = common.parseDOM(episode_pattern,"img", ret="src") [0]
                    image_episode         = image_episode_pattern.encode("utf-8")
                    if self.debug_mode :
                        print "image_episode : "+str(image_episode)                    
                    emission_name_pattern    = common.parseDOM(episode_pattern,"h4",ret="title") [0]
                    emission_name         =  emission_name_pattern.encode("utf-8")
                    p_pattern             = common.parseDOM(episode_pattern,"p") [0]
                    episode_name_pattern  = common.parseDOM(p_pattern,"a") [0]
                    episode_name          =  episode_name_pattern.encode("utf-8")
                    episode_name_full     = emission_name+" : "+episode_name
                    if self.debug_mode :
                        print "episode_name_full : "+str(episode_name_full)
                    episode_url_pattern   = common.parseDOM(p_pattern,"a",ret="href") [0]
                    episode_url           = re.findall("""\?vid=(.*)""",episode_url_pattern) [0]
                    episode_url           = "CANAL PLUS : VID="+episode_url
                    if self.debug_mode :
                        print "episode_url : "+str(episode_url)                                        
                    self.addLink(episode_name_full,episode_url,5,image_episode,fanart=fanartimage)                    
        paginator_pattern = common.parseDOM(div_content_pattern,"ul",attrs={"class":u"paginator-table paginator-table-alt pagination_ms  "})
        if paginator_pattern : #Plusieurs pages
            next_even_pattern = common.parseDOM(paginator_pattern,"li",attrs={"class":u"next"}) [0]
            if next_even_pattern.encode("utf-8") != "" :
                next_url_end  = common.parseDOM(next_even_pattern,"a",ret="href") [0]
                next_url_base = re.findall(u"""<meta property="og:site_name" content="(.*)"/>""",html) [0]
                next_url      = "http://"+next_url_base.encode("utf-8")+next_url_end.encode("utf-8")
                self.GET_EPISODES_CANAL(next_url,fanartimage) # !!Recursive

    def GET_LIVE(self,url):
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        soup              = self.get_soup(url)
        html              = soup.decode("iso-8859-1")
        #print html.encode("utf-8") 
        live_url = common.parseDOM(html,"input",attrs={"type":u"hidden","id":"iVideoEnCours"}, ret="value")[0]
        live_url = "LIVE : VID="+live_url
        live_name = "D8 - Direct"
        if self.debug_mode :
            print "Live_url :"+live_url
        self.addLink(live_name,live_url,5,'','')
    
    def GET_VIDEO(self,url):
        player_vod_js_url = self.get_player_vod_js(url) 
        video_url         = self.get_video_url(player_vod_js_url)
        return video_url 
        
    def GET_VIDEO_CANAL(self,vid,canal,live=False):
        soup      = self.get_soup(CANAL_VIDEOINFO_URL+canal+vid)
        xml       = soup.decode("utf-8")
        video_s = common.parseDOM(xml,"VIDEO")
        for video in video_s :
            id = common.parseDOM(video,'ID') [0]
            if str(id) == str(vid) :
                try :
                    if live :
                        video_url = common.parseDOM(video,"IPAD")[0]
                    else :
                        video_url = common.parseDOM(video,"HLS")[0]
                except :
                    video_url = common.parseDOM(video,"HAUT_DEBIT")[0]
                return video_url                                                          
          
    def set_debug_mode(self):
        debug =__settings__.getSetting('debug')
        if debug == 'true':
            self.debug_mode = True
        else:
            self.debug_mode = False
        print "D8: debug Mode:"
        print self.debug_mode        
        
    def addLink(self,name,url,mode,iconimage,info={},fanart=FANART_PATH):
        u  =sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok =True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty( "Fanart_Image", fanart)
        ok =xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok         

    def addDir(self,name,url,mode,iconimage,info={},fanart=FANART_PATH):
        if info == {} :
            info = {"Title":name}
        u  =sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok =True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels=info  )
        liz.setProperty( "Fanart_Image", fanart)
        ok =xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
    
    def get_params(self):
        param      =[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
            params         =sys.argv[2]
            cleanedparams  =params.replace('?','')
            if (params[len(params)-1]=='/'):
                params     =params[0:len(params)-2]
            pairsofparams  =cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                splitparams={}
                splitparams=pairsofparams[i].split('=')
                if (len(splitparams))==2:
                    param[splitparams[0]]=splitparams[1]
        return param

    def get_soup(self,url):
        req  = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/15.0.1')           
        req.add_header('Referer',url)
        soup = urllib2.urlopen(req).read()
        if (self.debug_mode):
            print str(soup)
        return soup

    def get_player_vod_js(self,url):
        soup                      = self.get_soup(url)
        html                      = soup.decode("utf-8")
        main_container_pattern    = common.parseDOM(html,"div",attrs={"class":"main_container"}) [0]
        video_div_pattern         = common.parseDOM(main_container_pattern,"div", attrs={"id":u"video"}) [0]
        content_block_pattern     = common.parseDOM(video_div_pattern,"div",attrs={"class":u"content-block"}) [0]
        player_vod_js_url_pattern = common.parseDOM(content_block_pattern,"script",ret="src") [1]
        player_vod_js_url         = player_vod_js_url_pattern.encode("utf-8")
        if self.debug_mode :
            print "Javascript URL : "+player_vod_js_url
        return player_vod_js_url 

    def get_video_url(self,url):
        soup             = self.get_soup(url)
        html             = soup.decode("utf-8")
        base_url_pattern = re.findall("""baseUrl:..*'(.*)',""",html) [0]
        if base_url_pattern:
            base_url         = base_url_pattern.encode("utf-8")
            if self.debug_mode :
                print "baseURL :"+base_url
            filename_pattern = re.findall("""url.*:.*'(.*)'""",html) [0]
            if filename_pattern :
                filename  = filename_pattern.encode("utf-8")
                if self.debug_mode :
                    print "filename :"+filename
                video_url = base_url+filename
                if self.debug_mode :
                    print "video_url : "+video_url
                return video_url  
                    
    def checkfolder(self,folder):
        try:
            if not os.path.exists(folder):
                print "checkfolder Impossible to find the directory - trying to create the directory: "+folder
                os.makedirs(folder)
        except Exception, e:
            print "Exception while creating folder "+folder
            print str(e)

    def clean_thumbnail(self,video_url):
        try:
            filename = xbmc.getCacheThumbName(video_url)
            filepath = xbmc.translatePath(os.path.join(THUMB_CACHE_PATH,filename[0],filename))
            if os.path.isfile(filepath):
                os.remove(filepath)
                if self.debug_mode:
                    print "Deleted %s thumb matching to %s video"%(filepath,video_url)
            elif self.debug_mode:
                print "No thumb found %s thumb matching to %s video"%(filepath,video_url)
            return True
        except:
            print "Error: clean_thumbnail()"
            print_exc()
            return False  
                
                                     
                                           

#######################################################################################################################    
# BEGIN !
#######################################################################################################################

if ( __name__ == "__main__" ):
    try:
        D8()
    except:
        print_exc()