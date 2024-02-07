import os
import datetime
from . import Config


if not os.path.isdir(Config.LOG_DIR): os.mkdir(Config.LOG_DIR)

today_str = str(datetime.date.today())
log_filepath = os.path.join(Config.LOG_DIR, f'log_{today_str}.txt')
order_history_filepath = os.path.join(Config.LOG_DIR, f'order_history_{today_str}.txt')


def write_log(*args, **kwargs):
    with open(log_filepath, mode='a', encoding='utf8') as f:
        f.write(str(datetime.datetime.today()) + '\n')
        if args:
            f.write('\t'.join([str(arg) for arg in args]) + '\n')
        if kwargs:
            f.write('\n'.join([f"{str(k)}: {str(v)}" for k, v in kwargs.items()]))
        f.write('\n\n')


def write_order_history(*args, **kwargs):
    with open(order_history_filepath, mode='a', encoding='utf8') as f:
        f.write(str(datetime.datetime.today()) + '\t')
        if args:
            f.write('\t'.join([str(arg) for arg in args]) + '\n')
        if kwargs:
            f.write('\n'.join([f"{str(k)}: {str(v)}" for k, v in kwargs.items()]))
        f.write('\n\n')
