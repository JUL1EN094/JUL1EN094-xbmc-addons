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
common             = CommonFunctions
common.plugin      = "plugin.video.D17Replay"



__addonID__        = "plugin.video.D17Replay"
__author__         = "JUL1EN094"
__date__           = "15-12-2014"
__version__        = "1.0.8"
__credits__        = "Merci aux auteurs des autres addons replay du dépôt Passion-XBMC pour leur inspiration"
__addon__          = xbmcaddon.Addon( __addonID__ )
__settings__       = __addon__
__language__       = __addon__.getLocalizedString
__addonDir__       = __settings__.getAddonInfo( "path" )

   

# Global Variable
ROOTDIR             = __settings__.getAddonInfo('path')
BASE_RESOURCE_PATH  = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH          = os.path.join( BASE_RESOURCE_PATH, "media" )
ADDON_DATA          = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
CACHEDIR            = os.path.join( ADDON_DATA, "cache")
THUMB_CACHE_PATH    = os.path.join( xbmc.translatePath( "special://profile/" ), "Thumbnails", "Video" )
WEBROOT             = "http://www.d17.tv"
CANAL_VIDEOINFO_URL = "http://service.canal-plus.com/video/rest/getVideosLiees/"        
FANART_PATH         = os.path.join( ROOTDIR, "fanart.jpg" )      

# List of directories to check at startup
dirCheckList       = (CACHEDIR,)
 

class D17Replay:
    """
    main plugin class
    """
    debug_mode = False # Debug mode
    
    def __init__( self, *args, **kwargs ):
        print "==============================="
        print "  D17 Replay - Version: %s"%__version__
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
        iconimage = None            
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
            print "Mode: "+str(mode)
            print "URL: "+str(url)
            print "Name: "+str(name)
            print "Iconimage: "+str(iconimage)
 
        # Check if directories in user data exist
        for i in range(len(dirCheckList)):
            self.checkfolder(dirCheckList[i]) 
    
        if mode==None or url==None or len(url)<1:
            if self.debug_mode:
                print "GET_CATEGORIES("+WEBROOT+")"
            self.GET_CATEGORIES(WEBROOT)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            
        elif mode==1:
            if self.debug_mode:
                print "GET_EMISSIONS_DIR : "+url 
            self.GET_EMISSIONS_DIR(url)         
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))            
            
        elif mode==2:
            if self.debug_mode:
                print "GET_EPISODES("+url+")"
            self.GET_EPISODES(url,name)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))            

        elif mode==3:
            if self.debug_mode:
                print "PLAY_VIDEO"
            print "vid :"+str(url)
            video_url = self.GET_VIDEO_CANAL(str(url),'d17/')
            item = xbmcgui.ListItem(path=video_url) 
            xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=item)


    def GET_CATEGORIES(self,url):
        soup        = self.get_soup(url) 
        html        = soup.decode("iso-8859-1")
        main_menu_s = common.parseDOM(html,"ul",attrs={"class":"main-menu"})
        if main_menu_s :
            main_menu = main_menu_s[0]
            li_s      = common.parseDOM(main_menu,"li")
            for li in li_s : 
                links = re.findall(u"""<a href="(.*)">(.*)</a>""",li)
                if links:
                    for anchor in links :
                        if self.debug_mode:
                            print "categorie : "+anchor[1].encode("utf-8")
                        self.addDir(anchor[1].encode("utf-8"),WEBROOT+(anchor[0].encode("utf-8")),1,"")
    
    def GET_EMISSIONS_DIR(self,url,iconimage=''):    # Olala mal de crâne!!
        soup            = self.get_soup(url)
        html            = soup.decode("iso-8859-1")
        main_s = common.parseDOM(html,"div",attrs={"id":"main"})
        if main_s :
            main           = main_s[0]
            block_videos_s = common.parseDOM (main,"div",attrs={"class":"block-videos"})
            for block in block_videos_s :
                bvh_titles_s = common.parseDOM(block,"h3",attrs={"class":"bvh-title"})
                for bvh in bvh_titles_s :
                    if bvh.startswith("<a href") : 
                        bvh = common.parseDOM(bvh,'a')[0]
                    self.addDir(bvh.encode("utf-8"),url,2,"")

    def GET_EPISODES(self,url,name):
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        soup   = self.get_soup(url)
        html   = soup.decode("iso-8859-1")
        main_s = common.parseDOM(html,"div",attrs={"id":"main"})
        if main_s :
            main           = main_s[0]
            block_videos_s = common.parseDOM (main,"div",attrs={"class":"block-videos"})
            for block in block_videos_s :
                bvh_titles_s = common.parseDOM(block,"h3",attrs={"class":"bvh-title"})
                for bvh in bvh_titles_s :
                    if bvh.startswith("<a href") : 
                        bvh = common.parseDOM(bvh,'a')[0]
                    if bvh.encode("utf-8")==name :
                        Mylist = common.parseDOM(block,"ul",attrs={"class":"bv-list MYlist"})[0]
                        li_s   = common.parseDOM(Mylist,"li")
                        for li in li_s :
                            episode_vid   = common.parseDOM(li,"a",ret="href")[0]
                            episode_vid   = str(re.findall("""\?vid=(.*)""",episode_vid)[0])
                            episode_name  = common.parseDOM(li,"h4")[0].encode("utf-8")
                            episode_image = common.parseDOM(li,"img",ret="src")[0].encode("utf-8")
                            self.addLink(episode_name,episode_vid,3,episode_image)

    def GET_VIDEO_CANAL(self,vid,canal):
        soup  = self.get_soup(CANAL_VIDEOINFO_URL+canal+vid)
        xml   = soup.decode("utf-8")
        video_s = common.parseDOM(xml,"VIDEO")
        for video in video_s :
            id = common.parseDOM(video,'ID') [0]
            if str(id) == str(vid) :
                video_url = common.parseDOM(video,"HLS")[0]
                return video_url            
          
    def set_debug_mode(self):
        debug =__settings__.getSetting('debug')
        if debug == 'true':
            self.debug_mode = True
        else:
            self.debug_mode = False
        print "D17 Replay: debug Mode:"
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
        req.add_header('User-Agent','Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/15.0.1')           
        req.add_header('Referer',url)
        soup = urllib2.urlopen(req).read()
        if (self.debug_mode):
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
        D17Replay()
    except:
        print_exc()