'''
    StreamLauncherDownloader for StreamLauncher XBMC Module
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

#-*- coding: utf-8 -*-
# Version 0.1 par JUL1EN094

"""Downloads files from http or ftp locations"""
import os,stat
import urllib2
import ftplib
import urlparse
import urllib
import sys
import socket
import time
import struct
import threading
#modif and validate string
import unicodedata
import string
validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
# print_exc
from traceback import print_exc
 
version = "1.0.0"

class CDownload(object):
    #DOWNLOAD STATUS
    DOWNLOADING = 1
    PAUSED = 2
    STOPPED = 3
    ERROR = 4
    CONNECTING = 5
    UNDEFINED = 6
    FINISHED = 7

class DownloadFile(threading.Thread):
    """This class is used for downloading files from the internet via http or ftp.
    It supports basic http authentication and ftp accounts, and supports resuming downloads. 
    It does not support https or sftp at this time.
    
    The main advantage of this class is it's ease of use, and pure pythoness. It only uses the Python standard library, 
    so no dependencies to deal with, and no C to compile.
    
    #####
    If a non-standard port is needed just include it in the url (http://example.com:7632).
    
    Basic usage:
        Simple
            downloader = StreamLauncherDownloader.DownloadFile('http://example.com/file.zip')
            downloader.download()
         Use full path to download
             downloader = StreamLauncherDownloader.DownloadFile('http://example.com/file.zip', "C:/Users/username/Downloads/newfilename.zip")
             downloader.download()
         Basic Authentication protected download
             downloader = StreamLauncherDownloader.DownloadFile('http://example.com/file.zip', "C:/Users/username/Downloads/newfilename.zip", ('username','password'))
             downloader.download()
         Resume
             downloader = StreamLauncherDownloader.DownloadFile('http://example.com/file.zip')
            downloader.resume()
    """        
    
    def __init__(self, url, localDir, auth=None, timeout=20.0, autoretry=False, retries=20,cache_size = 5 * 1024 * 1024 * 1024):
        """Note that auth argument expects a tuple, ('username','password')"""
        threading.Thread.__init__(self)
        self.url = url
        self.urlFileName = None
        self.progress = 0
        self.fileSize = None
        self.UrlFileSize = None
        self.type = self.getType()
        self.auth = auth
        self.timeout = timeout
        self.retries = retries
        self.curretry = 0
        self.cur = 0
        self.status = CDownload.UNDEFINED
        self.urlFilesize = self.getUrlFileSize()
        self.timer = 0
        self.cache_size = cache_size
        self.localdir = localDir
        self.localFileName =  os.path.join(localDir,self.RemoveDisallowedFilenameChars(self.getUrlFilename(self.url))[:128])
    
    
    def run(self, callBack=None):
        """attempts to resume file download"""
#         if self._check_cache() :
        if self.status != CDownload.STOPPED :
            try :
                self.curretry = 0
                self.status = CDownload.CONNECTING
                type = self.getType()
                if type == 'http':
                    self.__startHttpResume__(callBack=callBack)
                elif type == 'ftp':
                    self.__startFtpResume__()
            except :
                print_exc()
                self.__retry__()
        else :
            pass    
    
    def __downloadFile__(self, urlObj, fileObj, callBack=None):
        print """starts the download loop""" + self.url
        self.fileSize = self.getUrlFileSize()
        while self.status == CDownload.DOWNLOADING or self.status==CDownload.PAUSED:
            try:
                data = urlObj.read(8192)
            except (socket.timeout, socket.error) as t:
                print "caught ", t
                self.__retry__()
                break
            if not data:
                if int(self.cur) == int(self.fileSize) :
                    self.status = CDownload.FINISHED
                else :
                    print 'error on size'
                    print self.cur
                    print self.fileSize
                    self.__retry__()
#                     self.status = CDownload.ERROR
#                 fileObj.close()
                break
            else :
                fileObj.write(data)
                self.cur += len(data)
                if self.status==CDownload.PAUSED :
                    time.sleep(1)
        if callBack:
           callBack(cursize=self.cur)
            
    def __retry__(self):
        """auto-resumes up to self.retries"""
        if self.retries > self.curretry:
                print 'RETRY : '+str(self.curretry)
                time.sleep(2)
                self.curretry += 1
                if self.getLocalFileSize() != self.urlFilesize:
                    self.run()
        else:
            self.status = CDownload.ERROR
            print 'retries all used up'
            return False, "Retries Exhausted"
                    
    def __authHttp__(self):
        """handles http basic authentication"""
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        # this creates a password manager
        passman.add_password(None, self.url, self.auth[0], self.auth[1])
        # because we have put None at the start it will always
        # use this username/password combination for  urls
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        # create the AuthHandler
        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)
        
    def __authFtp__(self):
        """handles ftp authentication"""
        ftped = urllib2.FTPHandler()
        ftpUrl = self.url.replace('ftp://', '')
        req = urllib2.Request("ftp://%s:%s@%s"%(self.auth[0], self.auth[1], ftpUrl))
        req.timeout = self.timeout
        ftpObj = ftped.ftp_open(req)
        return ftpObj

    def RemoveDisallowedFilenameChars(self,filename):
        cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
        return ''.join(c for c in cleanedFilename if c in validFilenameChars)
        
    def _throwUnecessaryResumeData(self,urllib2Obj):
        #get 256 last byte in already downloaded file
        f = open(self.localFileName,'rb')
        f.seek(-256,os.SEEK_END)
        tofind = f.read(256)
        f.close()           
        #read http data until we have the last bytes of local file
        pos = 0            
        print len(tofind)
        while pos < len(tofind) :
            byte = urllib2Obj.read(1)
            if not byte :
               break
            if ord(byte) == ord(tofind[pos]):
               pos += 1
            else :
               pos = 0
                    
    def __startHttpResume__(self, restart=None, callBack=None):
        print """starts to resume HTTP"""
        curSize = self.getLocalFileSize()
        if curSize == self.getUrlFileSize() :
            #already downloaded
            return True
        if not curSize or restart:
            #print 'File_not exist or force restart'
            self.download(callBack)
            return True
        self.cur = curSize
        if self.auth:
            self.__authHttp__()
        urllib2Obj = self.seektoresume()        
        f = open(self.localFileName , "ab")
        if self.status != CDownload.STOPPED : 
            self.status = CDownload.DOWNLOADING
            self.__downloadFile__(urllib2Obj, f, callBack=callBack)

    def seektoresume(self) :
        req = urllib2.Request(self.url)
        req.headers['Range'] = 'bytes=%s-%s' % (self.cur, self.getUrlFileSize())
        urllib2Obj = urllib2.urlopen(req, timeout=self.timeout)
        return urllib2Obj
        
    def __startFtpResume__(self, restart=None):
        """starts to resume FTP"""
        if restart:
            f = open(self.localFileName , "wb")
        else:
            f = open(self.localFileName , "ab")
        ftper = ftplib.FTP(timeout=60)
        parseObj = urlparse.urlparse(self.url)
        baseUrl= parseObj.hostname
        urlPort = parseObj.port
        bPath = os.path.basename(parseObj.path)
        gPath = parseObj.path.replace(bPath, "")
        unEncgPath = urllib.unquote(gPath)
        fileName = urllib.unquote(os.path.basename(self.url))
        ftper.connect(baseUrl, urlPort)
        ftper.login(self.auth[0], self.auth[1])
        if len(gPath) > 1:
            ftper.cwd(unEncgPath)
        ftper.sendcmd("TYPE I")
        ftper.sendcmd("REST " + str(self.getLocalFileSize()))
        downCmd = "RETR "+ fileName
        ftper.retrbinary(downCmd, f.write)
        
    def getUrlFilename(self, url):
        """returns filename from url"""
        return urllib.unquote(os.path.basename(url)).decode('utf-8')
        
    def getUrlFileSize(self):
        """gets filesize of remote file from ftp or http server"""
        if not self.UrlFileSize :
            if self.type == 'http':
                if self.auth:
                    authObj = self.__authHttp__()
                print self.url
                n = 0
                while n<=5 and not self.UrlFileSize :
                    try :
                        urllib2Obj = urllib2.urlopen(self.url, timeout=10)
                        size = urllib2Obj.headers.get('content-length')
                        self.UrlFileSize =  size
                    except :
                        n += 1                        
        return self.UrlFileSize 
    
    def getLocalFileSize(self):
        """gets filesize of local file"""
        try :
            size = os.stat(self.localFileName).st_size
            return size
        except :
            return False
        
    def getType(self):
        """returns protocol of url (ftp or http)"""
        type = urlparse.urlparse(self.url).scheme
        return type 
        
    def checkExists(self):
        """Checks to see if the file in the url in self.url exists"""
        if self.auth:
            if self.type == 'http':
                authObj = self.__authHttp__()
                try:
                    urllib2.urlopen(self.url, timeout=self.timeout)
                except urllib2.HTTPError:
                    return False
                return True
            elif self.type == 'ftp':
                return "not yet supported"
        else:
            urllib2Obj = urllib2.urlopen(self.url, timeout=self.timeout)
            try:
                urllib2.urlopen(self.url, timeout=self.timeout)
            except urllib2.HTTPError:
                return False
            return True

    def download(self, callBack=None):
        """starts the file download"""
        self.curretry = 0
        self.cur = 0
        f = open(self.localFileName , "wb")
        if self.auth:
            if self.type == 'http':
                self.__authHttp__()
                urllib2Obj = urllib2.urlopen(self.url, timeout=self.timeout)
                if self.status != CDownload.STOPPED : 
                    self.status = CDownload.DOWNLOADING
                    self.__downloadFile__(urllib2Obj, f, callBack=callBack)
            elif self.type == 'ftp':
                self.url = self.url.replace('ftp://', '')
                authObj = self.__authFtp__()
                self.status = CDownload.DOWNLOADING
                self.__downloadFile__(authObj, f, callBack=callBack)
        else:
            urllib2Obj = urllib2.urlopen(self.url, timeout=self.timeout)
            self.status = CDownload.DOWNLOADING
            self.__downloadFile__(urllib2Obj, f, callBack=callBack)
        return True
            
    def getInfos(self):
        infos = {}
        infos['filesize'] = self.getUrlFileSize()
        infos['downloaded'] = self.cur
        infos['status'] = self.status
        infos['localfilename'] = self.localFileName
        infos['realurl'] = self.url
        infos['size'] = self.fileSize
        return infos
        
    def pause(self):
        self.status = CDownload.PAUSED
    
    def restart(self) :
        if self.status ==  CDownload.PAUSED :
            self.status = CDownload.DOWNLOADING
    
    def stop(self):
        self.status = CDownload.STOPPED
        
    def _check_cache(self):
        size_cache = self.__sizedirectory()
        files = self.__get_files_by_date()
        i = 0
        while size_cache + int(self.getUrlFileSize()) > self.cache_size :
            #have to remove older recording
            try :
                os.remove(files[i])
                print 'Remove %s from cache' %(files[i])
                size_cache = self.__sizedirectory()
                i+=1
            except IndexError, e:
                print 'cache too small for this file'
                return False
            except :
                pass
        return True
            
    def __get_files_by_date(self):
        files = []
        for fname in os.listdir(self.localdir) :
            fname = os.path.join(self.localdir,fname)
            _,ext = os.path.splitext(fname)
            if os.path.isfile(fname) :
                files.append((os.stat(fname)[stat.ST_CTIME], fname))
        files.sort()
        return  [f for s,f in files]
    
    def __sizedirectory(self): 
        size = 0 
        for root, dirs, files in os.walk(self.localdir): 
            for fic in files: 
                size += os.path.getsize(os.path.join(root, fic))
        return size


class FLVdownload(DownloadFile):    
    def seektoresume(self) :
        req = urllib2.Request(self.url + '?start=' + str(self.cur))
        urllib2Obj = urllib2.urlopen(req, timeout=self.timeout)
        #exctract header from flv
        urllib2Obj.read(13)
        return urllib2Obj


class MP4download(DownloadFile):    
    def seektoresume(self) :
        #throw last downloaded MB away, sometimes corrupt
        try :
            print 'before' + str(self.getLocalFileSize())
            with open(self.localFileName, 'ab') as f:
               f.seek(-1048576,os.SEEK_END)
               f.truncate()
               print 'SLEEP 20 sc to not spam and decrease file size too quickly'
               time.sleep(20)
        except :
            pass
        print 'after' + str(self.getLocalFileSize())
        curSize = self.getLocalFileSize()
        self.cur = curSize
        headersize = (5 *1024 * 1024)  #header size + throw last downloaded MB because corrupt when crash on purevid
        margesize = 10 * 1024 * 1024
        #if file too small - restart download (can't resume in header data)
        if curSize < headersize:
            return self.download()
        # import mutagen
        from mutagen.mp4 import MP4
        video = MP4(self.localFileName)
        #Dirty hack to calculate approximatif position in file
        start_time = 0
        end_time = video.info.length
        start_byte = headersize
        end_byte = int(self.getUrlFileSize())
        offset = 0
        DoubleDownload = 0
        center_marge = (margesize - headersize) / 2
        estimated_framerate = (end_byte - start_byte) / (end_time - start_time)
        curTime = float(curSize) / estimated_framerate
        #try to be at approximatif position in htpp file
        while DoubleDownload >= margesize or DoubleDownload <= (headersize)  :
            print 'startb' + str(start_byte)
            print 'startt' + str(start_time)
            print 'endb' + str(end_byte)
            print 'endt' + str(end_time)
            url = self.url + '?start=' + str(curTime+offset)
            print url
            req = urllib2.Request(url)
            urllib2Obj = urllib2.urlopen(req, timeout=self.timeout)
            resume_size = urllib2Obj.headers.get('content-length')
            DoubleDownload = int(int(curSize)  + int(resume_size) - int(self.getUrlFileSize()))
            print 'DoubleDownload' + str(DoubleDownload)
            if DoubleDownload > margesize :
               start_byte = int(self.getUrlFileSize()) - int(resume_size)
               start_time = curTime+offset
               estimated_framerate = (end_byte - start_byte) / (end_time - start_time)
               offset += (DoubleDownload - headersize) / estimated_framerate
            elif DoubleDownload < headersize :                             
               end_byte = int(self.getUrlFileSize()) - int(resume_size)
               end_time = curTime+offset
               estimated_framerate = (end_byte - start_byte) / (end_time - start_time)
               offset += (DoubleDownload - margesize) / estimated_framerate
        #extract mp4 header
        pos = self.extract_mp4_header(urllib2Obj)
        #exctract double download
        print 'double dl = ' + str(pos - (int(self.getUrlFileSize()) -self.cur))
        urllib2Obj.read(pos - (int(self.getUrlFileSize()) -self.cur))
        #self._throwUnecessaryResumeData(urllib2Obj)
        return urllib2Obj
    
    def extract_mp4_header(self,fileobj):
        end = int(fileobj.headers.get('content-length'))
        print end
        offset = 0
        while True:
            length = struct.unpack(">I4s", fileobj.read(8))[0]
            if offset + length  < end :
                fileobj.read(length-8)
                offset +=length
            else :
                break
        return end - (offset + 8)
