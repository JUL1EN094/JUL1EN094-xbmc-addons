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
common.plugin = "plugin.video.HD1"
# HASHLIB (replace MD5)
import hashlib 
# json
import json

__addonID__         = "plugin.video.HD1"
__author__          = "JUL1EN094"
__date__            = "01-02-2013"
__version__         = "1.0.4"
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
WEBROOT             = "http://www.hd1.tv"
WEBPG               = WEBROOT+"/programmes-tv/"
WEBREPLAY           = WEBROOT+"/videos/tous-les-replay/"
WEBROOTWAT          = "http://www.wat.tv"

       
# List of directories to check at startup
dirCheckList        = (CACHEDIR,)


class HD1:
    """
    main plugin class
    """
    debug_mode = False #self.debug_mode
    
    def __init__( self, *args, **kwargs ):
        print "==============================="
        print "  HD1 - Version: %s"%__version__
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
            self.addDir("Programmes",WEBPG,1,MEDIA_PATH+u"\\folder.png","Les programmes HD1")
            self.addDir("Replay",WEBREPLAY,2,MEDIA_PATH+u"\\folder.png","HD1:Les videos en replay")
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_LABEL)
                            
        elif mode==1:
            self.GET_EMISSIONS(url)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_LABEL)

        elif mode==2:
            self.GET_EPISODES (url)         
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_LABEL)
                    
        elif mode==3:
            video_url = self.GET_VIDEO_URL(url).encode("utf-8")
            item = xbmcgui.ListItem(path=video_url) 
            xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]),succeeded=True,listitem=item)
            xbmcplugin.endOfDirectory(int(sys.argv[1]))

        elif mode==20:
            self.GET_EPISODES_EMISSION(url)         
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_LABEL)
   
    def GET_EMISSIONS(self,url):
        if self.debug_mode:
            print "GET_EMISSIONS : "+url   
        soup      = self.get_soup(url,url)
        html      = soup.decode("utf-8")
        article_1 = common.parseDOM(html,"article",attrs={"class":u"teaser d-inline b-shadow1"})
        article_2 = common.parseDOM(html,"article",attrs={"class":u"teaser d-inline b-shadow1 hasLabel"})
        article_s = article_1 + article_2
        for article in article_s :
            emission_image = common.parseDOM(article,"img",ret="src")[0].encode("utf-8")
            h3_title       = common.parseDOM(article,"h3",attrs={"class":"title"}) [0]
            emission_url   = common.parseDOM(h3_title,"a",ret="href")[0].encode("utf-8")
            if emission_url[:4] != "http":
                emission_url = WEBROOT+emission_url
            emission_name  = common.parseDOM(h3_title,"a")[0].encode("utf-8")
            emission_desc  = ""
            if self.debug_mode :
                print "emission_image : "+emission_image
                print "emission_url : "+emission_url
                print "emission_name : "+emission_name
                print "emission_desc : "+emission_desc
            self.addDir(emission_name,emission_url,20,emission_image,emission_desc)

    def GET_EPISODES(self,url) :
        if self.debug_mode:
            print "GET_EPISODES : "+url   
        soup      = self.get_soup(url,url)
        html      = soup.decode("utf-8")
        article_s = common.parseDOM(html,"article",attrs={"class":u"teaser d-inline b-shadow1 hasLabel hasMedia"})
        for article in article_s :
            episode_image = common.parseDOM(article,"img",ret="src")[0].encode("utf-8")
            title         = common.parseDOM(article,"div",attrs={"class":"title"}) [0]
            episode_url   = common.parseDOM(title,"a",ret="href")[0].encode("utf-8")
            if episode_url[:4] != "http":
                episode_url = WEBROOT+episode_url
            episode_name  = common.parseDOM(title,"a")[0].encode("utf-8")
            try :
                episode_desc  = self.get_description(episode_url)
            except :
                episode_desc = episode_name
            if self.debug_mode :
                print "episode_image : "+episode_image
                print "episode_url : "+episode_url
                print "episode_name : "+episode_name
                print "episode_desc : "+episode_desc
            self.addLink(episode_name,episode_url,3,episode_image,episode_desc)
            xbmcplugin.setContent(int(sys.argv[1]),"movies")
#         next1 = common.parseDOM(html,"span",attrs={"class":"next"})  
#         if next1 : 
#             next = next1[0]
#             next_url = WEBROOT+common.parseDOM(next,"a",ret="href")[0].encode("utf-8")
#             if next_url :
#                 if self.debug_mode:
#                     print "next_url : "+next_url
#                 self.addDir("Pages suivantes",next_url,2,MEDIA_PATH+u"\\next.png","")                

    def GET_EPISODES_EMISSION(self,url) :
        if self.debug_mode:
            print "GET_EPISODES_EMISSION : "+url   
        soup      = self.get_soup(url,url)
        html      = soup.decode("utf-8")
        ibl166633 = common.parseDOM(html,"div",attrs={"id":u"ibl166633"})[0]
        li_s = common.parseDOM(ibl166633,"li")
        for li in li_s :
            episode_image = common.parseDOM(li,"img",ret="src")[0].encode("utf-8")
            title         = common.parseDOM(li,"h2",attrs={"class":u"titre sz20 c3 b"}) [0]
            episode_url   = common.parseDOM(title,"a",ret="href")[0].encode("utf-8")
            if episode_url[:4] != "http":
                episode_url = WEBROOT+episode_url
            episode_name  = common.parseDOM(title,"a")[0].encode("utf-8")
            episode_desc  = self.get_description(episode_url)
            if self.debug_mode :
                print "episode_image : "+episode_image
                print "episode_url : "+episode_url
                print "episode_name : "+episode_name
                print "episode_desc : "+episode_desc
            self.addLink(episode_name,episode_url,3,episode_image,episode_desc)
            xbmcplugin.setContent(int(sys.argv[1]),"movies")
#         next1 = common.parseDOM(html,"span",attrs={"class":"next"})  
#         if next1 : 
#             next = next1[0]
#             next_url = WEBROOT+common.parseDOM(next,"a",ret="href")[0].encode("utf-8")
#             if next_url :
#                 if self.debug_mode:
#                     print "next_url : "+next_url
#                 self.addDir("Pages suivantes",next_url,2,MEDIA_PATH+u"\\next.png","")                
                                                     
    def GET_VIDEO_URL(self,url) :
        if self.debug_mode:
            print "GET_VIDEO_URL("+url+")"
        ## Find mediaID and Referer
        mediaId  = self.get_mediaID(url) [0]
        referer  = self.get_mediaID(url) [1]
        if self.debug_mode : 
            print "MediaID : "+mediaId
            print "Referer : "+referer
        ## Download infos of mediaID
        jsonVideoInfos = self.get_soup(WEBROOTWAT+'/interface/contentv3/'+mediaId, referer)
        videoInfos     = json.loads(jsonVideoInfos)
        ## Check in infos if video HD is available and fix corresponding url
        try :
            HD = videoInfos["media"]["files"][0]["hasHD"]
            print "HD"
            wat_url = "/webhd/"
        except :
            wat_url = "/web/"
        ## List all video parts of mediaID from infos
        parts = []
        for vid in videoInfos['media']['files']:
            parts.append(str(vid['id']))
        ## Build video_url from list of parts
        video_url = self.build_video_url(parts,referer,wat_url)
        return video_url
    
    def get_description(self,url):
        soup           = self.get_soup(url,WEBROOT)
        html           = soup.decode("utf-8") 
        resume166495   = common.parseDOM(html,"section",attrs={"id":"resume166495","class":u"player-resume"})[0]    
        article        = common.parseDOM(resume166495,"article",attrs={"itemprop":"description"})[0]
        description_s  = common.parseDOM(article,"P")
        if description_s :
            description = description_s[0]
        else :
            description = article
        description    = description.replace(u"""<STRONG>""","")
        description    = description.replace(u"""</STRONG>""","")
        description    = description.encode("utf-8")
        return description     
    
    def get_mediaID(self,url) :
        soup          = self.get_soup(url,WEBROOT)
        html          = soup.decode("utf-8")
        player_unique = common.parseDOM(html,"section",attrs={"class":u"player-unique"})[0]
        mediaID       = [x.strip() for x in re.findall("mediaId :([^,]*)", player_unique)][0]
        referer       = [x.strip() for x in re.findall('url : "(.*?)"', player_unique)][0]
        return mediaID, referer
                               
    def get_wat(self,mediaID,wat_url):                              
        time_stamp = self.base36encode(int(self.get_time_stamp()))
        timesec    = hex(int(time_stamp, 36))[2:]  
        while(len(timesec)<8):
            timesec = "0"+timesec
        token = hashlib.md5("9b673b13fa4682ed14c3cfa5af5310274b514c4133e9b3a81e6e3aba00912564"+wat_url+str(mediaID)+str(timesec)).hexdigest()
        id_url1 = WEBROOTWAT+"/get"+wat_url+str(mediaID)+"?token="+token+"/"+str(timesec)+"&country=FR&getURL=1"   
        return id_url1
        
    def build_video_url(self,parts,referer,wat_url) :
        parts_url = []
        for vid in parts:
            print "part: " + vid
            ## Find tokenurl(mediaId)
            tokenurl = self.get_wat(vid,wat_url) 
            if self.debug_mode : 
                print "tokenurl : "+tokenurl
            ## Read tokenurl (needs referer)
            soup = self.get_soup(tokenurl,referer)
            html = soup.decode("utf-8")
            ## Build video_url
            rtmp  = 0
            if html.find("rtmpe,")!=-1 :
                html_url = html[6:] 
                rtmp     = 1 
            elif html.find("rtmp,")!=-1 :
                html_url = html[5:] 
                rtmp     = 1
            if rtmp == 1:
                html_url = html_url.replace("rtmpte","rtmpe")
                parts_url.append(html_url+""" swfUrl=http://www.wat.tv/images/v40/PlayerWat.swf swfVfy=1""")
            elif rtmp == 0:
                parts_url.append(html+'|User-Agent=' + urllib.quote(USERAGENT) + '&Cookie=' + urllib.quote('seen=' + vid))
        ## Concatenate all parts
        sep = " , "
        if len(parts_url) > 1 :
            video_url = "stack://" + sep.join(parts_url)
        else:
            video_url = parts_url[0]
        return video_url

    def get_time_stamp(self):                                 
        soup = self.get_soup(WEBROOTWAT+"/servertime",WEBROOTWAT)
        html = soup.decode("utf-8")
        time_stamp = html.split(u"""|""") [0]
        print time_stamp.encode("utf-8")
        return time_stamp.encode("utf-8")
          
    def set_debug_mode(self):
        self.debug_mode=__settings__.getSetting('debug')
        if self.debug_mode== 'true':
            self.debug_mode = True
        else:
            self.debug_mode = False
        print "HD1:self.debug_mode Mode:"
        print self.debug_mode        
        
    def addLink(self,name,url,mode,iconimage,desc):
        u  =sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&desc="+urllib.quote_plus(desc)
        ok =True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name,"plot":desc } )
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty('Fanart_Image', FANART_PATH )
        ok =xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok         

    def addDir(self,name,url,mode,iconimage,desc):
        u  =sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&desc="+urllib.quote_plus(desc)
        ok =True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name,"plot":desc } )
        liz.setProperty('Fanart_Image', FANART_PATH )
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
                
    def base36encode(self,number):
        if not isinstance(number, (int, long)):
            raise TypeError('number must be an integer')
        if number < 0:
            raise ValueError('number must be positive')
        alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        base36 = ''
        while number:
            number, i = divmod(number, 36)
            base36    = alphabet[i] + base36
        return base36 or alphabet[0]                                     
                                           

#######################################################################################################################    
# BEGIN !
#######################################################################################################################

if ( __name__ == "__main__" ):
    try:
        HD1()
    except:
        print_exc()