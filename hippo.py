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

def print_log_d(log_d):
    if log_d['message2']:
        print('%s %s %s\t%s %s: %s %s' % (log_d['time'], log_d['pid'], log_d['tid'], log_d['priority'], log_d['tag'], log_d['message'], log_d['message2']))
    else:
        print('%s %s %s\t%s %s: %s' % (log_d['time'], log_d['pid'], log_d['tid'], log_d['priority'], log_d['tag'], log_d['message']))

def print_log_d_list(log_d_list):
    for log_d in log_d_list:
        print_log_d(log_d)

def print_lines(lines):
    for line in lines:
        print(line.rstrip())

# --------

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
            print(log)
            continue
        log_d = result.groupdict()
        log_d_list.append(log_d)
    return log_d_list

def get_proc_meminfo(file):
    with open(file) as f:
        lines = f.readlines()
    
    for i in range(len(lines)):
        if 'MEMORY INFO (/proc/meminfo)' in lines[i]:
            index_start = i
        if "was the duration of 'MEMORY INFO'" in lines[i]:
            index_end = i

    out_list = lines[index_start:index_end]
    return out_list

def get_proc_pagetypeinfo(file):
    with open(file) as f:
        lines = f.readlines()
    
    for i in range(len(lines)):
        if 'PAGETYPEINFO (/proc/pagetypeinfo)' in lines[i]:
            index_start = i
        if "was the duration of 'PAGETYPEINFO'" in lines[i]:
            index_end = i

    out_list = lines[index_start:index_end]
    return out_list

def get_total_pss(file):
    with open(file) as f:
        lines = f.readlines()
    
    for i in range(len(lines)):
        if 'Total PSS by process' in lines[i]:
            index_start = i
        if "was the duration of 'DUMPSYS MEMINFO'" in lines[i]:
            index_end = i

    out_list = lines[index_start:index_end]
    return out_list

def get_cpu_info(file):
    with open(file) as f:
        lines = f.readlines()
    
    for i in range(len(lines)):
        if 'DUMPSYS CPUINFO (/system/bin/dumpsys -t 10 cpuinfo -a)' in lines[i]:
            first_index = i
        if "was the duration of 'DUMPSYS CPUINFO'" in lines[i]:
            last_index = i

    out_list = lines[first_index:last_index]
    return out_list

def get_dmesg(file):
    with open(file) as f:
        lines = f.readlines()
    
    for i in range(len(lines)):
        if '------ KERNEL LOG (dmesg) ------' in lines[i]:
            first_index = i
        if "was the duration of 'KERNEL LOG (dmesg)'" in lines[i]:
            last_index = i

    out_list = lines[first_index:last_index]
    return out_list

def get_uptime(file):
    with open(file) as f:
        lines = f.readlines()
    
    uptime_list =[]
    for i in range(len(lines)):
        if '------ UPTIME (uptime) ------' in lines[i]:
            uptime_list.append(lines[i + 1])

    #  10:56:03 up 18:41,  0 users,  load average: 5.51, 9.09, 9.09
    return uptime_list[0]

def get_ps(file):
    with open(file) as f:
        lines = f.readlines()
    
    for i in range(len(lines)):
        if '------ PROCESSES AND THREADS (ps -A -T -Z -O pri,nice,rtprio,sched,pcy) ------' in lines[i]:
            index_start = i
        if "was the duration of 'PROCESSES AND THREADS'" in lines[i]:
            index_end = i

    out_list = lines[index_start:index_end]
    return out_list

def get_top(file):
    with open(file) as f:
        lines = f.readlines()
    
    for i in range(len(lines)):
        if '------ CPU INFO (top -b -n 1 -H -s 6 -o pid,tid,user,pr,ni,%cpu,s,virt,res,pcy,cmd,name) ------' in lines[i]:
            index_start = i
        if "was the duration of 'CPU INFO'" in lines[i]:
            index_end = i

    out_list = lines[index_start:index_end]
    return out_list

def filter_log_d_with_pid(log_d_list, pid: int):
    filter_list = []
    for log_d in log_d_list:
        if int(log_d['pid']) == pid:
            filter_list.append(log_d)
    return filter_list

def filter_log_d_with_tid(log_d_list, pid: int):
    filter_list = []
    for log_d in log_d_list:
        if int(log_d['tid']) == pid:
            filter_list.append(log_d)
    return filter_list

def show_categories():
    print('您可以使用下面的内容分类:')
    print('         log - system log')
    print('      events - events log')
    print('      kernel - dmesg')
    print('      uptime - uptime')
    print('         cpu - dumpsys cpuinfo')
    print('         top - top')
    print('          ps - ps')
    print('         pss - total pss')
    print('     meminfo - cat /proc/meminfo')
    print('pagetypeinfo - cat /proc/pagetypeinfo')

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('categories', nargs='*', help='需要显示的内容分类')
    parser.add_argument('-f', '--file', help='指定文件作为数据源', dest='file')
    parser.add_argument('-p', '--pid', type=int, help='指定进程 pid')
    parser.add_argument('-t', '--tid', type=int, help='指定线程 tid')
    parser.add_argument('-l', '--list-categories', action='store_true', help='显示可用的内容分类', dest='list')
    return parser.parse_args()

def main():
    args = parse_arguments()

    if args.list:
        show_categories()
        return
    
    if not args.file:
        print('请使用 -f 指定 bugreport, 或使用 -h 查看使用说明')
        return

    if not args.categories or 'log' in args.categories:
        log_d_list = get_system_log(args.file)
        if args.pid:
            log_d_list = filter_log_d_with_pid(log_d_list, args.pid)
        if args.tid:
            log_d_list = filter_log_d_with_tid(log_d_list, args.tid)
        print_log_d_list(log_d_list)

    if 'events' in args.categories:
        log_d_list = get_events_log(args.file)
        if args.pid:
            log_d_list = filter_log_d_with_pid(log_d_list, args.pid)
        if args.tid:
            log_d_list = filter_log_d_with_tid(log_d_list, args.tid)
        print_log_d_list(log_d_list)
    
    if 'pss' in args.categories:
        print_lines(get_total_pss(args.file))
    
    if 'meminfo' in args.categories:
        print_lines(get_proc_meminfo(args.file))

    if 'pagetypeinfo' in args.categories:
        print_lines(get_proc_pagetypeinfo(args.file))
    
    if 'cpu' in args.categories:
        print_lines(get_cpu_info(args.file))

    if 'kernel' in args.categories:
        print_lines(get_dmesg(args.file))

    if 'uptime' in args.categories:
        print_lines([get_uptime(args.file)])

    if 'ps' in args.categories:
        print_lines(get_ps(args.file))

    if 'top' in args.categories:
        print_lines(get_top(args.file))

if __name__ == '__main__':
    main()