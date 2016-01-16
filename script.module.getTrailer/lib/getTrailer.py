# -*- coding: utf-8 -*-
# v0.0.2 par JUL1EN094
#---------------------------------------------------------------------
'''
    getTrailer XBMC Module
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
#xbmc 
import xbmc,xbmcgui
#---------------------------------------------------------------------

class getTrailer(): 
    """
    getTrailer class
    """    
    def __init__(self,search=False):
        self.search = search
        
    def Search_onAlloCine(self,search=False,allo_filter='movie',TrailerQuality='hd') :
        if not search :
            search = self.search
        # import allocinescraper
        from AlloCineScraper import AlloCineScraper
        allo = AlloCineScraper()
        # grab infos
        allo_infos      = {}
        allo_infos      = allo.grab(searchtext=search,maxTrailerQuality=TrailerQuality,filters=allo_filter)
        # return Trailer or False
        if 'Trailer' in allo_infos :
            return allo_infos['Trailer']
        else :
            return False
            
    def Search_onGoogle(self,search=False,manual=False) :
        if not search :
            search = self.search
        res_name = []
        res_url = []
        res_name.append('Rechercher manuellement')
        if manual:
            results = self.Search_YTonGoogle(search)
            for res in results:
                if 'www.youtube.com/watch' in res.url:
                    res_name.append(res.title.encode('utf8'))
                    res_url.append(res.url.encode('utf8'))
        else:
            results = self.Search_YTonGoogle(search+' bande annonce')
            for res in results:
                if 'www.youtube.com/watch' in res.url:
                    res_name.append(res.title.encode('utf8'))
                    res_url.append(res.url.encode('utf8'))    
        dialog = xbmcgui.Dialog()
        ret = dialog.select('Recherche de bande annonce : '+search,res_name)    
        # Manual search for trailer
        if ret == 0:
            if manual:
                default = search
                title   = 'Recherche manuelle de B.A. pour '+search
            else:
                default = search+' bande annonce'
                title   = 'Recherche manuelle de B.A. pour '+search
            keyboard = xbmc.Keyboard(default, title)
            keyboard.doModal()        
            if keyboard.isConfirmed():
                result = keyboard.getText()
                return self.Search_onGoogle(search=result,manual=True) 
        # return Trailer or False
        elif ret >= 1:
            trailer_url = res_url[ret-1]
            return trailer_url
        else:
            return False

    def Search_YTonGoogle(self,search):
        # import Google Search
        from xgoogle.search import GoogleSearch
        # search on google
        gs = GoogleSearch(search+' site:http://www.youtube.com ')
        gs.results_per_page = 25
        gs.page = 0
        # return result or None
        try:
            results = gs.get_results()
            return results
        except Exception, e:
            print 'getTrailer --> Error: %s' % e
            return None