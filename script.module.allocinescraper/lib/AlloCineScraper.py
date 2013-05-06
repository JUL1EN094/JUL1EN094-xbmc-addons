# -*- coding: utf-8 -*-
# v0.0.6 par JUL1EN094
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
#regex
import re
#time
import time, datetime
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
        self.filters         = False
        
    def get(self,code=False,page=1,count=25,filters='movie'):
        self.filters = filters
        query        = {}
        if code :
            if page :
                query["page"]  = str(page)
            else :
                query['page']  = '1'
            if count :
                query['count'] = str(count)
            else :
                query["count"] = '25'
            query['code']      = str(code)
            query['profile']   = 'large'
            query['filter']    = self.filters
            query['partner']   = self.PARTNER_ID
            query['format']    = 'json'
            query['striptags'] = 'synopsis,synopsisshort'
            self.url   = self.getURL(self.filters,query)
            self.json  = self.getJson(self.url)
            return self.json            
        else :
            return False
    
    def search(self,searchtext=False,page=False,count=False,filters='movie'):
        self.filters = filters
        query        = {}
        query['q']   = self.getQuery(searchtext)
        if query['q'] :
            if page :
                query["page"]  = str(page)
            else :
                query['page']  = '1'
            if count :
                query['count'] = str(count)
            else :
                query["count"] = '25'
            query['filter']  = self.filters
            query["partner"] = self.PARTNER_ID
            query["format"]  = 'json'
            self.url   = self.getURL('search',query)
            self.json  = self.getJson(self.url)
            return self.json
        else :
            return False
            
    def searchFirstAndFull(self,searchtext=False, filters='movie'):
        #search first result
        self.search(searchtext=searchtext,page=1,count=1,filters=filters)
        #if result
        if self.json :
            movie_s = self.getMoviesList()
            if movie_s :
                movie = movie_s[0]
                #get movie code
                code  = movie['code']
                #get full infos
                self.get(code=code,filters=self.filters)
                return self.json  
            else :
                return False              
        else :
            return False
        
    def getJson(self,url):           
        return json.loads(self.getWebContent(url).decode('utf-8')) 
    
    def getMoviesList(self):
        if self.json :
            try :
                feed   = self.json['feed']
                movies = feed[self.filters]
            except :
                try :
                    movies = self.json[self.filters] 
                except :
                    return False
            # un seul film : on met le dict dans une liste
            if type(movies) == dict :
                ls = []
                ls.append(movies)
                movies = ls
            return movies            
        else :
            return False
    
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
    
    def getTrailersUrl(self, code):
        media_url  = "http://www.allocine.fr/skin/video/AcVisionData_xml.asp?media=%s" % str(code)
        media_data = self.getWebContent(media_url)
        media      = {}
        match      = re.search( '<AcVisionVideo(.*?)/>', media_data , re.DOTALL )
        if match: 
            media_data = match.group(1)
        else :
            print "allocinescrapper : problème de récupération de la bande annonce"
            return False
        match      = re.search( 'title="(.*?)"', media_data )
        #Titre : 
        if match: 
            media["Title"] = match.group(1)
        else: 
            media["Title"] = ""
        print "allocinescrapper :récupération info média: %s" % media["Title"]
        #qualité
        for video_quality in [ "ld" , "md" , "hd"]:
            match = re.search( '%s_path="(.*?)"' % video_quality , media_data )
            if match: 
                media[video_quality] = match.group(1)
            else: 
                media[video_quality] = ""
        return media
    
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
        
    def getWebContent(self,url) :
        req  = urllib2.Request(url)
        req.add_header('User-Agent',self.USERAGENT)           
        soup = urllib2.urlopen(req).read()
        return soup
        
    def getXbmcDict(self,movieDict) :
        xbmcDict = {}
        # Année
        if 'productionYear' in movieDict : xbmcDict['Year']          = int(movieDict['productionYear'])
        # Synopsis court
        if 'synopsisShort'  in movieDict : xbmcDict['PlotOutline']   = movieDict['synopsisShort'] 
        # Titre
        if 'title'          in movieDict : xbmcDict['Title']         = movieDict['title'] 
        # Titre original
        if 'originalTitle'  in movieDict : xbmcDict['OriginalTitle'] = movieDict['originalTitle'] 
        # Synopsis
        if 'synopsis'       in movieDict : xbmcDict['Plot']          = movieDict['synopsis'] 
        # Durée
        if 'runtime'        in movieDict : xbmcDict['Duration']      = int(movieDict['runtime']/60) 
        # Vote et note
        if 'statistics' in movieDict : 
            statdict = movieDict['statistics']
            if 'userRating'      in statdict : xbmcDict['Rating'] = float(statdict['userRating']*2) 
            if 'userRatingCount' in statdict : xbmcDict['Vote']   = int(statdict['userRatingCount'])
        # Genre
        if 'genre' in movieDict : 
            genrelist = movieDict['genre']
            genres    = []
            for genre in genrelist :
                genres.append(genre['$'])
            xbmcDict['Genre'] = genres[0]
            if len(genres) > 1:
                n = 1
                while n < len(genres):
                    xbmcDict['Genre'] = xbmcDict['Genre']+', '+genres[n]
                    n+=1
        # Nationalité
        if 'nationality' in movieDict : 
            nationalitylist = movieDict['nationality']
            nationalities   = []
            for nationality in nationalitylist :
                nationalities.append(nationality['$'])
            xbmcDict['Country'] = nationalities[0]
            if len(nationalities) > 1:
                n = 1
                while n < len(nationalities):
                    xbmcDict['Country'] = xbmcDict['Country']+', '+nationalities[n]
                    n+=1
        # Affiche
        if 'poster' in movieDict : 
            posterdict = movieDict['poster']
            if 'href' in posterdict : xbmcDict['Thumb'] = posterdict['href']
        # Date de sortie
        if 'release' in movieDict : 
            releasedict = movieDict['release']
            if 'releaseDate' in releasedict : 
                ymd = re.search('([1900-3000])-([0-12])-([0-31])',releasedict['releaseDate'])
                if ymd :
                    xbmcDict['Date'] = ymd.group(2)+'-'+ymd.group(1)+'-'+ymd.group(0)
        # Acteurs et réalisateurs
        if 'castingShort' in movieDict : 
            castingShortdict = movieDict['castingShort']
            #realisateurs
            if 'directors' in castingShortdict :  xbmcDict['Director'] = castingShortdict['directors']
            #acteurs
            if 'actors'    in castingShortdict :  xbmcDict['Cast'] = castingShortdict['actors']
        # Bande Annonce
        if 'trailer' in movieDict :
            trailerDict = movieDict['trailer']
            if 'code' in trailerDict : 
                trailerCode = trailerDict['code']
                trailersurl = []
                trailersurl = self.getTrailersUrl(trailerCode)
                if (trailersurl['hd']) and (trailersurl['hd'] != ''):
                    xbmcDict['Trailer'] = trailersurl['hd']
                elif (trailersurl['md']) and (trailersurl['md'] != ''):
                    xbmcDict['Trailer'] = trailersurl['md']
                elif (trailersurl['ld']) and (trailersurl['ld'] != ''):
                    xbmcDict['Trailer'] = trailersurl['ld']
        return xbmcDict         
                   
    def grab(self,searchtext=False, codeid=False, filters='movie') :
        if searchtext :
            self.searchFirstAndFull(searchtext,filters=filters)
            moviedict_s = self.getMoviesList()
            if moviedict_s :
                moviedict = moviedict_s[0]
                return self.getXbmcDict(moviedict)
            else :
                return {}
        elif codeid :
            self.get(codeid, filters=filters)
            moviedict_s = self.getMoviesList()
            if moviedict_s :
                moviedict = moviedict_s[0]
                return self.getXbmcDict(moviedict)
            else :
                return {}
        else :
            return {}
    
    def printMovieInfos(self,movie=False):
        if type(movie) == dict :
            for info in movie.items():
                print '-----'
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
        else :
            return False
    
    def printResult(self):
        movies = self.getMoviesList()
        if movies :
            for movie in movies :
                print '--------------'
                print '--------------'
                self.printMovieInfos(movie)
                print '--------------'
                print '--------------'                       
        else :
            return False
            
