import thread
import socket
import os
import time
import sys

from cache import *
from urlparse import urlparse


config = {
    "HOST_NAME": "0.0.0.0",
    "BIND_PORT": 12345,
    "MAX_REQUEST_LEN": 1024,
    "CRLF": "\r\n\r\n"
}


# create server and listen on port 12345
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
c.bind((config['HOST_NAME'], config['BIND_PORT']))
c.listen(10)

# initiating cache engine
cached = CACHE()


def serve_client(s, a):
    request = s.recv(1024)
    # print request
    first_line = request.split('\n')[0]
    parsed_line = first_line.split(' ')
    method = parsed_line[0]                     # get method
    url = parsed_line[1]                        # get url
    protocol = parsed_line[2]
    http_pos = url.find("://")                  # find pos of ://
    ip_end = url.find("/", http_pos + 4)
    file_name = url[ip_end + 1:]
    # print file_name
    if (http_pos == -1):
        temp = url
    else:
        temp = url[(http_pos + 3):]             # get the rest of url

    port_pos = temp.find(":")                   # find the port pos (if any)

    # find end of web server
    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ""
    port = -1
    if (port_pos == -1 or webserver_pos < port_pos):      # default port
        port = 80
        webserver = temp[:webserver_pos]
    else:                                                 # specific port
        port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
        webserver = temp[:port_pos]

    # check if cached
    cache = cached.cache_check(webserver, port, file_name)[0]
    if(file_name == "2.binary"):
        cache = False

    final_request_notcahced = method + " /" + file_name + config['CRLF']
    if(cache):
        final_request_cached = method + " /" + file_name + \
            "\r\nIf-Modified-Since:" + cache.time + config['CRLF']
    try:
        temp = ""
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((webserver, port))

        if not(cache):  # if not cached
            print "not cached"
            # not cached, so normal request
            conn.send(final_request_notcahced)

        else:
            conn.send(final_request_cached)
            data = conn.recv(config['MAX_REQUEST_LEN'])
            # print "No" + data
            if(len(data) > 0):  # and modified since
                print "modified since cached"  # if modified send data received now
                s.send(data)
                temp += data
            else:
                print "sending from cache"
                s.send(cache.data)  # send from cache
                s.close()
                conn.shutdown(1)
                conn.close()
                return

        while True:
            data = conn.recv(config['MAX_REQUEST_LEN'])
            # print "Hey" + data
            if (len(data) == 0):
                cached.cache_file(webserver, port, file_name,
                                  temp)  # cache data
                conn.shutdown(1)
                conn.close()
                break
            else:
                s.send(data)  # send remaining data
                temp += data
    except socket.error:
        print "Socket Connection Error"
        s.send(ERROR_PAGE)

    s.close()

#Runs forever and each connection taken on a new thread
while True:

    try:
        s, a = c.accept()
        try:
            thread.start_new_thread(serve_client, (s, a))
        except:
            print "Threading Error"
        print ""

    except:
        print "Error : Socket connection couldnt be excepted, exiting"
        sys.exit(0)

c.close()
