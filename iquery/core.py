# -*- coding: utf-8 -*-

import sys
from .utils import args

def cli():
    """Various information query via command line.
    Usage:
        iquery [-dgktz] <from> <to> <date>
    Arguments:
        from             出发站
        to               到达站
        date             查询日期
    Options:
        -dgktz           动车,高铁,快速,特快,直达

    Usage：
        iquery [-w] <city>
    Arguments:
        city             城 市
    Options:
        -w              天气

    """
    if args.is_querying_train():
        from .train import query
        result = query(args.as_train_query_params())
        result.preety_print()

    elif args.is_querying_weather():
        from .weather import query
        result = query(sys.argv[2])
        result.preety_print()

    else:
        print(cli.__doc__)
