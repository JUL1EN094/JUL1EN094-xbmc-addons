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
common.plugin = "plugin.video.TMCReplay"
# HASHLIB (replace MD5)
import hashlib 
# json
import json

__addonID__         = "plugin.video.TMCReplay"
__author__          = "JUL1EN094"
__date__            = "01-02-2013"
__version__         = "1.0.1"
__credits__         = "Merci aux auteurs des autres addons replay du dépôt Passion-XBMC et de la communauté open-source"
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

# Web variable
USERAGENT           = "Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/15.0.1"
WEBROOT             = "http://www.tmc.tv"
WEBSITE             = WEBROOT+"/liste-programme-tv/"

WEBROOTVIDEO        = "http://videos.tmc.tv"
WEBROOTWAT          = "http://www.wat.tv"

       
# List of directories to check at startup
dirCheckList        = (CACHEDIR,)


class TMCReplay:
    """
    main plugin class
    """
    debug_mode = False #self.debug_mode
    
    def __init__( self, *args, **kwargs ):
        print "==============================="
        print "  TMC Replay - Version: %s"%__version__
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
            self.GET_EMISSIONS(WEBSITE)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_LABEL)
                            
        elif mode==1:
            self.GET_CATEGORIES_EMISSIONS (url)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_LABEL)


        elif mode==2:
            self.GET_EPISODES(url)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory(handle=int(sys.argv[1]),category=__language__(30000))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod(handle=int(sys.argv[1]),sortMethod=xbmcplugin.SORT_METHOD_LABEL)
                    
        elif mode==3:
            video_url = self.GET_VIDEO_URL(url).encode("utf-8")
            item = xbmcgui.ListItem(path=video_url) 
            xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]),succeeded=True,listitem=item)
            

    def GET_EMISSIONS(self,url):
        if self.debug_mode:
            print "GET_EMISSIONS("+url+")"
        soup     = self.get_soup(url,url)
        html     = soup.decode("utf-8")
        AaZ_url  = self.get_AaZ_url(url)
        self.get_emissions_param(AaZ_url)       
        
    def GET_CATEGORIES_EMISSIONS(self,url):
        if self.debug_mode:
            print "GET_CATEGORIES_EMISSIONS : "+url   
        soup       = self.get_soup(url,WEBROOTVIDEO)
        html       = soup.decode("utf-8")
        ongletList146853_s = common.parseDOM(html,"ul",attrs={"id":"ongletList146853"})    
        if ongletList146853_s :
            ongletList146853 = ongletList146853_s [0]
            li_s             = common.parseDOM(ongletList146853,"li")
            for li in li_s :
                a_s = common.parseDOM(li,"a",ret="href")
                if a_s :
                    categorie_emissions_url_end_u = a_s [0]
                    categorie_emissions_url       = WEBROOTVIDEO+categorie_emissions_url_end_u.encode("utf-8")
                    categorie_emissions_name_u    = common.parseDOM(li,"a") [0]
                    categorie_emissions_name_u    = categorie_emissions_name_u.split("\n") [0]
                    categorie_emissions_name      = categorie_emissions_name_u.encode("utf-8")
                else :
                    categorie_emissions_url       = url
                    categorie_emissions_name_u    = common.parseDOM(li,"span") [0]
                    categorie_emissions_name_u    = categorie_emissions_name_u.split("<span") [0]
                    categorie_emissions_name      = categorie_emissions_name_u.encode("utf-8")
                if self.debug_mode :
                    print "categorie_emissions_url : "+categorie_emissions_url
                    print "categorie_emissions_name : "+categorie_emissions_name
                self.addDir(categorie_emissions_name,categorie_emissions_url,2,"")                    
    
    def GET_EPISODES(self,url) :
        if self.debug_mode:
            print "GET_EPISODES : "+url
        soup        = self.get_soup(url,WEBROOTVIDEO)
        html        = soup.decode("utf-8")
        ibl146854_s = common.parseDOM(html,"div",attrs={"id":"ibl146854"})
        if ibl146854_s :
            ibl146854 = ibl146854_s [0]
            teaserList146854_s = common.parseDOM(ibl146854,"ul",attrs={"id":"liste_teasers146854"})
            if teaserList146854_s :
                teaserList146854 = teaserList146854_s [0]
                li_s             = common.parseDOM(teaserList146854,"li")
                n = 0
                for li in li_s :
                    print 'LI : '+li.encode("utf-8")
                    image_url_u       = common.parseDOM(li,"img",ret="src") [0]
                    image_url         = image_url_u.encode("utf-8")
                    infosTeaser       = common.parseDOM (li,"div",attrs={"class":"infosTeaser"}) [0]
                    h3                = common.parseDOM (infosTeaser,"h3") [0]
                    episode_name_u    = common.parseDOM (h3,"a") [0]
                    episode_name      = episode_name_u.encode("utf-8")
                    episode_name      = episode_name.replace("&#039;","""'""")
                    episode_url_end_u = common.parseDOM (h3,"a",ret="href") [0]
                    episode_url_end   = episode_url_end_u.encode("utf-8")
                    episode_url       = WEBROOTVIDEO+episode_url_end
                    if self.debug_mode :
                        print "image_url : "+image_url
                        print "episode_name : "+episode_name
                        print "episode_url : "+episode_url
                    self.addLink(episode_name,episode_url,3,image_url)
                    n = n + 1
        suivante_c4_t3_s  = common.parseDOM(html,"li",attrs={"class":u"suivante c4 t3"})
        if suivante_c4_t3_s :
            suivante_c4_t3 = suivante_c4_t3_s [0]
            a_s            = common.parseDOM(suivante_c4_t3,"a",ret="href")
            if a_s :
               next_url_end = a_s [0]
               next_url     = WEBROOTVIDEO+next_url_end.encode("utf-8")
               print "NEXTURL :"+next_url
               self.GET_EPISODES(next_url)    ##!! RECURSIVE FUNCTION!!
            else :
                print "ENDNEXT"  
        else :
            print "END - 1PAGE"
                                                        
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
        
    def get_AaZ_url(self,url):
        if self.debug_mode :
            print "get_AaZ_url : "+url
        soup = self.get_soup(url,url)
        html = soup.decode("utf-8")
        a_s  = common.parseDOM(html,"a",attrs={"class":u"c2 f1 t3"})
        n    = -1
        for a in a_s : 
            n = n+1
            if a == "De A &agrave; Z" :
                AaZ_url_end_s = common.parseDOM(html,"a",attrs={"class":u"c2 f1 t3"},ret="onmousedown")[n]
                AaZ_url_end   = re.findall("""sjs\(this,'#(.*)'""",AaZ_url_end_s)[0]
                AaZ_url_end   = urllib.quote(AaZ_url_end)
                AaZ_url_end   = "/".join(AaZ_url_end.split("%7C"))
                AaZ_url_end   = ".html".join(AaZ_url_end.split("%40html"))
                AaZ_url       = WEBROOT + AaZ_url_end
                if self.debug_mode :
                    print "AaZ_url : "+ AaZ_url.encode("utf-8")
                return AaZ_url

    def get_emissions_param(self,url):
        if self.debug_mode :
            print "get_emissions_param : "+url
        soup       = self.get_soup(url,url)
        html       = soup.decode("utf-8")
        prg_s = common.parseDOM(html,"li",attrs={"class":u"prg"})
        prg_dernier_s = common.parseDOM(html,"li",attrs={"class":u"prg dernier"})
        if prg_s :
            self.get_prg_param(prg_s)
        if prg_dernier_s :
            self.get_prg_param(prg_dernier_s)
        suivante_c4_t3_s = common.parseDOM(html,"li",attrs={"class":u"suivante c4 t3"})
        if suivante_c4_t3_s :
            suivante_c4_t3 = suivante_c4_t3_s [0]
            a_s = common.parseDOM(suivante_c4_t3,"a",ret="onmousedown")
            if a_s :
                a = a_s [0]
                next_url_end   = re.findall("""sjs\(this,'#(.*)'""",a)[0]
                next_url_end   = urllib.quote(next_url_end)
                next_url_end   = "/".join(next_url_end.split("%7C"))
                next_url_end   = ".html".join(next_url_end.split("%40html"))
                next_url     = WEBROOT+next_url_end.encode("utf-8")
                print "NEXTURL :"+next_url
                self.get_emissions_param(next_url)    ##!! RECURSIVE FUNCTION!!
            else :
                print "ENDNEXT"  
        else :
            print "END - 1PAGE"        
        
    def get_mediaID(self,url) :
        soup          = self.get_soup(url,WEBROOTVIDEO)
        html          = soup.decode("utf-8")
        player_unique = common.parseDOM(html,"div",attrs={"class":u"unique"})[0]
        mediaID       = [x.strip() for x in re.findall("mediaId :([^,]*)", player_unique)][0]
        referer       = [x.strip() for x in re.findall('url : "(.*?)"', player_unique)][0]
        return mediaID, referer
                                                    
    def get_prg_param(self,prg_list):
        n = 0
        for prg in prg_list :
            if self.debug_mode :
                print "prg : "+prg.encode("utf-8")
            image_url_u         = common.parseDOM(prg_list,"img",ret="""src""")[n]
            image_url          = image_url_u.encode("utf-8")
            if self.debug_mode :
                print "image_url : "+image_url
            title              = common.parseDOM(prg_list,"h2") [n]
            emission_url_end_u = common.parseDOM(title,"a",ret="href") [0]
            emission_url       = WEBROOTVIDEO + emission_url_end_u.encode("utf-8") 
            if self.debug_mode :
                print "emission_url : "+emission_url
            emission_titre_u   = common.parseDOM(title,"a") [0]
            emission_titre     = emission_titre_u.encode("utf-8")
            if self.debug_mode :
                print "emission_titre : "+emission_titre
            self.addDir(emission_titre,emission_url,1,image_url)
            n = n + 1
    
    def get_wat(self,mediaID,wat_url):                                
        
        time_stamp = self.base36encode(int(self.get_time_stamp()))
        timesec    = hex(int(time_stamp, 36))[2:]  
        while(len(timesec)<8):
            timesec = "0"+timesec
        token = hashlib.md5("9b673b13fa4682ed14c3cfa5af5310274b514c4133e9b3a81e6e3aba00912564"+wat_url+str(mediaID)+str(timesec)).hexdigest()
        id_url1 = WEBROOTWAT+"/get"+wat_url+str(mediaID)+"?token="+token+"/"+str(timesec)+"&country=FR&getURL=1"   #&version=WIN 11,5,502,110&playerContext=CONTEXT_TMC&domain=videos.tmc.tv&domain2=null&revision=4.1.85&synd=0&helios=1&context=swftmc
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
        print "TMC Replay:self.debug_mode Mode:"
        print self.debug_mode        
        
    def addLink(self,name,url,mode,iconimage):
        u  =sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok =True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('IsPlayable', 'true')
        ok =xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok         

    def addDir(self,name,url,mode,iconimage):
        u  =sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok =True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
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
            base36 = alphabet[i] + base36
        return base36 or alphabet[0]                                     
                                           

#######################################################################################################################    
# BEGIN !
#######################################################################################################################

if ( __name__ == "__main__" ):
    try:
        TMCReplay()
    except:
        print_exc()