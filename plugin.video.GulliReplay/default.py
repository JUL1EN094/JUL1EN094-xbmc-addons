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
import ast
# print_exc
from traceback import print_exc
# parseDOM
import CommonFunctions
common = CommonFunctions
common.plugin = "plugin.video.GulliReplay"




__addonID__         = "plugin.video.GulliReplay"
__author__          = "JUL1EN094"
__date__            = "01-02-2013"
__version__         = "2.0.0"
__credits__         = "Merci aux auteurs des autres addons replay du repo Passion XBMC pour leur inspiration"
__addon__           = xbmcaddon.Addon(__addonID__)
__settings__        = __addon__
__language__        = __addon__.getLocalizedString
__addonDir__        = __settings__.getAddonInfo("path")


   

# Global Variable
ROOTDIR             = __settings__.getAddonInfo('path')
BASE_RESOURCE_PATH  = os.path.join(ROOTDIR,"resources")
MEDIA_PATH          = os.path.join(BASE_RESOURCE_PATH,"media")
ADDON_DATA          = xbmc.translatePath("special://profile/addon_data/%s/"%__addonID__)
CACHEDIR            = os.path.join(ADDON_DATA,"cache")
THUMB_CACHE_PATH    = os.path.join(xbmc.translatePath("special://profile/"),"Thumbnails","Video")
WEBSITE             = "http://replay.gulli.fr"  




# List of directories to check at startup
dirCheckList        = (CACHEDIR,)

       


class GulliReplay:
    """
    main plugin class
    """
    debug_mode = False # Debug mode
    
    def __init__( self, *args, **kwargs ):
        print "==============================="
        print "  Gulli Replay - Version: %s"%__version__
        print "==============================="
        print
        self.set_debug_mode()
        if self.debug_mode:
            print "Python version:"
            print sys.version_info
            print "ROOTDIR: %s"%ROOTDIR
            print "ADDON_DATA: %s"%ADDON_DATA
            print "CACHEDIR: %s"%CACHEDIR  
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
            self.GET_CATEGORIES(WEBSITE)
            all_episodes = __language__(30050).encode("utf-8") 
            self.addDir(all_episodes,"http://replay.gulli.fr/AaZ",1,"")
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
                   
        elif mode==1:
            if self.debug_mode:
                print "GET_EPISODES("+url+")"
            self.GET_EPISODES(url)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
                    
        elif mode==2:
            if self.debug_mode:
                print "PLAY_VIDEO"
            rtmp_url = self.PLAY_VIDEO(url)
            item     = xbmcgui.ListItem(path=rtmp_url) 
            xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=item)
            
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_LABEL)

    def GET_CATEGORIES(self,url):
        soup   = self.get_soup(url) 
        html   = soup.decode("utf-8")
        smenu0 = common.parseDOM(html,"dd",attrs={"id":u"smenu0"}) [0]
        ul     = common.parseDOM(smenu0,"li")
        for  li in ul :
            if self.debug_mode :
                print "li :"+li.encode("utf-8")
            url_categorie_pattern  = common.parseDOM(li,"a",ret="href") [0]
            url_categorie          = url_categorie_pattern.encode("utf-8")            
            if self.debug_mode :
                print "URL : "+url_categorie
            name_categorie_pattern = common.parseDOM(li,"span",attrs={"class":u"btn_repeat"}) [0]
            name_categorie         = name_categorie_pattern.encode("utf-8")
            if self.debug_mode :
                print "NOM : "+name_categorie
            self.addDir(name_categorie,url_categorie,1,"")
  
    def GET_EPISODES(self,url):
        soup                        = self.get_soup(url)
        html                        = soup.decode("utf-8")
        wrapper_pattern             = common.parseDOM(html,"div",attrs={"id":u"wrapper"}) [0]
        ul_liste_resultats_pattern  = common.parseDOM(wrapper_pattern,"ul",attrs={"class":"liste_resultats"})
        for ul in ul_liste_resultats_pattern :
            li_pattern_list = common.parseDOM(ul,"li")
            for li_pattern in li_pattern_list :
                image_url_pattern   = common.parseDOM(li_pattern,"img",ret="src") [0]
                image_url           = image_url_pattern.encode("utf-8")
                if self.debug_mode :
                    print "image_url :"+image_url
                episode_url_pattern = common.parseDOM(li_pattern,"a",ret="href") [0]
                episode_url         = episode_url_pattern.encode("utf-8")
                if self.debug_mode :
                    print "episode_url : "+episode_url
                titre1_pattern      = common.parseDOM(li_pattern,"strong") [0]
                titre1              = titre1_pattern.encode("utf-8")
                if self.debug_mode :
                    print "titre1 :"+titre1
                p_list_pattern      = common.parseDOM(li_pattern,"p") [0]
                titre2_pattern      = common.parseDOM(p_list_pattern,"span") [0]
                titre2_tmp          = titre2_pattern.encode("utf-8")
                titre2_tmp          = "//".join(titre2_tmp.split("""<br/>"""))
                titre2_tmp          = "".join(titre2_tmp.split("\n"))
                titre2_tmp          = "".join(titre2_tmp.split("\s"))
                titre2_tmp          = "".join(titre2_tmp.split("\t"))
                titre2_tmp          = "".join(titre2_tmp.split("\r"))
                titre2_tmp          = "".join(titre2_tmp.split("\f"))
                titre2_tmp          = "".join(titre2_tmp.split("\v"))
                titre2              = " ".join(titre2_tmp.split("&nbsp;"))
                if self.debug_mode :
                    print "titre2 : "+titre2                                
                titre_episode       = titre1 +" : "+ titre2
                if self.debug_mode :
                    print "titre_episode :"+titre_episode
                self.addLink(titre_episode,episode_url,2,image_url)
 
    def PLAY_VIDEO(self,url):
        smil_url   = self.get_smil_url(url)
        video_name = self.get_video_filename(smil_url)
        streamer   = "rtmp://stream2.lgdf.yacast.net/gulli_replay"
        app        = "gulli_replay"
        swfUrl     = "http://cdn1-gulli.ladmedia.fr/extension/lafrontoffice/design/standard/flash/jwplayer/release/player.swf"
        swfVfy     = "1"
        extension  = re.findall("""\.(.*)""",video_name) [0]
        if extension :
            rtmp_url   = streamer +" app="+app+" swfUrl="+swfUrl+" playpath=mp4:"+video_name+" swfVfy="+swfVfy
            if self.debug_mode:
                print rtmp_url
            return rtmp_url

    def get_smil_url(self,url):
        soup             = self.get_soup(url)
        html             = soup.decode("utf-8")
        wrapper_pattern  = common.parseDOM(html,"div",attrs={"id":u"wrapper"}) [0]
        column_2_pattern = common.parseDOM(wrapper_pattern,"div",attrs={"class":u"column_2"}) [0]
        script_pattern   = common.parseDOM(column_2_pattern,"script") [1]
        script           = script_pattern.encode("utf-8")
        script_split     = script.split("""display geoblocking message""") [0]
        script_split     = script_split.encode("utf-8")
        smil_url         = re.findall(u""".*type:.*"POST".*url:.*"(.*)".*data:""",script_split) [0]
        if smil_url :
            smil_url = smil_url.encode("utf-8")
            if self.debug_mode :
                print "smil_url : "+smil_url
            return smil_url
        
    def get_video_filename(self,url):
        soup           = self.get_soup(url)
        html           = soup.decode("utf-8")
        dico           = ast.literal_eval(html) 
        video_filename = dico["filename"]
        video_filename = video_filename.encode("utf-8")
        if self.debug_mode :
            print "video_filename : "+video_filename
        return video_filename

    def set_debug_mode(self):
        debug =__settings__.getSetting('debug')
        if debug == 'true':
            self.debug_mode = True
        else:
            self.debug_mode = False
        print "Gulli Replay: debug Mode:"
        print self.debug_mode        
        
    def addLink(self,name,url,mode,iconimage):
        u  = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok = True
        liz= xbmcgui.ListItem(name,iconImage="DefaultVideo.png",thumbnailImage=iconimage)
        liz.setInfo(type="Video",infoLabels={"Title":name})
        liz.setProperty('IsPlayable','true')
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok         

    def addDir(self,name,url,mode,iconimage):
        u  = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok = True
        liz= xbmcgui.ListItem(name,iconImage="DefaultFolder.png",thumbnailImage=iconimage)
        liz.setInfo(type="Video",infoLabels={"Title":name})
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
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
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/15.0.1')           
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
        GulliReplay()
    except:
        print_exc()