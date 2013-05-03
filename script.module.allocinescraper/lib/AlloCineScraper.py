# -*- coding: utf-8 -*-
# v0.0.2 par JUL1EN094
#---------------------------------------------------------------------
'''
    AlloCineScraper XBMC Module
    Copyright (C) 2013 JUL1EN094

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
'''
#---------------------------------------------------------------------

#IMPORTS
#xbmc
import xbmc
#time
import time
#web
import urllib, urllib2
#crypto
import base64, hashlib
#json
import simplejson as json
#json
import operator

class AlloCineScraper():    
    def __init__(self, q=False,mode='search'):
        self.query           = {}
        self.query['q']      = self.getQuery(q)
        if not self.query['q'] :
            return None
        self.query['filter'] = 'movie'
        self.mode            = 'search'
        self.URL_API         = 'http://api.allocine.fr/rest/v3/'
        self.PARTNER_ID      = '100043982026'
        self.PARTNER_KEY     = '29d185d98c984a359e6e6f26a0474269'
        self.USERAGENT       = "Dalvik/1.6.0 (Linux; U; Android 4.0.3; SGH-T989 Build/IML74K)"
        self.url             = self.getURL(self.mode,self.query)
        self.json            = self.getJson(self.url)
        
    def getWebContent(self,url) :
        req  = urllib2.Request(url)
        req.add_header('User-Agent',self.USERAGENT)           
        soup = urllib2.urlopen(req).read()
        return soup
        
    def getJson(self,url):
        return json.loads(self.getWebContent(url).decode('utf-8')) 
    
    def getQuery(self,query):
        if not query : 
            keyboard = xbmc.Keyboard('','Entrer le nom du film à scraper')
            keyboard.doModal()
            if (keyboard.isConfirmed()):
                query = keyboard.getText()
        if query :
            return urllib.quote(query)
        else :
            return False
    
    def getURL(self, route, tokens):
        sed               = time.strftime('%Y%m%d', time.localtime());
        tokens["page"]    = '1'
        tokens["count"]   = '25'
        tokens["partner"] = self.PARTNER_ID
        tokens["format"]  = 'json'
        sorted_token      = sorted(tokens.iteritems(), key=operator.itemgetter(1))
        tokensUrl         = ''
        for param in sorted_token :
            httpparam = '='.join(param)
            tokensUrl = tokensUrl+'&'+httpparam
            tokensUrl = tokensUrl.lstrip("&")    
        sig = urllib.quote(base64.b64encode(hashlib.sha1(self.PARTNER_KEY+tokensUrl+'&sed='+sed).digest()))
        return self.URL_API + route + '?' + tokensUrl + '&sed=' + sed + '&sig='+ sig
        
           