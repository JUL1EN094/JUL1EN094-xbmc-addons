#-*- coding: utf-8 -*-

import os
import xbmc
import xbmcaddon
import xbmcgui
import shutil

__addonID__   = 'script.module.metahandler'
__addon__     = xbmcaddon.Addon( __addonID__ )

ROOTDIR                  = __addon__.getAddonInfo('path')
ADDON_DATA               = xbmc.translatePath( "special://profile/addon_data/script.module.metahandler/")

METAFOLDER = __addon__.getSetting('meta_folder_location')
METAFOLDER = xbmc.translatePath(METAFOLDER)
if not METAFOLDER :
    METAFOLDER = ADDON_DATA
METAFOLDER = os.path.join(METAFOLDER, 'meta_cache')

DBLOCATION = os.path.join(METAFOLDER,'video_cache.db')


def remove_DataBase() :
    xbmc.log("metahandler - deleting database...")
    if os.path.exists(DBLOCATION) :
        os.remove(DBLOCATION)
    xbmcgui.Dialog().ok("Metahandler", "Database deleted")    
    xbmc.log("Metahandler - Clearing database cache. Done!")

    
if ( __name__ == "__main__" ):
    remove_DataBase()
