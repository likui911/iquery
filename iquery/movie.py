# -*- coding: utf-8 -*-

import os
import requests
import json
import sys
import prettytable
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from .utils import exit_after_echo
from .utils import requests_get

from bs4 import BeautifulSoup

# 解决递归深度问题
sys.setrecursionlimit(50000)

GEWALA_URL = 'http://www.gewara.com/'
SEARCH_MOVIE_URL = 'http://www.gewara.com/movie/searchMovie.xhtml'
SEARCH_MOVIE_DETAIL = 'http://www.gewara.com/movie/%s'

CITY_NOT_FOUND = 'city not found '
QUERY_FAILED = 'query failed '
END_PAGE_OF_QUERY = 'it\'s already the last page'
BEGIN_PAGE_OF_QUERY = 'it\'s already the first page'
ID_NOT_FOUND = 'the movie id not found'
MOVIE_HEADER = ('序号','片名','评分','类型','语言','导演')


class GewalaCollection():

    def __init__(self,city):
        self.city = city
        self.idx = 0
        self.cookie = self._get_cookie()
        self.urls = self.get_pages()
        
       
    def _get_cookie(self):
        return requests_get(GEWALA_URL+ self.city).cookies

    def next(self):
        if self.idx <len(self.urls)-1:
            self.idx += 1
            return self.query_page(self.urls[self.idx])

    def prev(self):
        if self.idx >0:
            self.idx -= 1
            return self.query_page(self.urls[self.idx])

    def query_page(self,url=None):
     
        if not url:
            url = self.urls[self.idx]
        # todo 查询当前页面内容，并打印
        r = requests.get(url,cookies = self.cookie)
        soup = BeautifulSoup(r.text,'html.parser')
        movie_list = soup.find_all('div',class_='movieList')[0]

        movies = []
        for movie in movie_list.find_all('div',class_ ='ui_text'):
            # 电影id
            movie_id = movie.div.h2.a.get('href').split('/')[-1]
            # 电影片名
            movie_string = movie.div.h2.a.string
            grade =  movie.find_all('span',class_='grade')[0]
            # 电影评分
            movie_grade = grade.sub.string + grade.sup.string
            detail = movie.find_all('p')
            for p in detail:
                if not p.string :
                    pass
                elif  p.string.startswith('类型：'):
                    movie_style = p.string[3:]
                elif p.string.startswith('语言：'):
                    movie_lang = p.string[3:]
                elif p.string.startswith('导演：'):
                    # 控制台输出·与字符不等宽，换成-显示效果好
                    movie_command = p.string[3:].replace('·','-')
            movies.append(
                (movie_id,movie_string,movie_grade,movie_style,movie_lang,movie_command))

        self.print_hotmovies(movies)
        return True

    def print_hotmovies(self,movies):
        pt = PrettyTable(header=False)
        pt.add_row(MOVIE_HEADER)
        for each in movies:
            pt.add_row(each)
  
        try:
            # 递归偶会有MemoryError
            print(pt)
        except MemoryError:
            exit_after_echo(QUERY_FAILED)

    def query_detail(self,id):
        url = SEARCH_MOVIE_DETAIL%id
        r = requests.get(url,cookies = self.cookie)
        try:
            soup = BeautifulSoup(r.text,'html.parser')
        
            txt = soup.find_all('div',onclick="openPoint('ui_movieInfoBox');")[0]
            print(txt.p.contents[0])
            return True
        except:
            return False

    def get_pages(self):
        r= requests_get(SEARCH_MOVIE_URL,cookies = self.cookie)
        soup = BeautifulSoup(r.text,'html.parser')
        page = soup.find_all('div',id='page')[0]

        urls = [SEARCH_MOVIE_URL]

        max_page = 0
        for link in page.find_all('a'):
            url = link.get('href')
            if '=' not in url:
                continue
            page_no = int(url.split('=')[1])
            if page_no > max_page:
                max_page = page_no

        if max_page == 0:
            return urls

        for i in range(1,max_page+1):
            urls.append(SEARCH_MOVIE_URL+"?pageNo=%d"%i)
        return urls
        
def query(city):
    '''
    命令:
        <id>            输入电影编号查看详情
        N/n             下一页
        P/p             上一页
        ！q              退 出
        H/h             帮助 
    '''
       
    file_path = os.path.join(os.path.dirname(__file__),'datas','cities.dat')
    with open(file_path,'r')as fp:
        cities = json.load(fp)

    if city not in cities:
        exit_after_echo(CITY_NOT_FOUND)
  
    gewala = GewalaCollection(cities[city])
    gewala.query_page()
    print(query.__doc__)

    while(True):
        # todo 这里做一些验证
        command = input('>')
        if command == '!q':
            exit_after_echo('---')
        elif command =='n' or command =='N':
            if not gewala.next():
                print(END_PAGE_OF_QUERY)
        elif command == 'p' or command == 'P':
            if not gewala.prev():
                print(BEGIN_PAGE_OF_QUERY)
        elif command =='h' or command == 'H':
            print(query.__doc__)
        else:
            if not gewala.query_detail(command):
                print(ID_NOT_FOUND)
