# -*- coding: utf-8 -*-
# v0.0.3 par JUL1EN094
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
    def __init__(self):
        self.URL_API         = 'http://api.allocine.fr/rest/v3/'
        self.PARTNER_ID      = '100043982026'
        self.PARTNER_KEY     = '29d185d98c984a359e6e6f26a0474269'
        self.USERAGENT       = "Dalvik/1.6.0 (Linux; U; Android 4.0.3; SGH-T989 Build/IML74K)"
        self.url             = False
        self.json            = False
        self.isSearch        = False
        self.isGet           = False
        
    def get(self,code=False,page=1,count=25):
        self.isGet = True
        query    = {}
        if code :
            query['code']      = str(code)
            query['profile']   = 'large'
            query['filter']    = 'movie'
            query["page"]  = str(page)
            query['count'] = str(count)
            query["partner"]   = self.PARTNER_ID
            query["format"]    = 'json'
            query["striptags"] = 'synopsis,synopsisshort'
            self.url   = self.getURL('movie',query)
            self.json  = self.getJson(self.url)
            return self.json            
        else :
            return False
    
    def search(self,searchtext=False,page=False,count=False):
        self.isSearch = True
        query       = {}
        query['q']  = self.getQuery(searchtext)
        if query['q'] :
            query['filter']  = 'movie'
            if page :
                query["page"]  = str(page)
            if count :
                query['count'] = str(count)
            query["count"]   = '25'
            query["partner"] = self.PARTNER_ID
            query["format"]  = 'json'
            self.url   = self.getURL('search',query)
            self.json  = self.getJson(self.url)
            return self.json
        else :
            return False
        
    def getWebContent(self,url) :
        req  = urllib2.Request(url)
        req.add_header('User-Agent',self.USERAGENT)           
        soup = urllib2.urlopen(req).read()
        return soup
        
    def getJson(self,url):
        return json.loads(self.getWebContent(url).decode('utf-8')) 
    
    def getQuery(self,query=False):
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
        sorted_token      = sorted(tokens.iteritems(), key=operator.itemgetter(1))
        tokensUrl         = ''
        for param in sorted_token :
            httpparam = '='.join(param)
            tokensUrl = tokensUrl+'&'+httpparam
            tokensUrl = tokensUrl.lstrip("&")    
        sig = urllib.quote(base64.b64encode(hashlib.sha1(self.PARTNER_KEY+tokensUrl+'&sed='+sed).digest()))
        return self.URL_API + route + '?' + tokensUrl + '&sed=' + sed + '&sig='+ sig
        
    def printResult(self):
        if self.isSearch or self.isGet :
            try :
                feed   = self.json['feed']
                movies = feed['movie']
            except :
                movies = self.json['movie']
            try :
                for movie in movies :
                    print '--------------'
                    print '--------------'
                    for info in movie.items():
                        try :
                            info0 = info[0].encode('utf-8')
                        except :
                            info0 = str(info[0])
                        try :
                            info1 = info[1].encode('utf-8')
                        except :
                            info1 = str(info[1])
                        print info0+' :'
                        print info1
                        print '-----'
                    print '--------------'
                    print '--------------'
            except:
                print '--------------'
                print '--------------'
                for info in movies.items():
                    try :
                        info0 = info[0].encode('utf-8')
                    except :
                        info0 = str(info[0])
                    try :
                        info1 = info[1].encode('utf-8')
                    except :
                        info1 = str(info[1])
                    print info0+' :'
                    print info1
                    print '-----'
                print '--------------'
                print '--------------'
                       
        else :
            return False