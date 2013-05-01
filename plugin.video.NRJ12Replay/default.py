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
# pyamf
from pyamf.remoting.client import RemotingService
# parseDOM
import CommonFunctions
common = CommonFunctions
common.plugin = "plugin.video.NRJ12Replay"



__addonID__      = "plugin.video.NRJ12Replay"
__author__       = "JUL1EN094 ,vilain_mamuth"
__date__         = "18-02-2013"
__version__      = "2.0.3"
__credits__      = "Merci aux auteurs des autres addons replay du dépôt Passion-XBMC et de la communauté open-source"
__addon__        = xbmcaddon.Addon( __addonID__ )
__settings__     = __addon__
__language__     = __addon__.getLocalizedString
__addonDir__     = __settings__.getAddonInfo( "path" )   

# Global Variable
ROOTDIR             = __settings__.getAddonInfo('path')
BASE_RESOURCE_PATH  = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH          = os.path.join( BASE_RESOURCE_PATH, "media" )
ADDON_DATA          = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
CACHEDIR            = os.path.join( ADDON_DATA, "cache")
THUMB_CACHE_PATH    = os.path.join( xbmc.translatePath( "special://profile/" ), "Thumbnails", "Video" )

# Web variable
WEBROOT = "http://www.nrj12.fr"
WEBSITE = WEBROOT + "/replay-4203/collectionvideo/"        
INFOSITE = "http://prod-kernnrj12v5.integra.fr/videoinfo"        
 
# List of directories to check at startup
dirCheckList        = (CACHEDIR,) 

class NRJ12Replay:
    """
    main plugin class
    """
    debug_mode = False # Debug mode
    
    def __init__( self, *args, **kwargs ):
        print "==============================="
        print "  NRJ12 Replay - Version: %s"%__version__
        print "==============================="
        print
        self.set_debug_mode()
        if self.debug_mode:
            print "Python version:"
            print sys.version_info    
        params  = self.get_params()
        url     = None
        name    = None
        mode    = None            
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
        if self.debug_mode:
            print "Mode: "+str(mode)
            print "URL: "+str(url)
            print "Name: "+str(name)
            
        # Check if directories in user data exist
        for i in range(len(dirCheckList)):
            self.checkfolder(dirCheckList[i])           
    
        if mode==None or url==None or len(url)<1:
            if self.debug_mode:
                print "GET_CATEGORIES("+WEBSITE+")"
            self.addDir(__language__(30051).encode("utf-8"),"All_Episodes",1,"")
            self.GET_CATEGORIES(WEBSITE)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
 
                            
        elif mode==1:
            if self.debug_mode:
                print "GET_ALL_EPISODES("+WEBSITE+")"
            self.GET_ALL_EPISODES(WEBSITE)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
 
        elif mode==2:
            if self.debug_mode:
                print "GET_EMISSIONS("+WEBSITE+","+url+")"
            self.GET_EMISSIONS(WEBSITE,url)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
                     
        elif mode==3:
            if self.debug_mode:
                print "GET_EPISODES("+WEBSITE+","+url+")"
            self.GET_EPISODES(WEBSITE,url)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
             
        elif mode==4:
            if self.debug_mode:
                print "PLAY_VIDEO"
            url_video = self.PLAY_VIDEO(url)
            item = xbmcgui.ListItem(path=url_video)
            xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=item)

        
               

    def GET_CATEGORIES(self,url):
        soup = self.get_soup(url)
        links = re.findall(u"""nocursor">(.*)</a>""",soup)
        if links:
            for cat in links :
                cat = str(cat)
                if self.debug_mode:
                    print "catégorie :"+cat
                self.addDir(cat,cat,2,"")

    def GET_EMISSIONS(self,url,cat):
        soup = self.get_soup(url)
#         soup = soup.split("""<div id="content"   >""")
#         soup = soup[1]
#         soup = soup.split("""<div class="line most-view""")
#         soup = soup[0]
        html = soup.replace('\xe9', 'e').replace('\xe0', 'a').decode("utf-8")
        line_replay_s = common.parseDOM(html,"div",attrs={"class":"line replay"})
        for line_replay in line_replay_s :
            Categorie = common.parseDOM(line_replay,"a",attrs={"class":"nocursor"}) [0]
            if Categorie.encode("utf-8") == cat:
                print "linereplay : "+line_replay.encode("utf-8")
                li_s = common.parseDOM(line_replay,"li",attrs={"id":u"*"})
                for li in li_s :
                    replay_hover_s = common.parseDOM(li,"div",attrs={"class":u"replay_hover"})
                    if replay_hover_s :
                        image_div = common.parseDOM(li,"div",attrs={"class":"image"}) [0]
                        image_a_u = common.parseDOM(image_div,"a") [0]
                        image_url = re.findall(""".*src="(.*)">""",image_a_u) [0]
                        titre_p   = common.parseDOM(li,"p",attrs={"class":"titre"}) [0]
                        titre_u   = common.parseDOM(titre_p,"a") [0]
                        titre     = titre_u.encode("utf-8")
                        if self.debug_mode :
                            print "Nom : "+titre,"url : "+titre,"Mode : 3","image : "+image_url 
                        self.addDir(titre,titre,3,image_url)
                    else :
                        image_div   = common.parseDOM(li,"div",attrs={"class":"image"}) [0]
                        image_a_u   = common.parseDOM(image_div,"a") [0]
                        image_url   = re.findall(""".*src="(.*)">""",image_a_u) [0]
                        titre_p     = common.parseDOM(li,"p",attrs={"class":"titre"}) [0]
                        titre_u     = common.parseDOM(titre_p,"a") [0]
                        titre       = titre_u.encode("utf-8")
                        video_url_u = common.parseDOM(titre_p,"a",ret="href") [0]
                        video_url   = video_url_u.encode("utf-8")
                        if self.debug_mode :
                            print "Nom : "+titre,"url : "+video_url,"Mode : 3","image : "+image_url 
                        self.addLink(titre,video_url,4,image_url)
                    
    def GET_EPISODES(self,url,emission):
        soup = self.get_soup(url)
#         soup = soup.split("""<div id="content"   >""")
#         soup = soup[1]
#         soup = soup.split("""<div class="line most-view""")
#         soup = soup[0]
        html = soup.replace('\xe9', 'e').replace('\xe0', 'a').decode("utf-8")
        line_replay_s = common.parseDOM(html,"div",attrs={"class":"line replay"})
        for line_replay in line_replay_s :
            print "linereplay : "+line_replay.encode("utf-8")
            li_s = common.parseDOM(line_replay,"li",attrs={"id":u"*"})
            for li in li_s :
                replay_hover_s = common.parseDOM(li,"div",attrs={"class":u"replay_hover"})
                if replay_hover_s :
                    titre_p   = common.parseDOM(li,"p",attrs={"class":"titre"}) [0]
                    titre_u   = common.parseDOM(titre_p,"a") [0]
                    titre     = titre_u.encode("utf-8")
                    if titre == emission:
                        self.get_titres(emission,li)  
    
    def GET_ALL_EPISODES(self,url):
        soup = self.get_soup(url)
#         soup = soup.split("""<div id="content"   >""")
#         soup = soup[1]
#         soup = soup.split("""<div class="line most-view""")
#         soup = soup[0]
        html = soup.replace('\xe9', 'e').replace('\xe0', 'a').decode("utf-8")
        line_replay_s = common.parseDOM(html,"div",attrs={"class":"line replay"})
        for line_replay in line_replay_s :
            li_s = common.parseDOM(line_replay,"li",attrs={"id":u"*"})
            for li in li_s :
                titre_p   = common.parseDOM(li,"p",attrs={"class":"titre"}) [0]
                titre_u   = common.parseDOM(titre_p,"a") [0]
                titre     = titre_u.encode("utf-8")
                self.get_titres(titre,li)    
    
    def PLAY_VIDEO(self,url):
        mediaId   = self.get_mediaId(url)
        url_video = self.get_episode_url(INFOSITE,mediaId)
        return url_video

    def set_debug_mode(self):
        debug =__settings__.getSetting('debug')
        if debug == 'true':
            self.debug_mode = True
        else:
            self.debug_mode = False
        print "NRJ2 Replay: debug Mode:"
        print self.debug_mode        
        
    def addLink(self,name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok         

    def addDir(self,name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
    
    def get_params(self):
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                splitparams={}
                splitparams=pairsofparams[i].split('=')
                if (len(splitparams))==2:
                    param[splitparams[0]]=splitparams[1]
        return param

    def get_soup(self,url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/15.0.1')           
        soup = urllib2.urlopen(req).read()
        if (self.debug_mode):
            print str(soup)
        return soup   
        
    def get_mediaId(self,url) :
        if (url.startswith("http://")):
            html = self.get_soup(url)
        else:
            html = self.get_soup(WEBROOT + url)
        mediaIdList = re.findall('mediaId_(.*?)"',html)
        if mediaIdList :
            mediaId = mediaIdList[0]
            if self.debug_mode: 
                print "mediaId : "+mediaId
            return mediaId
            
    def get_episode_url(self,url,Id):
        client = RemotingService(url)
        vi = client.getService('Nrj_VideoInfos')
        mi = vi.mediaInfo(Id)
        if self.debug_mode:
            print "url_episode : "+mi["url"]
        url_episode = mi["url"]
        return url_episode 
            
    def get_emission(self,liste):
        emission = re.findall("""title="(.*)".*</a>""",liste)
        if emission:
            emission = emission[0]     
            if self.debug_mode:
                print "emission :"+emission
            return emission   
            
    def get_titres(self,emission,liste):
        replay_hover_s = common.parseDOM(liste,"div",attrs={"class":u"replay_hover"})
        if replay_hover_s :
            replay_hover = replay_hover_s[0]
            content_ul   = common.parseDOM(replay_hover,"ul",attrs={"class":"content"}) [0]
            li_s         = common.parseDOM(content_ul,"li")
            for li in li_s :
                print li.encode("utf-8")
                image_div   = common.parseDOM(li,"div",attrs={"class":"image"}) [0]
                image_a_u   = common.parseDOM(image_div,"a") [0]
                image_url   = re.findall(""".*src="(.*)".*>""",image_a_u) [0]
                titre_p     = common.parseDOM(li,"p",attrs={"class":"titre"}) [0]
                titre_u     = common.parseDOM(titre_p,"a") [0]
                titre       = emission+" : "+titre_u.encode("utf-8")
                video_url_u = common.parseDOM(titre_p,"a",ret="href") [0]
                video_url   = video_url_u.encode("utf-8")
                if self.debug_mode :
                    print "Nom : "+titre,"url : "+video_url,"Mode : 3","image : "+image_url 
                self.addLink(titre,video_url,4,image_url)
        else :
            image_div   = common.parseDOM(liste,"div",attrs={"class":"image"}) [0]
            image_a_u   = common.parseDOM(image_div,"a") [0]
            image_url   = re.findall(""".*src="(.*)">""",image_a_u) [0]
            titre_p     = common.parseDOM(liste,"p",attrs={"class":"titre"}) [0]
            titre_u     = common.parseDOM(titre_p,"a") [0]
            titre       = titre_u.encode("utf-8")
            video_url_u = common.parseDOM(titre_p,"a",ret="href") [0]
            video_url   = video_url_u.encode("utf-8")
            if self.debug_mode :
                print "Nom : "+titre,"url : "+video_url,"Mode : 3","image : "+image_url 
            self.addLink(titre,video_url,4,image_url) 

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
        NRJ12Replay()
    except:
        print_exc()
