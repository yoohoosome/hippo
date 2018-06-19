#!/usr/bin/env python3

import json
import argparse
import sys
import re


#Set Color Class  
class colors:  
    BLACK         = '\033[0;30m'  
    DARK_GRAY     = '\033[1;30m'  
    LIGHT_GRAY    = '\033[0;37m'  
    BLUE          = '\033[0;34m'  
    LIGHT_BLUE    = '\033[1;34m'  
    GREEN         = '\033[0;32m'  
    LIGHT_GREEN   = '\033[1;32m'  
    CYAN          = '\033[0;36m'  
    LIGHT_CYAN    = '\033[1;36m'  
    RED           = '\033[0;31m'  
    LIGHT_RED     = '\033[1;31m'  
    PURPLE        = '\033[0;35m'  
    LIGHT_PURPLE  = '\033[1;35m'  
    BROWN         = '\033[0;33m'  
    YELLOW        = '\033[1;33m'  
    WHITE         = '\033[1;37m'  
    DEFAULT_COLOR = '\033[00m'  
    RED_BOLD      = '\033[01;31m'  
    ENDC          = '\033[0m'  

'''
uid 可能是字符串

06-04 11:45:41.965 10067 30167 16250 W PackageParser: Ignoring duplicate uses-permissions/uses-permissions-sdk-m: android.permission.WRITE_SYNC_SETTINGS in package: com.jd.jrapp at: Binary XML file line #73
06-05 10:56:18.280  root   902  1080 I ThermalEngine: handle_thresh_sig: HIS Id HISTORY-CPU4 Sensor tsens_tz_sensor7 Temp 58000

解析后

{'uid': '10067', 
'pid': '30167'. 
'tid': '16250', 
'time': '06-04 11:45:41.965', 
'priority': 'W', 
'tag': 'PackageParser', 
'message': 'Ignoring duplicate uses-permissions/uses-permissions-sdk-m: android.permission.WRITE_SYNC_SETTINGS in package: com.jd.jrapp at: Binary XML file line #73', 
'message2': None}
'''

RE_LOGCAT = re.compile(r'(?P<time>\d\d-\d\d \d\d:\d\d:\d\d.\d\d\d)'
                           r' *(?P<uid>\w+) *(?P<pid>\d+) *(?P<tid>\d+) *(?P<priority>.)'
                           r' (((?P<tag>.*?) *:($| (?P<message>.*)))|(?P<message2>.*))')

PRIORITY_MAPPER = {
        'V': 'verbose',
        'D': 'debug',
        'I': 'info',
        'W': 'warn',
        'E': 'error',
    }

def priority_char_to_string(char: str):
    if char in PRIORITY_MAPPER:
        return PRIORITY_MAPPER[char]
    else:
        return char

def print_green(string):
    print(colors.YELLOW + string + colors.ENDC)

def print_yellow(string):
    print(colors.BLUE + string + colors.ENDC)

def get_ps():
    pass

def get_system_log(file):
    with open(file) as f:
        lines = f.readlines()
    
    for i in range(len(lines)):
        if 'SYSTEM LOG (logcat -v threadtime -v printable -v uid -d *:v)' in lines[i]:
            index_start = i + 2
        if "was the duration of 'SYSTEM LOG'" in lines[i]:
            index_end = i

    logs = lines[index_start:index_end]

    log_d_list = []
    for log in logs:
        result = RE_LOGCAT.search(log)
        if not result:
            print('无法解析')
            print(log)
            continue
        log_d = result.groupdict()
        log_d_list.append(log_d)
    return log_d_list


def get_events_log(file):
    with open(file) as f:
        lines = f.readlines()
    
    for i in range(len(lines)):
        if 'EVENT LOG (logcat -b events' in lines[i]:
            index_start = i + 2
        if "was the duration of 'EVENT LOG'" in lines[i]:
            index_end = i

    logs = lines[index_start:index_end]

    log_d_list = []
    for log in logs:
        result = RE_LOGCAT.search(log)
        if not result:
            print('无法解析')
            print(log)
            continue
        log_d = result.groupdict()
        log_d_list.append(log_d)
    return log_d_list

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='指定文件作为数据源')
    parser.add_argument('-p', '--pid', type=int, help='进程 pid')
    parser.add_argument('-e', '--events', action="store_true", help='解析 events log')
    return parser.parse_args()

def print_log_d(log_d):
    print('%s %s %s\t%s %s: %s %s' % (log_d['time'], log_d['pid'], log_d['tid'], log_d['priority'], log_d['tag'], log_d['message'], log_d['message2']))

def print_log_d_list(log_d_list):
    for log_d in log_d_list:
        print_log_d(log_d)

def filter_log_d_with_pid(log_d_list, pid: int):
    filter_list = []
    for log_d in log_d_list:
        if int(log_d['pid']) == pid:
            filter_list.append(log_d)
    return filter_list


def main():
    args = parse_arguments()

    if args.events:
        log_d_list = get_events_log(args.file)
    else:
        log_d_list = get_system_log(args.file)

    if args.pid:
        log_d_list = filter_log_d_with_pid(log_d_list, args.pid)

    print_log_d_list(log_d_list)

        
main()