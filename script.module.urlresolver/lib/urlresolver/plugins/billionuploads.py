'''
Billionuploads urlresolver plugin
Copyright (C) 2013 jas0npc

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

import re, xbmcgui, time, os
from urlresolver import common
from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
net = Net()

#SET ERROR_LOGO# THANKS TO VOINAGE, BSTRDMKR, ELDORADO
error_logo = os.path.join(common.addon_path, 'resources', 'images', 'redx.png')

class billionuploads(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "billionuploads"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_media_url(self, host, media_id):
        try:
            url = 'http://'+host+'/'+media_id
            dialog = xbmcgui.DialogProgress()
            dialog.create('Resolving', 'Resolving BillionUploads Link...')       
            dialog.update(0)
        
            html = net.http_GET(url).content
            if re.search('File Not Found', html):
                common.addon.log_error('BillionUploads - File Not Found')
                raise Exception ('File Not Found or removed')
            common.addon.show_countdown(3, title='BillionUploads', text='Loading Video...')
            
            data = {}
            r = re.findall(r'type="hidden" name="(.+?)" value="(.+?)">', html)
            for name, value in r:
                data[name] = value

            captchaimg = re.search('<img src="((?:http://|www\.)?BillionUploads.com/captchas/.+?)"', html)
        
            if captchaimg:
                dialog.close()
                img = xbmcgui.ControlImage(550,15,240,100,captchaimg.group(1))
                wdlg = xbmcgui.WindowDialog()
                wdlg.addControl(img)
                wdlg.show()
        
                time.sleep(3)
        
                kb = xbmc.Keyboard('', 'Type the letters in the image', False)
                kb.doModal()
                capcode = kb.getText()
        
                if (kb.isConfirmed()):
                    userInput = kb.getText()
                    if userInput != '':
                        capcode = kb.getText()
                    elif userInput == '':
                        common.addon.show_error_dialog("You must enter the text from the image to access video")
                        return False
                else:
                    return False
                wdlg.close()
                dialog.close() 
                dialog.create('Resolving', 'Resolving BillionUploads Link...') 
                dialog.update(50)
                data.update({'code':capcode})

            else:  
                dialog.create('Resolving', 'Resolving BillionUploads Link...') 
                dialog.update(50)
                    
            html = net.http_POST(url, data).content
            dialog.update(100)
            link = re.search('&product_download_url=(.+?)"', html).group(1)
            link = link + "|referer=" + url
            dialog.close()
            mediaurl = link
        
            return mediaurl

        except Exception, e:
            common.addon.log_error('**** BillionUploads Error occured: %s' % e)
            common.addon.show_small_popup(title='[B][COLOR white]BILLIONUPLOADS[/COLOR][/B]', msg='[COLOR red]%s[/COLOR]' % e, delay=5000, image=error_logo)
            return False
    
    def get_url(self, host, media_id):
        return 'http://www.BillionUploads.com/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search('//(.+?)/([0-9a-zA-Z]+)',url)
        if r:
            return r.groups()
        else:
            return False
        return ('host', 'media_id')

    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return (re.match('http://(www.)?[bB]illion[uU]ploads.com/' +
                         '[0-9A-Za-z]+', url) or
                         '[bB]illion[uU]ploads' in host)
