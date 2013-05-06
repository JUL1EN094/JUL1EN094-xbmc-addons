You can use this module to grab movies infolabel from AlloCine API v3 (with sed and sig).


Exemple code :

##### import ##### 
--
from AlloCineScraper import AlloCineScraper
--


##### main #####       
--
if __name__ == "__main__":
    x = AlloCineScraper()
--


##### Get Original json from api (set x.json variable - can takes 'filters' arg) ##### 
--
   Search exemples :
   x.search()
or  
   x.search('Avatar',filter='movie')
-- 
   get exemple :
   x.get(139291)


##### jsonfile variable (after a get or a search call) ##### 
    x.json


##### print prettify ##### 
    x.printResult()

## you can specified for each call (get and search) these param :
    count (as the API's page param - Default 25)
    page  (as the API's page param - Default 1 )
    filters (as the API's filter param - Default 'movie')

##########################################################################################
##########################################################################################
###################################### EASY METHODS ######################################
##########################################################################################
########################################################################################## 

##### searchFirstAndFull(self,searchtext=False) #####
x.searchFirstAndFull("Avatar") -->return json file with full infos of first result 


##### getMoviesList(self) #####
-- can be use after a search, get call
x.searchFirstAndFull("Who's the boss", 'filters'='tvseries')
ls = []
ls = x.getMoviesList() --> return a list of movieDict (json format) or return False


#####  printMovieInfos(self,movie) ##### 
-- movie must be an item of the return of getmovieList() function 
x.searchFirstAndFull("Avatar")
ls  = []
ls  = x.getMoviesList()
if ls :
    x.printMovieInfos(ls[0]) --> print a prettify version of the movie's info

##### getTrailersUrl(self, code): #####
-- code must be the allocine movie id 
url = getTrailersUrl(4567) --> return trailer's url (best quality) of the movie


##### getXbmcDict(self,movieDict): #####
-- movieDict must be an item of the return of getmovieList() function 
x.searchFirstAndFull("Avatar")
dic = {}
ls  = []
ls  = x.getMoviesList()
if ls :
    dic = getXbmcDict(ls[0]) --> return dict of movie's infos formatted for xbmc, with item name same as xbmc infolabels

##########################################################################################
##########################################################################################
###################################### XBMC  GRAB   ######################################
##########################################################################################
##########################################################################################

##### grab(self,searchtext=False, codeid=False,filters='movie'): #####    
-- must be use either with 'searchtext' param or with 'codeid' param
dic = {}
dic = x.grab(searchtext="Avatar") --> return dict of movie's infos formatted for xbmc, with item name same as xbmc infolabels and with Trailer.






