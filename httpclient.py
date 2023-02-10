#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Fahad Naveed,Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
'''Here are the external sources that helped me during this assignment
    https://www.internalpointers.com/post/making-http-requests-sockets-python
    https://stackoverflow.com/questions/409783/socket-shutdown-vs-socket-close
    https://docs.python.org/2/library/socket.html#socket.socket.setblocking
    https://stackoverflow.com/questions/45695168/send-raw-post-request-using-socket'''
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse,urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        
        return int(data[9:12])

    def get_headers(self,data):
        return data[0]

    def get_body(self, data):
        return data[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        try:
            while not done:
                part = sock.recv(1024)
                #\sock.setblocking(0)
                
                if (part):
                    buffer.extend(part)
                else:
                    done = not part
            return buffer.decode('utf-8')
        except BlockingIOError:
            done = True
            buffer.extend(part)
            return buffer.decode('utf-8')
    def GET(self, url, args=None):
        #code = 500
        #body = ""
        
        if '/' not in url[7:]:
            url+='/'
        length = 50
        #ensuring args is in a format readable by the post request
        if args is not None:
            args = urlencode(args)
            length = len(args)
            
        
        parsed = urlparse(url)
        #if statement to differentiate bw local host and sites on the web
        if ":" in parsed[1]:
            #Separating the host and the port to connect to
            conn = parsed[1].split(":")
            host = conn[0]
            port = int(conn[1])
            self.connect(host, port)
            #Creating the get request
            sender  = "GET %s HTTP/1.1\r\nHost:%s\r\nConnection: close\r\n\r\n%s" % (parsed[2],host,args)
    
        else:
            #seaparating the host from the path to pass in the get request
            host = parsed[1]
            path = parsed[2]
            sender  = "GET %s HTTP/1.1\r\nHost:%s\r\nConnection: close\r\n\r\n%s" % (path,host,args)
            self.connect(host, 80)
        self.sendall(sender)

        stringa = self.recvall(self.socket)

        self.close()
        response =stringa.split('\r\n\r\n')
        #print(response)
        #extracting the headers and body from the response
        code = self.get_code(stringa)

        headers = self.get_headers(response)
        body = self.get_body(response)

        print(headers+'\n')
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        
        code = 500
        body = ""
        if '/' not in url[7:]:
            url+='/'
        length = 50
        #ensuring args is in a format readable by the post request
        if args is not None:
            args = urlencode(args)
            length = len(args)
            
    
        parsed = urlparse(url)
        
        #if statement to differentiate bw local host and sites on the web
        if ":" in parsed[1]:
            #Separating the host and the port to connect to
            conn = parsed[1].split(":")
            host = conn[0]
            port = int(conn[1])
            self.connect(host, port)
            #Creating the POST request
            sender  = "POST %s HTTP/1.1\r\nHost:%s\r\nAccept: application/json\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %d\r\n\r\n%s" % (parsed[2],host,length,args)
    
        else:
            #seaparating the host from the path to pass in the POST request
            host = parsed[1]
            path = parsed[2]
            sender  = "POST %s HTTP/1.1\r\nHost:%s\r\nAccept: application/json\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %d\r\n\r\n%s" % (path,host,length,args)
            self.connect(host, 80)
        self.sendall(sender)
        self.socket.shutdown(socket.SHUT_WR)
        stringa = self.recvall(self.socket)

        self.close()
        
        response =stringa.split('\r\n\r\n')
        
        #extracting the headers and body from the response
        code = self.get_code(stringa)
        headers = self.get_headers(response)
        body = self.get_body(response)
        print(headers+'\n')
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
