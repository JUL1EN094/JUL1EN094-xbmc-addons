#-*- coding: utf-8 -*-
"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import random
import re
import urllib, urllib2
import ast
import xbmc
import time
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import SiteAuth
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
from urlresolver import common
import xbmc,xbmcplugin,xbmcgui,xbmcaddon, datetime
import cookielib
from t0mm0.common.net import Net
import json


class purevid(Plugin, UrlResolver, SiteAuth, PluginSettings):
    implements = [UrlResolver, SiteAuth, PluginSettings]
    name = "purevid"
    profile_path = common.profile_path    
    cookie_file = os.path.join(profile_path, '%s.cookies' % name)
    
    def __init__(self):
        p = self.get_setting('priority') or 1
        self.priority = int(p)
        self.net = Net()
        try:
            os.makedirs(os.path.dirname(self.cookie_file))
        except OSError:
            pass

    #UrlResolver methods
    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        try:
            html = self.net.http_GET(web_url).content
        except urllib2.URLError, e:
            common.addon.log_error(self.name + '- got http error %d fetching %s' %
                                   (e.code, web_url))
            return False
        
        data = json.loads(html)                
        url = data['clip']['bitrates'][-1]['url']        
        params = ''
        for val in data['plugins']['lighttpd']['params'] :
            params += val['name'] + '=' + val['value'] + '&'
        
        url =  url + '?' + params[:-1]
        
        cookies = {}
        for cookie in self.net._cj:
            cookies[cookie.name] = cookie.value
            
        url = url + '|' + urllib.urlencode({'Cookie' :urllib.urlencode(cookies)}) 
        print url
        return url
                                                                                            
    def get_url(self, host, media_id):
        return 'http://www.purevid.com/?m=video_info_embed_flv&id=%s' % media_id
                        
    def get_host_and_id(self, url):     
        r = re.search('//(.+?)/v/([0-9A-Za-z]+)', url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):                 
        if self.get_setting('login') == 'false':        
            return False
        print url
        return 'purevid' in url

    #SiteAuth methods
    def login(self):
        print 'login to purevid'
        url = 'http://www.purevid.com/?m=login'
                        
        data = {'username' : self.get_setting('username'), 'password' : self.get_setting('password')}        
        source = self.net.http_POST(url,data).content        
                
        if re.search(self.get_setting('username'), source):            
            self.net.save_cookies(self.cookie_file)
            self.net.set_cookies(self.cookie_file)
            return True
        else:
            return False
                    
    #PluginSettings methods
    def get_settings_xml(self):
        xml = PluginSettings.get_settings_xml(self)
        xml += '<setting id="purevid_login" '        
        xml += 'type="bool" label="login" default="false"/>\n'
        xml += '<setting id="purevid_username" enable="eq(-1,true)" '
        xml += 'type="text" label="username" default=""/>\n'
        xml += '<setting id="purevid_password" enable="eq(-2,true)" '
        xml += 'type="text" label="password" option="hidden" default=""/>\n'
        return xml
       
