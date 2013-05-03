Exemple code :

## import
from AlloCineScraper import AlloCineScraper


## main      
if __name__ == "__main__":
    x = AlloCineScraper()


## Search exemples :
   x.search()
or  
   x.search('Avatar')


## get exemple :

    x.get(139291)


## print prettify
    x.printResult()

## jsonfile variable (after a get or a search call) :
    x.json

## you can specified for each call (get and search) these param :
    count (as the API's page param - Default 25)
    page  (as the API's page param - Default 1 )