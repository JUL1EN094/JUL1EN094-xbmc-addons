'''
Allmyvideos urlresolver plugin
Copyright (C) 2013 Vinnydude

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

import re
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError
import xbmc

class MooShareResolver(UrlResolver):
    name = "mooshare"
    domains = ["mooshare.biz"]
    pattern = '(?://|\.)(mooshare\.biz)/(?:embed-|iframe/)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        url = self.get_url(host, media_id)
        html = self.net.http_GET(url).content

        data = {}
        if '<form role="search"' in html and '<Form method="POST" action=\'\'>' in html: html = html.split('<Form method="POST" action=\'\'>')[1]
        r = re.findall(r'type="hidden" name="(.+?)"\s* value="?(.+?)">', html)
        for name, value in r:
            data[name] = value
        data[u'referer'] = ''
        data[u'usr_login'] = ''
        data[u'imhuman'] = 'Proceed to video'
        data[u'btn_download'] = 'Proceed to video'
        xbmc.sleep(5000)
        html = self.net.http_POST(url, data).content

        r = re.search('file\s*:\s*"(.+?)"', html)
        if r:
            return r.group(1)
        else:
            raise ResolverError('could not find video')

    def get_url(self, host, media_id):
        return 'http://mooshare.biz/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
