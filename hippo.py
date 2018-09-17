#!/usr/bin/env python3

import argparse
import re
import zipfile
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

VERSION = '0.7.2'


# Set Color Class
class Colors:
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
    print(Colors.YELLOW + string + Colors.ENDC)


def print_yellow(string):
    print(Colors.BLUE + string + Colors.ENDC)


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


sysui_action_dct = {
    '127': 'NOTIFICATION_PANEL',
    '252': 'ACTION_FINGERPRINT_AUTH',
    '319': 'APP_TRANSITION_DELAY',
    '321': 'STARTING_WINDOW_DELAY',
    '322': 'WINDOWS_DRAWN_DELAY',
    '325': 'DEVICE_UPTIME_SECONDS',
    '757': 'CATEGORY',
    '758': 'TYPE',
    '759': 'SUBTYPE',
    '793': 'NOTIFICATION_SINCE_CREATE_MS',
    '794': 'NOTIFICATION_SINCE_VISIBLE_MS',
    '795': 'NOTIFICATION_SINCE_UPDATE_MS',
    '799': 'NAME',
    '801': 'BUCKET',
    '802': 'VALUE',
    '803': 'PACKAGE',
    '804': 'HISTOGRAM',
    '805': 'TIMESTAMP',
    '806': 'PACKAGE',
    '857': 'FIELD_NOTIFICATION_CHANNEL_ID',
    '871': 'ACTIVITY',
    '904': 'CALLING_PACKAGE',
    '905': 'IS_EPHEMERAL',
    '945': 'BIND_APPLICATION_DELAY',
    '947': 'FIELD_NOTIFICATION_GROUP_SUMMARY',
}


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
        if self.tag == 'sysui_multi_action' \
                or self.tag == 'sysui_action' \
                or self.tag == 'sysui_view_visibility':
            words = self.message.lstrip('[').rstrip(']').split(',')
            if len(words) % 2 != 0:
                raise Exception('sysui_multi_action 解析失败: %s' % self.message)
            message = '['
            for i in range(0, len(words), 2):
                k, v = words[i], words[i + 1]
                if k in sysui_action_dct:
                    message = message + '%s,%s,' % (sysui_action_dct[k], v)
                else:
                    message = message + '%s,%s,' % (k, v)
            self.message = message.rstrip(',') + ']'
        elif self.tag == '[30089]':
            self.tag = 'skipped_frames'

    def __str__(self):
        pid_str = str(self.pid)
        if self.pid < 100:
            pid_str = '   ' + pid_str
        elif self.pid < 1000:
            pid_str = '  ' + pid_str
        elif self.pid < 10000:
            pid_str = ' ' + pid_str
        tid_str = str(self.tid)
        if self.tid < 100:
            tid_str = '   ' + tid_str
        elif self.tid < 1000:
            tid_str = '  ' + tid_str
        elif self.tid < 10000:
            tid_str = ' ' + tid_str
        time_str = self.time.strftime('%m-%d %H:%M:%S.%f')[:-3]

        return '%s %s %s %s %s: %s' % (time_str, pid_str, tid_str,
                                       self.priority, self.tag, self.message)


def priority2level(level_str: str) -> int:
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


def read_lines(file_name: str) -> list:
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


def get_logs(minute: int = None) -> (list, list):
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
            [log for log in system_logs if
             start_time < log.time <= report_time]
        events_logs = \
            [log for log in events_logs if
             start_time < log.time <= report_time]

    return system_logs, events_logs


def filter_log(logs: list,
               pid: str = None,
               tid: str = None,
               tag: str = None,
               grep: str = None,
               priority: str = None,
               process: str = None,
               **kwargs) -> (list, list):
    target_logs = []
    rest_logs = []
    if process:
        pid = get_pid(process)
    for entry in logs:
        if pid and entry.pid != int(pid):
            rest_logs.append(entry)
            continue
        if tid and entry.tid != int(tid):
            rest_logs.append(entry)
            continue
        if tag and tag not in entry.tag:
            rest_logs.append(entry)
            continue
        if grep and grep not in entry.message:
            rest_logs.append(entry)
            continue
        if priority and entry.level < priority2level(priority):
            rest_logs.append(entry)
            continue
        target_logs.append(entry)
    return target_logs, rest_logs


def get_proc_meminfo() -> list:
    for i in range(len(bugreport_lines)):
        if 'MEMORY INFO (/proc/meminfo)' in bugreport_lines[i]:
            index_start = i
        if "was the duration of 'MEMORY INFO'" in bugreport_lines[i]:
            index_end = i

    out_list = bugreport_lines[index_start:index_end]
    return out_list


def get_proc_pagetypeinfo() -> list:
    for i in range(len(bugreport_lines)):
        if 'PAGETYPEINFO (/proc/pagetypeinfo)' in bugreport_lines[i]:
            index_start = i
        if "was the duration of 'PAGETYPEINFO'" in bugreport_lines[i]:
            index_end = i

    out_list = bugreport_lines[index_start:index_end]
    return out_list


def get_total_pss() -> list:
    for i in range(len(bugreport_lines)):
        if 'Total PSS by process' in bugreport_lines[i]:
            index_start = i
        if "was the duration of 'DUMPSYS MEMINFO'" in bugreport_lines[i]:
            index_end = i

    out_list = bugreport_lines[index_start:index_end]
    return out_list


def get_cpu_info() -> list:
    for i in range(len(bugreport_lines)):
        if 'DUMPSYS CPUINFO (/system/bin/dumpsys -t 10 cpuinfo -a)' \
                in bugreport_lines[i]:
            first_index = i
        if "was the duration of 'DUMPSYS CPUINFO'" in bugreport_lines[i]:
            last_index = i

    out_list = bugreport_lines[first_index:last_index]
    return out_list


def get_dmesg() -> list:
    for i in range(len(bugreport_lines)):
        if '------ KERNEL LOG (dmesg) ------' in bugreport_lines[i]:
            first_index = i
        if "was the duration of 'KERNEL LOG (dmesg)'" in bugreport_lines[i]:
            last_index = i

    out_list = bugreport_lines[first_index:last_index]
    return out_list


def get_uptime() -> list:
    uptime_list = []
    for i in range(len(bugreport_lines)):
        if '------ UPTIME (uptime) ------' in bugreport_lines[i]:
            uptime_list.append(bugreport_lines[i + 1])

    if not uptime_list:
        return 'Failed to get uptime'

    #  10:56:03 up 18:41,  0 users,  load average: 5.51, 9.09, 9.09
    return uptime_list[0]


def get_report_time(elogs) -> datetime:
    for log in elogs:
        if log.tag == 'am_proc_start' and 'com.miui.bugreport' in log.message:
            report_time = log.time
    return report_time


def get_ps() -> list:
    for i in range(len(bugreport_lines)):
        if '------ PROCESSES AND THREADS (ps' in bugreport_lines[i]:
            index_start = i
        if "was the duration of 'PROCESSES AND THREADS'" in bugreport_lines[i]:
            index_end = i

    out_list = bugreport_lines[index_start:index_end]
    return out_list


def get_top() -> list:
    for index in range(len(bugreport_lines)):
        if '------ CPU INFO (top' in bugreport_lines[index]:
            index_start = index
        if "was the duration of 'CPU INFO'" in bugreport_lines[index]:
            index_end = index

    out_list = bugreport_lines[index_start:index_end]
    return out_list


top_lines = []


def get_pid(process: str) -> int:
    global top_lines
    if not top_lines:
        top_lines = get_top()
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


def get_perfevents() -> list:
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

    uptime_diff = 0
    for line in bugreport_lines[first_index:last_index]:
        if 'eventTypeName' not in line:
            continue
        event_type, json_str = line.split(':', 1)
        try:
            event_d = json.loads(json_str)
            if event_d['eventTypeName'] == 'JankRecord':
                occur_time = event_d['occurTime']
                received_uptime = event_d['receivedUptime']
                received_current_time = event_d['receivedCurrentTime']
                uptime_diff = received_current_time - received_uptime
                uptime = occur_time + uptime_diff
                time = datetime.fromtimestamp(uptime / 1000)
                event_d['timestamp'] = time.strftime('%m-%d %H:%M:%S.%f')[:-3]
            elif 'beginTime' in event_d and uptime_diff:
                uptime = event_d['beginTime'] + uptime_diff
                time = datetime.fromtimestamp(uptime / 1000)
                event_d['timestamp'] = time.strftime('%m-%d %H:%M:%S.%f')[:-3]
            event_d['eventId'] = event_id
            event_list.append(event_d)
            event_id = event_id + 1
        except:
            pass

    return event_list


def filter_perfevents(events,
                      pid: str = None,
                      tid: str = None,
                      duration: str = None,
                      process: str = None,
                      type: str = None,
                      **kwargs) -> list:
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
            if 'maxDuration' in event_d and event_d['maxDuration'] < int(duration):
                continue
            if 'endTime' in event_d and 'beginTime' in event_d:
                end_time = int(event_d['endTime'])
                start_time = int(event_d['beginTime'])
                if (end_time - start_time) < int(duration):
                    continue
        rst_events.append(event_d)
    return rst_events


def print_event(event_d: dict, print_policy=False):
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

    print(event_d['eventTypeName'])
    print(json.dumps(event_d, indent=4, separators=(',', ':'), sort_keys=True))

    if 'endTime' in event_d and 'beginTime' in event_d:
        dur = event_d['endTime'] - event_d['beginTime']
        print('duration: %d\n' % dur)
    if 'maxFrameDuration' in event_d:
        print('maxDuration: %d' % event_d['maxFrameDuration'])
        print('totalDuration: %d\n' % event_d['totalDuration'])


def print_perfevents(events: list):
    for event_d in events:
        print_event(event_d)


def show_categories():
    print('           dmesg - dmesg')
    print('          uptime - uptime')
    print('         cpuinfo - dumpsys cpuinfo')
    print('             top - top')
    print('              ps - ps')
    print('             pss - total pss')
    print('         meminfo - cat /proc/meminfo')
    print('    pagetypeinfo - cat /proc/pagetypeinfo')


def show_rules():
    print('您可以直接使用以下规则:')
    show_categories()
    file_path = get_rules_path()
    tree = ET.ElementTree(file=file_path)
    for e in tree.iter(tag='rule'):
        name = e.attrib['name']
        if len(name) < 16:
            name = (16 - len(name)) * ' ' + name
        if 'describe' in e.attrib:
            print('%s - %s' % (name, e.attrib['describe']))
        else:
            print(name)
    print('\n您还可以在 %s 中扩展上面的规则' % file_path)


def show_summary(file_name: str):
    if not zipfile.is_zipfile(file_name):
        return

    with zipfile.ZipFile(file_name) as z:
        for file_name in z.namelist():
            if file_name == 'summary.txt':
                with z.open(file_name) as f:
                    summary_str = f.read().decode('utf-8')
                    summary_d = json.loads(summary_str)
                    print('反馈时间     %s' % summary_d['timestamp'])
                    print('反馈内容     %s' % summary_d['content'])
            if file_name == 'sys_version.txt':
                with z.open(file_name) as f:
                    summary_str = f.read().decode('utf-8')
                    info_d = json.loads(summary_str)
                    print('机型         %s, %s' % (info_d['model'], info_d['deviceName']))
                    print('平台         %s, %s' % (info_d['productHardware'], info_d['productBoard']))
                    print('Android      %s' % info_d['osVersion'])
                    print('MIUI         %s, %s' % (info_d['miVersion'], info_d['miuiBigVersion']))
                    print('region       %s' % info_d['region'])
                    print('buildType    %s' % info_d['buildType'])
                    print('buildId      %s' % info_d['buildId'])
                    print('networkName  %s' % info_d['networkName'])


def show_events_hint():
    print('cpu (total|1|6),(user|1|6),(system|1|6),(iowait|1|6),(irq|1|6),'
          '(softirq|1|6)')
    print('am_pss (Pid|1|5),(UID|1|5),(Process Name|3),(Pss|2|2),(Uss|2|2),(SwapPss|2|2)')
    print('dvm_lock_sample (process|3),(main|1|5),(thread|3),(time|1|3),(file|3),(line|1|5),(ownerfile|3),(ownerline|1|5),(sample_percent|1|6)')
    print('binder_sample (descriptor|3),(method_num|1|5),(time|1|3),(blocking_package|3),(sample_percent|1|6)')
    print('am_lifecycle_sample (User|1|5),(Process Name|3),(MessageCode|1|5),(time|1|3)')
    print('am_activity_launch_time (User|1|5),(Token|1|5),(Component Name|3),(time|2|3)')
    print('am_mem_factor (Current|1|5),(Previous|1|5)')

def print_version():
    print('Version: ' + VERSION)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('file',
                        nargs='?',
                        help='指定文件作为数据源 (支持 zip 包)')
    parser.add_argument('rule',
                        nargs='?',
                        default='summary',
                        help='指定规则名')
    parser.add_argument('-m',
                        '--minute',
                        type=int,
                        help='只显示最近 MINUTE 分钟的日志')
    parser.add_argument('-l',
                        '--list-rules',
                        action='store_true',
                        help='显示可用的规则',
                        dest='list')
    parser.add_argument('-v',
                        '--version',
                        action='store_true',
                        help='显示版本')
    parser.add_argument('--hint',
                        action='store_true',
                        help='显示 events log 含义提示')
    return parser.parse_args()

def get_rules_path():
    from os import path, readlink
    if path.islink(__file__):
        dirname = path.dirname(readlink(__file__))
        if dirname.startswith('..'):
            # 链接使用相对路径
            dirname = path.join(path.dirname(__file__), dirname)
    else:
        dirname = path.dirname(__file__)
    return path.join(dirname, 'rules.xml')

def get_target_rule(name):
    file_path = get_rules_path()
    tree = ET.ElementTree(file=file_path)
    target_element = None
    for e in tree.iter(tag='rule'):
        if e.attrib['name'] == name:
            target_element = e
    if not target_element:
        raise Exception('没找到您要的规则: %s' % name)
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
        show_rules()
        return

    if args.hint:
        show_events_hint()
        return

    if not args.file:
        print('终于等到你!')
        print('请指定一份 bugreport, 比如 hippo 2018-07-29-112838-59434332-k6ZXjO4LYb.zip')
        return

    if args.rule == 'summary':
        show_summary(args.file)
        return

    global bugreport_lines, all_system_logs, all_events_logs, all_perfevents
    bugreport_lines = read_lines(args.file)
    all_perfevents = get_perfevents()
    all_system_logs, all_events_logs = get_logs(args.minute)

    if 'pss' == args.rule:
        print_lines(get_total_pss())
        return

    if 'meminfo' == args.rule:
        print_lines(get_proc_meminfo())
        return

    if 'pagetypeinfo' == args.rule:
        print_lines(get_proc_pagetypeinfo())
        return

    if 'cpuinfo' == args.rule:
        print_lines(get_cpu_info())
        return

    if 'dmesg' == args.rule:
        print_lines(get_dmesg())
        return

    if 'uptime' == args.rule:
        print_lines([get_uptime()])
        return

    if 'ps' == args.rule:
        print_lines(get_ps())
        return

    if 'top' == args.rule:
        print_lines(get_top())
        return

    system_logs = []
    events_logs = []
    perfevents = []

    rule = get_target_rule(args.rule)
    for condition in rule:
        if condition.tag == 'log':
            attr = condition.attrib
            if 'mute' in attr and attr['mute'] == 'true':
                target_logs, rest_logs = filter_log(system_logs, **attr)
                system_logs = rest_logs
            else:
                target_logs, rest_logs = filter_log(all_system_logs,
                                                    **attr)
                system_logs.extend(target_logs)
        elif condition.tag == 'elog':
            attr = condition.attrib
            if 'mute' in attr and attr['mute'] == 'true':
                target_logs, rest_logs = filter_log(events_logs, **attr)
                events_logs = rest_logs
            else:
                target_logs, rest_logs = filter_log(all_events_logs,
                                                    **attr)
                events_logs.extend(target_logs)
        elif condition.tag == 'perfevent':
            attr = condition.attrib
            perfevents.extend(filter_perfevents(all_perfevents, **attr))

    # 去重 排序
    logs = list(set(system_logs + events_logs))  # todo: too low
    logs.sort(key=lambda log: log.time)
    print_logs(logs)
    print_perfevents(perfevents)


if __name__ == '__main__':
    main()
