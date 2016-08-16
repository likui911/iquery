# -*- coding: utf-8 -*-

import sys
from .utils import args

def cli():
    """Various information query via command line.
    Usage:
        iquery -w <city>
        iquery -m <city>
        iquery [-dgktz] <from> <to> <date>
    Arguments:
        city             城市

        from             出发站
        to               到达站
        date             查询日期
    Options:
        -h, --help       帮助
        -w               天气
        -dgktz           动车,高铁,快速,特快,直达
        -m               电影
    """
    if args.is_querying_train():
        from .train import query
        result = query(args.as_train_query_params())
        result.preety_print()

    elif args.is_querying_weather():
        from .weather import query
        result = query(sys.argv[2])
        result.preety_print()

    elif args.is_querying_movie():
        from .movie import query
        query(sys.argv[2])
  
    elif args.is_asking_help():
        print(cli.__doc__)
