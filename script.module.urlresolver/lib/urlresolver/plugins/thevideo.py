'''
thevideo urlresolver plugin
Copyright (C) 2014 Eldorado

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import re, urllib2, os, xbmcgui
from urlresolver import common
from lib import jsunpack

#SET ERROR_LOGO# THANKS TO VOINAGE, BSTRDMKR, ELDORADO
error_logo = os.path.join(common.addon_path, 'resources', 'images', 'redx.png')

USER_AGENT='Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:30.0) Gecko/20100101 Firefox/30.0'

class SharesixResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "thevideo"


    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()


    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        try:
            headers = {
                'User-Agent': USER_AGENT,
                'Referer': web_url
            }

            html = self.net.http_GET(web_url).content

            if 'File Not Found' in html:
                raise Exception ('File Not Found or removed')

            count = 0
            while "Proceed to video" in html:
                if count > 3:
                    raise Exception ('Unable to resolve TheVideo link. Player config not found.')
                data = {}
                
                r = re.findall(r'name: \'(.+?)\', value: \'(.+?)\'', html)
                for name, value in r:
                    data[name] = value
                
                r = re.findall(r'type="hidden"\s*name="(.+?)"\s*value="(.*?)"', html)
                for name, value in r:
                    data[name] = value
                data[u"imhuman"] = "Proceed to video"; 
                html = self.net.http_POST(web_url, data, headers=headers).content
                count += 1

            r = re.search("<script type='text/javascript'>eval(.*?)</script>",html,re.DOTALL)
            if not r:
                raise Exception ('Unable to resolve TheVideo link. Player config not found.')
            js = jsunpack.unpack(r.group(1))
            r = re.search('file:"(.+?)"', js.replace("\\'", ""))
            if not r:
                raise Exception('Unable to locate link')
            else:
                stream_url=r.group(1)+'?start=0'
                return stream_url + '|Referer=http://www.thevideo.me/player_custom/player.swf'

        except urllib2.HTTPError, e:
            common.addon.log_error(self.name + ': got http error %d fetching %s' %
                                   (e.code, web_url))
            common.addon.show_small_popup('Error','Http error: '+str(e), 5000, error_logo)
            return self.unresolvable(code=3, msg=e)
        except Exception, e:
            common.addon.log_error('**** TheVideo Error occured: %s' % e)
            common.addon.show_small_popup(title='[B][COLOR white]THEVIDEO[/COLOR][/B]', msg='[COLOR red]%s[/COLOR]' % e, delay=5000, image=error_logo)
            return self.unresolvable(code=0, msg=e)


    def get_url(self, host, media_id):
        return 'http://%s/%s' % (host, media_id)


    def get_host_and_id(self, url):
        r = re.search('//(.+?)/([0-9a-zA-Z/]+)', url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return (re.match('http://(www\.|embed-)?thevideo.me/' +
                         '[0-9A-Za-z]+', url) or
                         'thevideo' in host)
