# -*- coding: utf-8 -*-

import os
import re
import json
import pickle
import prettytable

from datetime import datetime
from .utils import exit_after_echo
from .utils import request_post
from .utils import colored

NO_CITIES = 'city not found'
QUERY_URL = "http://www.zuimeitianqi.com/zuimei/queryWeather"
TABLE_HEADER = ('日期','天气','最低','最高','节气')
WEA_DICT = {'0':'晴','1':'多云','2':'阴','3':'阵雨','4':'雷阵雨','7':'小雨','8':'中雨','9':'大雨','10':'暴雨'}


class WeatherCollection():

    def __init__(self,forecast):
        self._forecast = forecast['data'][0]['forecast']

    def wea_parse(self,wea):
        wea=re.findall('\d',wea)
       
        if len(wea)==1:
            return WEA_DICT[wea[0]]
        else:
            return '%s转%s'%(WEA_DICT[wea[0]],WEA_DICT[wea[1]])
        
    def forecasts(self):
        for fc in self._forecast:
            date = fc.get('date').split(' ')[0]
            _date = datetime.strptime(date,'%Y-%m-%d')
            offset = _date -datetime.today()
 
            if offset.days in range(-1,6):
                forecast = (date,# 日期
                            self.wea_parse(fc.get('wea')),# 天气
                            colored.green(str(fc.get('low'))),# 最低气温
                            colored.red(str(fc.get('high'))),# 最高气温
                            fc.get('ftv'),# 节气
                    )
                yield forecast


    def preety_print(self):
        pt = prettytable.PrettyTable(header=False)
        pt.add_row(TABLE_HEADER) 
        for fc in self.forecasts():
            pt.add_row(fc)
        print(pt)
        


class WeatherForecastQuery():

    def __init__(self, city):
        self._city = city
        self._cites = self.cites()

    def cites(self):
        file_path = os.path.join(
            os.path.dirname(__file__),'datas','citycodes.dat')

        with open(file_path,'r',encoding='utf-8') as f:
            cities = json.load(f)
        return cities

    def query(self):
        if self._city not in self._cites:
            exit_after_echo(NO_CITIES)

        req_data = {}
        req_data['cityCode'] = self._cites[self._city][0]
        r = request_post(QUERY_URL,data=req_data)
        forecast = r.json()

        return WeatherCollection(forecast)
        
   
            

def query(city):
    return WeatherForecastQuery(city).query()
