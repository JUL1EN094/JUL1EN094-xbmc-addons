#-*- coding: utf-8 -*-

# IMPORTS
import CommonFunctions
import re
import requests
from xbmcswift2 import Plugin

# OBJECTS()
common = CommonFunctions
common.plugin = "plugin.video.GulliReplay"
plugin = Plugin()

# VARIABLES
__addon__   = plugin.addon
__path__    = __addon__.getAddonInfo("path")
__version__ = __addon__.getAddonInfo("version")
LS_INDEX =(
          {'Label':'Dessins Animés','EndUrl':'dessins-animes'},
          {'Label':'Séries'        ,'EndUrl':'series'},
          {'Label':'L\'intégrale'  ,'EndUrl':'all'},
          {'Label':'Emissions'     ,'EndUrl':'emissions'}
          )
URL_BASE  = 'http://replay.gulli.fr'
URL_VIDEO = 'http://replay.gulli.fr/jwplayer/embed/%s'

#------------------------------------
#-------------ROUTES----------------- 
#------------------------------------
@plugin.route('/')
def index():
    items = []
    for item in LS_INDEX :
        items.append({'label':item['Label'],'path':plugin.url_for('get_shows',url='%s/%s'%(URL_BASE,item['EndUrl']))})
    items.sort()
    return items    

@plugin.route('/get_shows/<url>/<isTitle>',name='get_all_shows')
@plugin.route('/get_shows/<url>/')
def get_shows(url,isTitle=False):
    plugin.log.debug('get_shows(%s)'%url)
    items = []
    n     = 0
    while n > -1 :
        if n==0 : tmpUrl = url
        else    : tmpUrl = '%s/%s' %(url,n)
        html  = requests.get(tmpUrl).text.encode('utf-8')
        plugin.log.debug('%s'%tmpUrl)
        plugin.log.debug('%s'%html)
        shows = common.parseDOM(html,'div',attrs={'class':'col-md-4'})
        if not shows : 
            shows = common.parseDOM(html,'div',attrs={'class':'col-md-2 col-sm-3 col-xs-6'})
        if shows :
            for show in shows :
                show_url = common.parseDOM(show,'a',ret='href')[0]
                show_img = 'http:%s' %(common.parseDOM(show,'img',ret='src')[0])
                if isTitle :
                    show_name = common.parseDOM(show,'img',ret='alt')[0]
                else :
                    show_name = show_url.split('/')[-1].replace('-',' ')
                plugin.log.debug('------------')
                plugin.log.debug('show_name -> %s'%show_name)
                plugin.log.debug('show_url  -> %s'%show_url)
                plugin.log.debug('show_img  -> %s'%show_img)
                plugin.log.debug('-----------')
                items.append({'label':show_name,'path':plugin.url_for('get_episodes',url=show_url),'icon':show_img})
            n+=1
        else :
            n=-1
    plugin.set_content('tvshows')
    return items
    
@plugin.route('/get_episodes/<url>/')
def get_episodes(url):
    plugin.log.debug('get_episodes(%s)'%url)
    items = []
    html  = requests.get(url).text
    plugin.log.debug(url)
    plugin.log.debug(html.encode('utf-8'))
    all   = common.parseDOM(html,'div',attrs={'class':'all-videos'})[0]
    epi_s = common.parseDOM(all,'li',attrs={'class':'col-md-3'})
    for epi in epi_s :
        epi_url  = common.parseDOM(epi,'a',ret='href')[0]
        epi_img  = 'http:%s' %(common.parseDOM(epi,'img',ret='src')[0])
        epi_name = common.parseDOM(epi,'span',attrs={'class':'title'})[0]
        epi_name = common.replaceHTMLCodes(epi_name)
        epi_name = common.stripTags(epi_name).encode('utf-8')
        epi_name = epi_name.replace('\n',' : ').replace('  ','')
        plugin.log.debug('------------')
        plugin.log.debug('epi_name -> %s'%epi_name)
        plugin.log.debug('epi_url  -> %s'%epi_url)
        plugin.log.debug('epi_img  -> %s'%epi_img)
        plugin.log.debug('-----------')
        items.append({'label':epi_name,'path':plugin.url_for('play_video',url=epi_url),'icon':epi_img,'thumbnail':epi_img,'properties':{'Fanart_Image':__addon__.getAddonInfo('fanart')},'is_playable':True})
    plugin.set_content('tvshows')
    return items

@plugin.route('/play_video/<url>/')
def play_video(url):
    plugin.log.debug('play_video(%s)'%(url))
    video_id  = url.split('/')[-1] 
    plugin.log.debug('video_id : %s'%(video_id))
    video_url = get_video_url(video_id)
    plugin.set_resolved_url(video_url)    

# ------------------------------------
# -----------FUNCTIONS----------------
# ------------------------------------
def get_video_url(video_id):
    plugin.log.debug('get_video_url(%s)'%(video_id))
    url  = URL_VIDEO %(video_id)
    html = requests.get(url).text.encode('utf-8')
    plugin.log.debug(url)
    plugin.log.debug(html)
    video_index        = 0
    video_index_string = re.findall("""jwplayer\(idplayer\)\.playlistItem\((.+?)\)""", html)
    if video_index_string :
        plugin.log.debug('video_index:%s'%video_index_string[0])
        video_index = int(video_index_string[0])
    video_urls = re.findall("""file: \"(.+?)\"""", html)
    if video_urls :
        if video_index<len(video_urls) :
            video_url = video_urls[video_index]
        else :
            video_url = video_urls[0]
    else:
         video_url = False
    plugin.log.debug('video_url -> %s'%video_url)
    return video_url            

#------------------------------------    
#-------------MAIN-------------------
#------------------------------------  
if __name__ == '__main__':
    plugin.log.debug("===============================")
    plugin.log.debug("  Gulli Replay - Version: %s"%__version__)
    plugin.log.debug("===============================")
    plugin.run()