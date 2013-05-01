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
common.plugin = "plugin.video.Cherie25Replay"


__addonID__         = "plugin.video.Cherie25Replay"
__author__          = "JUL1EN094"
__date__            = "01-02-2013"
__version__         = "1.0.1"
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
FANART_PATH         = os.path.join( ROOTDIR, "fanart.jpg" )

# Web variable
USERAGENT           = "Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/15.0.1"
# Web variable
WEBROOT = "http://www.cherie25.fr"
WEBSITE = WEBROOT + "/replay-4272/collectionvideo/"        
INFOSITE = "http://prod-kernnrj12v5.integra.fr/videoinfo"  
       
# List of directories to check at startup
dirCheckList        = (CACHEDIR,)


class Cherie25Replay:
    """
    main plugin class
    """
    debug_mode = False #self.debug_mode
    
    def __init__( self, *args, **kwargs ):
        print "==============================="
        print "  Chérie 25 Replay - Version: %s"%__version__
        print "==============================="
        print
        self.set_debug_mode()
        if self.debug_mode:
            print "Python version:"
            print sys.version_info
            print "ROOTDIR: %s"%ROOTDIR
            print "ADDON_DATA: %s"%ADDON_DATA
            print "CACHEDIR: %s"%CACHEDIR 
            print "FANART_PATH: %s"%FANART_PATH 
        params     = self.get_params()
        url        = None
        name       = None
        mode       = None
        iconimage  = None   
        desc       = None         
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
        try:
            desc=urllib.unquote_plus(params["desc"])
        except:
            pass            
                    
        if self.debug_mode:
            print "Mode: "+str(mode)
            print "URL: "+str(url)
            print "Name: "+str(name)
            print "Iconimage: "+str(iconimage)
            print "Description : "+str(desc)
 
        # Check if directories in user data exist
        for i in range(len(dirCheckList)):
            self.checkfolder(dirCheckList[i]) 
    
        if mode==None or url==None or len(url)<1:
            if self.debug_mode:
                print "GET_CATEGORIES("+WEBSITE+")"
            self.addDir(__language__(30051).encode("utf-8"),"All_Episodes",1,MEDIA_PATH+u"\\folder2.png",FANART_PATH,"")
            self.GET_CATEGORIES(WEBSITE)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
                            
        elif mode==1:
            if self.debug_mode:
                print "GET_EMISSIONS("+WEBSITE+","+url+")"
            self.GET_EMISSIONS(WEBSITE,url)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )

        elif mode==2:
            if self.debug_mode:
                print "GET_EPISODES("+WEBSITE+","+url+","+str(iconimage)+")"
            self.GET_EPISODES(WEBSITE,url,iconimage)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )

        elif mode==3:
            if self.debug_mode:
                print "PLAY_VIDEO"
            item = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=item)
                 
  
    def GET_CATEGORIES(self,url):
        soup   = self.get_soup(url,url)
        html   = soup.decode("utf-8")
        line_s = common.parseDOM(html,"div",attrs={"class":u"line replay magazines"})
        for line in line_s :
            title = common.parseDOM(line,"div",attrs={"class":"title"})[0]
            categorie_name = common.parseDOM(title,"span")[0].encode("utf-8")
            self.addDir(categorie_name,categorie_name,1,MEDIA_PATH+u"\\folder.png",FANART_PATH,"")

    def GET_EMISSIONS(self,url,cat):
        soup        = self.get_soup(url,url)
        html        = soup.decode("utf-8")
        line_replay = common.parseDOM(html,"div",attrs={"class":u"line replay magazines"})
        for line in line_replay :
            title = common.parseDOM(line,"div",attrs={"class":"title"})[0]
            categorie = common.parseDOM(title,"span")[0].encode("utf-8")
            if cat   == "All_Episodes" :
                li_s    = common.parseDOM(line,"li",attrs={"id":"liste_[0-9]"})
                for li in li_s :
                    replay_hover_s = common.parseDOM(li,"div",attrs={"class":u"replay_hover"})
                    if replay_hover_s :
                        image_div  = common.parseDOM(li,"div",attrs={"class":"image"}) [0]
                        image_a_u  = common.parseDOM(image_div,"a") [0]
                        image_url  = common.parseDOM(image_a_u,"img",ret="src") [0]
                        titre_p    = common.parseDOM(li,"p",attrs={"class":"titre"}) [0]
                        titre_u    = common.parseDOM(titre_p,"a") [0]
                        titre      = titre_u.encode("utf-8")
                        if self.debug_mode :
                            print "Nom : "+titre,"url : "+titre,"Mode : 3","image : "+image_url, 
                        self.addDir(titre,titre,2,image_url,image_url,"")
                    else :
                        image_div   = common.parseDOM(li,"div",attrs={"class":"image"}) [0]
                        image_a_u   = common.parseDOM(image_div,"a") [0]
                        image_url   = common.parseDOM(image_a_u,"img",ret="src") [0]
                        titre_p     = common.parseDOM(li,"p",attrs={"class":"titre"}) [0]
                        titre_u     = common.parseDOM(titre_p,"a") [0]
                        titre       = titre_u.encode("utf-8")
                        video_url_u = common.parseDOM(titre_p,"a",ret="href") [0]
                        video_url   = video_url_u.encode("utf-8")
                        if self.debug_mode :
                            print "Nom : "+titre,"url : "+video_url,"Mode : 3","image : "+image_url 
                        self.addLink(titre,video_url,3,image_url,"")
            elif cat == categorie :
                li_s    = common.parseDOM(line,"li",attrs={"id":"liste_[0-9]"})
                for li in li_s :
                    replay_hover_s = common.parseDOM(li,"div",attrs={"class":u"replay_hover"})
                    if replay_hover_s :
                        image_div  = common.parseDOM(li,"div",attrs={"class":"image"}) [0]
                        image_a_u  = common.parseDOM(image_div,"a") [0]
                        image_url  = common.parseDOM(image_a_u,"img",ret="src") [0]
                        titre_p    = common.parseDOM(li,"p",attrs={"class":"titre"}) [0]
                        titre_u    = common.parseDOM(titre_p,"a") [0]
                        titre      = titre_u.encode("utf-8")
                        if self.debug_mode :
                            print "Nom : "+titre,"url : "+titre,"Mode : 2","image : "+image_url, 
                        self.addDir(titre,titre,2,image_url,image_url,"")
                    else :
                        image_div   = common.parseDOM(li,"div",attrs={"class":"image"}) [0]
                        image_a_u   = common.parseDOM(image_div,"a") [0]
                        image_url   = common.parseDOM(image_a_u,"img",ret="src") [0]
                        titre_p     = common.parseDOM(li,"p",attrs={"class":"titre"}) [0]
                        titre_u     = common.parseDOM(titre_p,"a") [0]
                        titre       = titre_u.encode("utf-8")
                        video_url_u = common.parseDOM(titre_p,"a",ret="href") [0]
                        video_url   = video_url_u.encode("utf-8")
                        if self.debug_mode :
                            print "Nom : "+titre,"url : "+video_url,"Mode : 3","image : "+image_url 
                        self.addLink(titre,video_url,3,image_url,"")

    def GET_EPISODES(self,url,emission,fanart):
        soup        = self.get_soup(url,url)
        html        = soup.decode("utf-8")
        line_replay = common.parseDOM(html,"div",attrs={"class":u"line replay magazines"})
        for line in line_replay :
            li_s    = common.parseDOM(line,"li",attrs={"id":"liste_[0-9]"})
            for li in li_s :
                replay_hover_s = common.parseDOM(li,"div",attrs={"class":u"replay_hover"})
                if replay_hover_s :
                    titre_p   = common.parseDOM(li,"p",attrs={"class":"titre"}) [0]
                    titre_u   = common.parseDOM(titre_p,"a") [0]
                    titre     = titre_u.encode("utf-8")
                    if titre == emission:
                        self.get_titres(emission,li,fanart)  

    def get_titres(self,emission,liste,fanart):
        replay_hover_s = common.parseDOM(liste,"div",attrs={"class":u"replay_hover"})
        if replay_hover_s :
            replay_hover = replay_hover_s[0]
            li_s         = common.parseDOM(replay_hover,"li",attrs={"id":"list_item_[0-9]"})
            for li in li_s :
                image_div   = common.parseDOM(li,"div",attrs={"class":"image"}) [0]
                image_a_u   = common.parseDOM(image_div,"a") [0]
                image_url   = common.parseDOM(image_a_u,"img",ret="src") [0]
                titre_p     = common.parseDOM(li,"p",attrs={"class":"titre"}) [0]
                titre_u     = common.parseDOM(titre_p,"a") [0]
                titre       = titre_u.encode("utf-8")
                video_url_u = common.parseDOM(titre_p,"a",ret="href") [0]
                video_url   = WEBROOT+video_url_u.encode("utf-8")
                video_desc  = self.get_video_desc(video_url)
                mediaId     = self.get_mediaId(video_url)
                url_video   = self.get_episode_url(INFOSITE,mediaId)
                if self.debug_mode :
                    print "Nom : "+titre,"url : "+url_video,"Mode : 3","image : "+image_url, 
                self.addLink(titre,url_video,3,image_url,fanart,video_desc)
    
    def get_video_desc(self,url):
        soup                       = self.get_soup(url,url)
        html                       = soup.decode("utf-8")
        encart_titre_mea_mea_video = common.parseDOM(html,"div",attrs={"class":u"encart_titre_mea mea_video"}) [0]
        text_infos                 = common.parseDOM(encart_titre_mea_mea_video,"div",attrs={"class":u"text-infos"}) [0]
        text                       = common.parseDOM(text_infos,"div",attrs={"class":"text"}) [0]
        video_desc                 = common.parseDOM(text,"p")[0]
        return video_desc.encode("utf-8")

    def get_mediaId(self,url) :
        soup = self.get_soup(url,url)    
        html = soup.decode("utf-8")
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
    
    def set_debug_mode(self):
        self.debug_mode=__settings__.getSetting('debug')
        if self.debug_mode== 'true':
            self.debug_mode = True
        else:
            self.debug_mode = False
        print "HD1:self.debug_mode Mode:"
        print self.debug_mode        
        
    def addLink(self,name,url,mode,iconimage,fanart,desc):
        u  =sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&desc="+urllib.quote_plus(desc)
        ok =True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name,"plot":desc } )
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty('Fanart_Image', fanart )
        ok =xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok         

    def addDir(self,name,url,mode,iconimage,fanart,desc):
        u  =sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&desc="+urllib.quote_plus(desc)
        ok =True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name,"plot":desc } )
        liz.setProperty('Fanart_Image',fanart)
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

    def get_soup(self,url,referer):
        req  = urllib2.Request(url)
        req.add_header('User-Agent',USERAGENT)           
        req.add_header('Referer',referer)
        soup = urllib2.urlopen(req).read()
        if (self.debug_mode):
            print "get_soup : " + url
            print "referer  : " + referer
            print str(soup)
        return soup

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
        Cherie25Replay()
    except:
        print_exc()