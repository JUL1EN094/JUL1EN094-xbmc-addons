"""    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
    
    Special thanks for help with this resolver go out to t0mm0,
    mash2k3, Mikey1234,voinage and of course Eldorado. Cheers guys :)
"""

import os, urllib2, re
from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
from urlresolver import common
from lib import jsunpack
net = Net()

#SET ERROR_LOGO# THANKS TO VOINAGE, BSTRDMKR, ELDORADO
error_logo = os.path.join(common.addon_path, 'resources', 'images', 'redx.png')

class vidto(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "vidto"
    profile_path = common.profile_path

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()
        
    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)+'.html'
        try:
            html = self.net.http_GET(web_url).content
            r = re.findall(r'<font class="err">File was removed</font>',html,re.I)
            if r:
                common.addon.log_error(self.name + ': File was removed')
                common.addon.show_small_popup(title='[B][COLOR white]VIDTO.ME[/COLOR][/B]', msg='[COLOR red]No such file or the file has been removed[/COLOR]', delay=5000, image=error_logo)
                return False            
            if not r:
                r = re.findall(r'(eval\(function\(p,a,c,k,e,d\)\{while.+?flvplayer.+?)</script>'
                               ,html,re.M|re.DOTALL)
                if r:
                    unpacked = jsunpack.unpack(r[0])
                    r = re.findall(r'label:"360p",file:"(.+?)"}',unpacked)
                if not r:
                    r = re.findall('type="hidden" name="(.+?)" value="(.+?)">',html)
                    post_data = {}
                    for name, value in r:
                        post_data[name] = value
                    post_data['usr_login'] = ''
                    post_data['referer'] = web_url
                    common.addon.show_countdown(7, 'Please Wait', 'Resolving')
                    html = net.http_POST(web_url,post_data).content
                    r = re.findall(r'(eval\(function\(p,a,c,k,e,d\)\{while.+?flvplayer.+?)</script>'
                                   ,html,re.M|re.DOTALL)
                    if r:
                        unpacked = jsunpack.unpack(r[0])
                        r = re.findall(r'label:"360p",file:"(.+?)"}',unpacked)
                    if not r:
                        r = re.findall(r"var file_link = '(.+?)';",html)
            return r[0]            
        except urllib2.URLError, e:
            common.addon.log_error(self.name + ': got http error %d fetching %s' %
                                   (e.code, web_url))
            common.addon.show_small_popup('Error','Http error: '+str(e), 5000, error_logo)
            return False
        except Exception, e:
            common.addon.log_error('**** Vidto.me Error Occured : %s' % e)
            common.addon.show_small_popup('Error','An error has occured, unable to resolve link', 5000, error_logo)
            return False
        
    def get_url(self, host, media_id):
        return 'http://www.vidto.me/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search('//(.+?)/([0-9A-Za-z]+)',url)
        if r:
            return r.groups()
        else:
            return False
        return ('host', 'media_id')
        

    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return (re.match('http://(www.)?vidto.me/' +
                         '[0-9A-Za-z]+', url) or 'vidto.me' in host)

