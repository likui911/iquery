# -*- coding: utf-8 -*-

import sys
import requests
import random

from requests.exceptions import ConnectionError

# SSL网站禁止警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecurePlatformWarning
from requests.packages.urllib3.exceptions import SNIMissingWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
requests.packages.urllib3.disable_warnings(SNIMissingWarning)

NETWORK_CONNECTION_FAILED = 'Network connection failed.'

USER_AGENTS = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
    ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) '
        'Chrome/19.0.1084.46 Safari/536.5'),
    ('Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46'
        'Safari/536.5')
)

def exit_after_echo(promt):
    print(promt)
    sys.exit(1)


def requests_get(url, **kwargs):

    try:
        r = requests.get(
            url,
            headers={'User-Agent': random.choice(USER_AGENTS)}, **kwargs
        )
    except ConnectionError as e:
        exit_after_echo(NETWORK_CONNECTION_FAILED)
   
    return r

def request_post(url,data,**kwargs):

    try:
        r = requests.post(
            url,
            headers={'User-Agent': random.choice(USER_AGENTS)}, data=data,**kwargs
            )
    except ConnectionError:
        exit_after_echo(NETWORK_CONNECTION_FAILED)

    return r


class Colored():

    '''控制台输出颜色
    '''

    RED = '\033[0;31;40m'
    GREEN = '\033[0;32;40m'
    RESET = '\033[0m'

    def color_str(self,color,s):
        return '%s%s%s'%(getattr(self,color),s,self.RESET)

    def red(self,s):
        return self.color_str('RED',s)

    def green(self,s):
        return self.color_str('GREEN',s)



class Args():
    def __init__(self, args=None):
        self._args = sys.argv[1:]
        self._argc = len(self)

    def __len__(self):
        return len(self._args)

    def all(self):
        return self._args

    def get(self, idx):
        try:
            return self.all()[idx]
        except IndexError:
            return None

    def options(self):
        """返回列车查询选项"""
        arg = self.get(0)
        if arg.startswith('-'):
            return arg[1:]
        return ''

    def is_asking_help(self):
        if self.get(0)=='-h'or self.get(0)=='-help':
            return True
        return False

    def is_querying_weather(self):
        '''args长度为2并且以-w开始为天气查询的请求'''
        if self._argc != 2:
            return False
        if self.get(0)!='-w':
            return False
        return True

    def is_querying_movie(self):
        if self.get(0)!='-m':
            return False
        if self._argc !=2:
            return False
        return True

    def is_querying_train(self):
        '''根据args的长度和关键字判断是否是列车查询'''
        if self._argc not in (3, 4):
            return False
        if self._argc == 4:
            arg = self.get(0)
            if not arg.startswith('-'):
                return False
            if arg[1] not in 'dgktz':
                return False
        return True

    def as_train_query_params(self):
        opts = self.options()
        if opts:
            return self._args[1:] + [opts]
        return self._args

args = Args()
colored = Colored()
