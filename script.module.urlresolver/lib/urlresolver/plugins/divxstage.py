'''
divxstage urlresolver plugin
Copyright (C) 2011 t0mm0, DragonWin

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
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class DivxstageResolver(UrlResolver):
    name = 'divxstage'
    domains = ['divxstage.eu', 'divxstage.net', 'divxstage.to', 'cloudtime.to']
    pattern = '(?://|\.)(divxstage.eu|divxstage.net|divxstage.to|cloudtime.to)/(?:video/|embed/\?v=)([A-Za-z0-9]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        sources = []
        for idx, match in enumerate(re.finditer('<source src="([^"]+)"', html, re.DOTALL)):
            sources.append(('Mirror ' + str(idx + 1), match.group(1)))

        if not sources:
            raise ResolverError('File not found')
        source = helpers.pick_source(sources, self.get_setting('auto_pick') == 'true')
        return source

    def get_url(self, host, media_id):
        return 'http://www.cloudtime.to/embed/?v=%s' % media_id
