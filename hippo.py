#!/usr/bin/env python3

import argparse
import re
import zipfile
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

VERSION = '0.4.1'

# Set Color Class
class colors:
    BLACK = '\033[0;30m'
    DARK_GRAY = '\033[1;30m'
    LIGHT_GRAY = '\033[0;37m'
    BLUE = '\033[0;34m'
    LIGHT_BLUE = '\033[1;34m'
    GREEN = '\033[0;32m'
    LIGHT_GREEN = '\033[1;32m'
    CYAN = '\033[0;36m'
    LIGHT_CYAN = '\033[1;36m'
    RED = '\033[0;31m'
    LIGHT_RED = '\033[1;31m'
    PURPLE = '\033[0;35m'
    LIGHT_PURPLE = '\033[1;35m'
    BROWN = '\033[0;33m'
    YELLOW = '\033[1;33m'
    WHITE = '\033[1;37m'
    DEFAULT_COLOR = '\033[00m'
    RED_BOLD = '\033[01;31m'
    ENDC = '\033[0m'


def print_green(string):
    print(colors.YELLOW + string + colors.ENDC)


def print_yellow(string):
    print(colors.BLUE + string + colors.ENDC)


'''
uid 可能是字符串

06-04 11:45:41.965 10067 30167 16250 W PackageParser: Ignoring duplicate uses-permissions/uses-permissions-sdk-m: android.permission.WRITE_SYNC_SETTINGS in package: com.jd.jrapp at: Binary XML file line #73
06-05 10:56:18.280  root   902  1080 I ThermalEngine: handle_thresh_sig: HIS Id HISTORY-CPU4 Sensor tsens_tz_sensor7 Temp 58000

解析后

{'uid': '10067', 
'pid': '30167'. 
'tid': '16250', 
'month': '06',
'day': '04',
'hour': '11',
'minute': '45',
'second': '41',
'millisecond': '965',
'priority': 'W', 
'tag': 'PackageParser', 
'message': 'Ignoring duplicate uses-permissions/uses-permissions-sdk-m: android.permission.WRITE_SYNC_SETTINGS in package: com.jd.jrapp at: Binary XML file line #73', 
'message2': None}
'''

RE_LOGCAT = re.compile(
    r'(?P<month>\d\d)-(?P<day>\d\d) (?P<hour>\d\d):(?P<minute>\d\d):'
    r'(?P<second>\d\d).(?P<millisecond>\d\d\d)'
    r' *(?P<uid>\w+) *(?P<pid>\d+) *(?P<tid>\d+) *(?P<priority>.)'
    r' (((?P<tag>.*?) *:($| (?P<message>.*)))|(?P<message2>.*))')


def print_logs(logs):
    for log in logs:
        print(log)


def print_lines(lines):
    for line in lines:
        print(line.rstrip())


# --------

class LogEntry:
    def __init__(self, log_d):
        self.time = datetime(
            year=datetime.now().year,
            month=int(log_d['month']),
            day=int(log_d['day']),
            hour=int(log_d['hour']),
            minute=int(log_d['minute']),
            second=int(log_d['second']),
            microsecond=int(log_d['millisecond']) * 1000)
        self.pid = int(log_d['pid'])
        self.tid = int(log_d['tid'])
        self.priority = log_d['priority']
        self.level = priority2level(log_d['priority'])
        self.tag = log_d['tag']
        self.message = log_d['message']
        if log_d['message2']:
            self.message = self.message + ' ' + log_d['message2']

    def __str__(self):
        pid_str = str(self.pid)
        if self.pid < 10000:
            pid_str = ' ' + pid_str
        tid_str = str(self.tid)
        if self.tid < 10000:
            tid_str = ' ' + tid_str
        time_str = self.time.strftime('%m-%d %H:%M:%S.%f')[:-3]

        return '%s %s %s %s %s: %s' % (time_str, pid_str, tid_str,
                                       self.priority, self.tag, self.message)


def priority2level(level_str):
    levels = {'V': 1,
              'D': 2,
              'I': 3,
              'W': 4,
              'E': 5,
              'F': 6}
    if level_str not in levels:
        print(level_str)
        raise Exception('log level 填写错误, 必须是 VDIWEF')
    return levels[level_str]


def read_lines(file_name):
    if zipfile.is_zipfile(file_name):
        with zipfile.ZipFile(file_name) as z:
            file_names = z.namelist()
            for file_name in file_names:
                if file_name.startswith('bugreport_') \
                        and file_name.endswith('.log'):
                    bugreport_file = file_name
            if not bugreport_file:
                print('没有找到 bugreport 文件')
            with z.open(bugreport_file) as f:
                return [line.decode('utf-8') for line in f.readlines()]
    else:
        with open(file_name) as f:
            return f.readlines()


def get_logs(minute=None):
    for i in range(len(bugreport_lines)):
        if 'SYSTEM LOG (logcat' in bugreport_lines[i]:
            syslog_index_start = i + 2
        if "was the duration of 'SYSTEM LOG'" in bugreport_lines[i]:
            syslog_index_end = i
        if 'EVENT LOG (logcat -b events' in bugreport_lines[i]:
            elog_index_start = i + 2
        if "was the duration of 'EVENT LOG'" in bugreport_lines[i]:
            elog_index_end = i

    if not syslog_index_start or not syslog_index_end:
        raise Exception('Syetem Log Lost')

    if not elog_index_start or not elog_index_end:
        raise Exception('Events Log Lost')

    system_logs = []
    events_logs = []

    for line in bugreport_lines[syslog_index_start:syslog_index_end]:
        result = RE_LOGCAT.search(line)
        if not result:
            # print(log)
            continue
        log_d = result.groupdict()
        system_logs.append(LogEntry(log_d))

    for line in bugreport_lines[elog_index_start:elog_index_end]:
        result = RE_LOGCAT.search(line)
        if not result:
            # print(log)
            continue
        log_d = result.groupdict()
        events_logs.append(LogEntry(log_d))

    if minute:
        report_time = get_report_time(events_logs)
        start_time = report_time - timedelta(minutes=minute)
        system_logs = \
            [log for log in system_logs if start_time < log.time < report_time]
        events_logs = \
            [log for log in events_logs if start_time < log.time < report_time]

    return system_logs, events_logs


def filter_log(logs,
               pid=None,
               tid=None,
               tag=None,
               grep=None,
               priority=None,
               process=None) -> list:
    filtered_log = []
    if process:
        pid = get_pid(process)
    for entry in logs:
        if pid and entry.pid != int(pid):
            continue
        if tid and entry.tid != int(tid):
            continue
        if tag and tag not in entry.tag:
            continue
        if grep and grep not in entry.message:
            continue
        if priority and entry.level < priority2level(priority):
            continue

        filtered_log.append(entry)
    return filtered_log


def get_proc_meminfo():
    for i in range(len(bugreport_lines)):
        if 'MEMORY INFO (/proc/meminfo)' in bugreport_lines[i]:
            index_start = i
        if "was the duration of 'MEMORY INFO'" in bugreport_lines[i]:
            index_end = i

    out_list = bugreport_lines[index_start:index_end]
    return out_list


def get_proc_pagetypeinfo():
    for i in range(len(bugreport_lines)):
        if 'PAGETYPEINFO (/proc/pagetypeinfo)' in bugreport_lines[i]:
            index_start = i
        if "was the duration of 'PAGETYPEINFO'" in bugreport_lines[i]:
            index_end = i

    out_list = bugreport_lines[index_start:index_end]
    return out_list


def get_total_pss():
    for i in range(len(bugreport_lines)):
        if 'Total PSS by process' in bugreport_lines[i]:
            index_start = i
        if "was the duration of 'DUMPSYS MEMINFO'" in bugreport_lines[i]:
            index_end = i

    out_list = bugreport_lines[index_start:index_end]
    return out_list


def get_cpu_info():
    for i in range(len(bugreport_lines)):
        if 'DUMPSYS CPUINFO (/system/bin/dumpsys -t 10 cpuinfo -a)' \
                in bugreport_lines[i]:
            first_index = i
        if "was the duration of 'DUMPSYS CPUINFO'" in bugreport_lines[i]:
            last_index = i

    out_list = bugreport_lines[first_index:last_index]
    return out_list


def get_dmesg():
    for i in range(len(bugreport_lines)):
        if '------ KERNEL LOG (dmesg) ------' in bugreport_lines[i]:
            first_index = i
        if "was the duration of 'KERNEL LOG (dmesg)'" in bugreport_lines[i]:
            last_index = i

    out_list = bugreport_lines[first_index:last_index]
    return out_list


def get_uptime():
    uptime_list = []
    for i in range(len(bugreport_lines)):
        if '------ UPTIME (uptime) ------' in bugreport_lines[i]:
            uptime_list.append(bugreport_lines[i + 1])

    if not uptime_list:
        return 'Failed to get uptime'

    #  10:56:03 up 18:41,  0 users,  load average: 5.51, 9.09, 9.09
    return uptime_list[0]


def get_report_time(elogs):
    for log in elogs:
        if log.tag == 'am_proc_start' and 'com.miui.bugreport' in log.message:
            report_time = log.time
    return report_time


def get_ps(lines):
    for i in range(len(lines)):
        if '------ PROCESSES AND THREADS (ps' in lines[i]:
            index_start = i
        if "was the duration of 'PROCESSES AND THREADS'" in lines[i]:
            index_end = i

    out_list = lines[index_start:index_end]
    return out_list


def get_top(lines):
    for index in range(len(lines)):
        if '------ CPU INFO (top' in lines[index]:
            index_start = index
        if "was the duration of 'CPU INFO'" in lines[index]:
            index_end = index

    out_list = lines[index_start:index_end]
    return out_list


def get_pid(process):
    top_lines = get_top(bugreport_lines)
    dct = {}
    for line in top_lines:
        try:
            words = line.split()
            if len(words) < 10:
                continue
            name = words[-1]
            pid = int(words[0])
            tid = int(words[1])
            user = words[2]
            if pid == tid:
                dct[name] = pid
        except:
            pass
    if process in dct:
        return dct[process]
    else:
        raise Exception('没有 %s 这个进程' % process)


def get_perfevents():
    event_list = []
    event_id = 1
    first_index = 0
    last_index = 0
    for index in range(len(bugreport_lines)):
        if '------------- start of perfeventstats --------------' \
                in bugreport_lines[index]:
            first_index = index + 1
        if '----- end of perfeventstats ----' in bugreport_lines[index]:
            last_index = index

    if not first_index or not last_index:
        return []

    for line in bugreport_lines[first_index:last_index]:
        if 'eventTypeName' not in line:
            continue
        event_type, json_str = line.split(':', 1)
        try:
            event_d = json.loads(json_str)
            event_d['eventId'] = event_id
            event_list.append(event_d)
            event_id = event_id + 1
        except:
            pass

    return event_list


def filter_perfevents(events,
                      pid: str=None,
                      tid: str=None,
                      duration: str=None,
                      process: str=None,
                      type: str=None,
                      grep: str=None) -> list:
    rst_events = []
    for event_d in events:
        if process:
            if 'processName' not in event_d \
                    or process not in event_d['processName']:
                continue
        if type and type not in event_d['eventTypeName']:
            continue
        if pid:
            if 'pid' not in event_d or event_d['pid'] != pid:
                continue
        if tid:
            if 'threadId' not in event_d or event_d['threadId'] != tid:
                continue
        if duration:
            if 'endTime' not in event_d or 'beginTime' not in event_d:
                continue
            end_time = int(event_d['endTime'])
            start_time = int(event_d['beginTime'])
            if int(duration) > (end_time - start_time):
                continue
        rst_events.append(event_d)
    return rst_events


def print_event(event_d, print_policy=False):
    if not print_policy:
        if 'schedGroup' in event_d:
            del event_d['schedGroup']
        if 'priority' in event_d:
            del event_d['priority']
        if 'policy' in event_d:
            del event_d['policy']
    if 'runnableTime' in event_d:
        del event_d['runnableTime']
    if 'runningTime' in event_d:
        del event_d['runningTime']
    if 'sleepingTime' in event_d:
        del event_d['sleepingTime']
    if 'seq' in event_d:
        del event_d['seq']
    if 'endRealTime' in event_d:
        del event_d['endRealTime']
    if 'eventFlags' in event_d:
        del event_d['eventFlags']
    if 'eventType' in event_d:
        del event_d['eventType']
    if 'packageName' in event_d and not event_d['packageName']:
        del event_d['packageName']

    dur = event_d['endTime'] - event_d['beginTime']
    print(event_d['eventTypeName'])
    print(json.dumps(event_d, indent=4, separators=(',', ':'), sort_keys=True))
    print('duration: %d\n' % dur)


def print_perfevents(events):
    for event_d in events:
        if 'endTime' not in event_d or 'beginTime' not in event_d:
            continue
        print_event(event_d)


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


def print_version():
    print('Version: ' + VERSION)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('categories',
                        nargs='*',
                        help='需要显示的内容分类')
    parser.add_argument('-f',
                        '--file',
                        help='指定文件作为数据源',
                        dest='file')
    parser.add_argument('-p',
                        '--pid',
                        type=int,
                        help='指定进程 PID')
    parser.add_argument('-t',
                        '--tid',
                        type=int,
                        help='指定线程 TID')
    parser.add_argument('-m',
                        '--minute',
                        type=int,
                        help='只显示最近 MINUTE 分钟的日志')
    parser.add_argument('-r',
                        '--rule',
                        type=str,
                        help='使用自定义规则')
    parser.add_argument('-l',
                        '--list-categories',
                        action='store_true',
                        help='显示可用的内容分类',
                        dest='list')
    parser.add_argument('-v',
                        '--version',
                        action='store_true',
                        help='显示版本')
    return parser.parse_args()


def get_target_rule(name):
    from os import path, readlink
    file_path = path.join(path.dirname(readlink(__file__)), 'rules.xml')
    tree = ET.ElementTree(file=file_path)
    for e in tree.iter(tag='rule'):
        if e.attrib['name'] == name:
            target_element = e
    if not target_element:
        raise Exception('没找到符合要求的 rule')
    return target_element


bugreport_lines = []
all_system_logs = []
all_events_logs = []
all_perfevents = []


def main():
    args = parse_arguments()

    if args.version:
        print_version()
        return

    if args.list:
        show_categories()
        return

    if not args.file:
        print('请使用 -f 指定 bugreport, 或使用 -h 查看使用说明')
        return

    global bugreport_lines, all_system_logs, all_events_logs, all_perfevents
    bugreport_lines = read_lines(args.file)
    all_perfevents = get_perfevents()
    all_system_logs, all_events_logs = get_logs(args.minute)

    system_logs = []
    events_logs = []
    perfevents = []

    if args.rule:
        rule = get_target_rule(args.rule)
        for condition in rule:
            if condition.tag == 'log':
                attr = condition.attrib
                system_logs.extend(filter_log(all_system_logs, **attr))
            elif condition.tag == 'elog':
                attr = condition.attrib
                events_logs.extend(filter_log(all_events_logs, **attr))
            elif condition.tag == 'perfevent':
                attr = condition.attrib
                perfevents.extend(filter_perfevents(all_perfevents, **attr))

    if 'log' in args.categories:
        system_logs.extend(filter_log(all_system_logs, pid=args.pid, tid=args.tid))

    if 'events' in args.categories:
        events_logs.extend(filter_log(all_events_logs, pid=args.pid, tid=args.tid))

    # 去重 排序
    system_logs = list(set(system_logs)) # todo: too low
    system_logs.sort(key=lambda log: log.time)
    print_logs(system_logs)
    events_logs = list(set(events_logs))
    events_logs.sort(key=lambda log: log.time)
    print_logs(events_logs)
    print_perfevents(perfevents)

    if 'pss' in args.categories:
        print_lines(get_total_pss())

    if 'meminfo' in args.categories:
        print_lines(get_proc_meminfo())

    if 'pagetypeinfo' in args.categories:
        print_lines(get_proc_pagetypeinfo())

    if 'cpu' in args.categories:
        print_lines(get_cpu_info())

    if 'kernel' in args.categories:
        print_lines(get_dmesg())

    if 'uptime' in args.categories:
        print_lines([get_uptime()])

    if 'ps' in args.categories:
        print_lines(get_ps())

    if 'top' in args.categories:
        print_lines(get_top())


if __name__ == '__main__':
    main()
