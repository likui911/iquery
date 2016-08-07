# -*- coding: utf-8 -*-

import os
import re
import prettytable
from datetime import datetime
from collections import OrderedDict
from .utils import requests_get, exit_after_echo,colored

QUERY_URL = 'https://kyfw.12306.cn/otn/lcxxcx/query'
FROM_STATION_NOT_FOUND = 'from station not found'
TO_STATION_NOT_FOUND = 'to station not found'
NO_RESPONSE = 'no response'
INVALID_DATE = 'invalid date'
TABLE_HEADER = ('车次','车站','时间','历时','商务','一等','二等','软卧','硬卧','软座','硬座','无座')


class TrainsCollection():
    def __init__(self, rows, opt):
        self._rows = rows
        self._opt = opt

    def _during_time(self,lishi):
        hours,minutes = lishi.split(':')
        if hours == '00':
            return '%s分钟'%minutes
        return '%s小时%s分钟'%(hours,minutes)


    def trains(self):
        for row in self._rows:
            train_code = row.get('station_train_code')[0].lower()
            if not self._opt or train_code in self._opt:    
                train = (row.get('station_train_code'),
                colored.green(row.get('from_station_name'))+'\n'+colored.red(row.get('to_station_name')),
                colored.green(row.get('start_time'))+'\n'+colored.red(row.get('arrive_time')),
                self._during_time(row.get('lishi')),
                row.get('swz_num'),# 商务座
                row.get('zy_num'), # 一等座
                row.get('ze_num'), # 二等座
                row.get('rw_num'), # 软 卧
                row.get('yw_num'), # 硬 卧
                row.get('rz_num'), # 软 座
                row.get('yz_num'), # 硬 座
                row.get('wz_num')) # 无 座
                yield train

    def preety_print(self):
        table = prettytable.PrettyTable(header=False)
        table.add_row(TABLE_HEADER)
        for train in self.trains():
            table.add_row(train)
        print(table)


class TrainTicketsQuery():
    def __init__(self, from_station, to_station, date, opts=None):

        self.from_station = from_station
        self.to_station = to_station
        self.date = date
        self.opts = opts

    def stations(self):
        filepath = os.path.join(
            os.path.dirname(__file__),
            'datas', 'stations.dat'
        )
        d = {}
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                name, telecode = line.split()
                d.setdefault(name, telecode)
        return d

    def _from_station_telecode(self):
        code = self.stations().get(self.from_station)
        if not code:
            exit_after_echo(FROM_STATION_NOT_FOUND)
        return code

    def _to_station_telecode(self):
        code = self.stations().get(self.to_station)
        if not code:
            exit_after_echo(TO_STATION_NOT_FOUND)
        return code

    def _parser_date(self):
        result = ''.join(re.findall('\d',self.date))
        l = len(result)
        
        # 处理类似6.1 、6.21 、0621之类的输入
        if l in (2,3,4):
            year = str(datetime.today().year)
            return year + result

        # 处理类似2016.6.1 、2016.6.21、2016.06.21之类的输入
        if l in (6,7,8):
            return result
        return ''

    def _valid_date(self):
        date = self._parser_date()
        if not date:
            exit_after_echo(INVALID_DATE)

        try:
            date = datetime.strptime(date,'%Y%m%d')
        except ValueError:
            exit_after_echo(INVALID_DATE)
        
        # 火车票预售期为50天
        offset = date - datetime.today()
       
        if offset.days not in range(-1,50):
            exit_after_echo(INVALID_DATE)

        return datetime.strftime(date, '%Y-%m-%d')

    def _build_params(self):
        d = OrderedDict()
        d['purpose_codes'] = 'ADULT'
        d['queryDate'] = self._valid_date()
        d['from_station'] = self._from_station_telecode()
        d['to_station'] = self._to_station_telecode()
        return d

    def query(self):
        params = self._build_params()

        r = requests_get(QUERY_URL, params=params, verify=False)
        try:
            rows = r.json()['data']['datas']
        except KeyError:
            rows = []
        except TypeError:
            exit_after_echo(NO_RESPONSE)

        return TrainsCollection(rows, self.opts)


def query(params):
    """`params` is a list, contains `from`, `to`, `date`."""
    return TrainTicketsQuery(*params).query()
