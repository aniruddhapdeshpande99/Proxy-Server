#Caching of the proxy server

from time import localtime
from datetime import datetime
from time import strftime
import sys

limit = 2
#Cache Limit
min_int = sys.maxint
min_int = -min_int - 1
#Calculating Smallest integer (-INT_MAX)

#Class for Cached Data
class CACHED_DATA:

    #Cache initialisation
    #Params :
    #time : Time when cache data added
    #server : Server url
    #port : Server port
    #data : Data to be cached
    #filename : Name of the file to be cached
    def __init__(self, server, port, filename, data):
        self.time = strftime('%a %b %d %H:%M:%S %Z %Y', localtime())
        self.server = server
        self.port = port
        self.data = data
        self.filename = filename

    def file_check(self, server, port, filename):
        # Returns true if file with filename exists on server or not
        if(self.server == server and self.port == port and self.filename == filename):
            return True
        return False

#Class for Cache operation
class CACHE:
    cache_num = 0 #Position in cache
    cached_data =[CACHED_DATA(" ", 12345, "filename", "data")]*3 #Cached Data

    def cache_check(self, server, port, file_requested):
    #Check if data present within cache
        for data in self.cached_data:
        #Entire Cache is checked
            if(data.file_check(server, port, file_requested)):
                #Return File if in cache
                return [data, self.cached_data.index(data)]
        return [0, min_int]
        #Return 0 ie. false and smallest integer as its index

    def cache_file(self, server, port, filename, data):
        exists = self.cache_check(server, port, filename)

        if( exists[0] == 0 and self.cache_num <= limit):
            temp_data = CACHED_DATA(server, port, filename, data)
            print self.cache_num
            self.cached_data[self.cache_num] = temp_data
            self.cache_num = self.cache_num + 1

        elif (exists[0] == 0 and self.cache_num > limit):
            print self.cache_num
            self.cache_num = 0
            temp_data = CACHED_DATA(server, port, filename, data)
            self.cached_data[self.cache_num] = temp_data
            self.cache_num = self.cache_num + 1
