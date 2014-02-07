You can use this module to search and get Trailer from different sources (AlloCine, Google and Youtube,..)


Exemple code :

##### import ##### 
--
from getTrailer import getTrailer
--


##### main #####       
--
if __name__ == "__main__":
    x = getTrailer()

    Trailer = x.Search_onAlloCine(search=Searchtext,allo_filter='movie',TrailerQuality='hd')
    
    if not Trailer :
        Trailer = x.Search_onGoogle(search=Searchtext)
--