# HippoTool

## 工具介绍

hippo 是一个帮助查看 bugreport 的终端工具. 

bugreport 的内容非常多, 看起来很痛苦, 因此我们希望有这样一个工具, 它能帮助我们快速定位我们关注的性能信息, 并且使用简单.

## 准备

第一步, clone [仓库](http://git.n.xiaomi.com/sangyaohui/hippotool/tree/master) http://git.n.xiaomi.com/sangyaohui/hippotool.git

第二步, 为了更方便地使用, 建议您将 hippo.py 改为可执行, 并创建链接, 将链接放在 PATH 路径中, 这里假设是 `/home/mi/bin`

```
$ sudo chmod a+x hippo.py
$ ln -s <仓库路径>/hippo.py /home/mi/bin/hippo
```

第三步, 开始使用, 通过 -h 查看说明

```
$ hippo -h
usage: hippo [-h] [-f FILE] [-p PID] [-t TID] [-m MINUTE] [-l] [-v]
             [categories [categories ...]]

positional arguments:
  categories            需要显示的内容分类

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  指定文件作为数据源
  -p PID, --pid PID     指定进程 PID
  -t TID, --tid TID     指定线程 TID
  -m MINUTE, --minute MINUTE
                        只显示最近 MINUTE 分钟的日志
  -l, --list-categories
                        显示可用的内容分类
  -v, --version         显示版本

```

## 使用

hippo 的使用方法类似 systrace, 可以通过 `hippo -l` 查看所有支持的 categories, 然后选择感兴趣的部分输出.

### 查看支持的 categories

```
$ hippo -l
         log - system log
      events - events log
      kernel - dmesg
      uptime - uptime
         cpu - dumpsys cpuinfo
         top - top
          ps - ps
         pss - total pss
     meminfo - cat /proc/meminfo
pagetypeinfo - cat /proc/pagetypeinfo
```

### 查看 system log

```
$ hippo -f bugreport_1526359678499.log log -p 1575 | grep Slow
06-12 10:48:04.275 1575 17699	W ActivityManager: Slow operation: 1660ms so far, now at startProcess: returned from zygote!
06-12 10:48:04.531 1575 17699	W ActivityManager: Slow operation: 1916ms so far, now at startProcess: done updating battery stats
06-12 10:48:04.534 1575 17699	W ActivityManager: Slow operation: 1920ms so far, now at startProcess: building log message
06-12 10:48:04.548 1575 17699	W ActivityManager: Slow operation: 1934ms so far, now at startProcess: starting to update pids map
06-12 10:48:04.548 1575 17699	W ActivityManager: Slow operation: 1934ms so far, now at startProcess: done updating pids map
06-12 10:48:04.558 1575 17699	W ActivityManager: Slow operation: 1943ms so far, now at startProcess: done starting proc!
06-12 10:48:15.595 1575 11235	W ActivityManager: Slow operation: 1654ms so far, now at attachApplicationLocked: after mServices.attachApplicationLocked
```

该命令会将 bugreport 中进程号为 1575 的 system log 输出到终端. 

您还可以通过 grep 命令进行二次过滤.

### 查看 events log

```
$ hippo -f bugreport_1526359678499.log events -t 1668
06-12 10:48:41.641 1575 1668	I dvm_lock_sample: [system_server,0,android.ui,7626,ActivityManagerService.java,20286,ActivityStarter.java,815,0]
06-12 10:48:43.405 1575 1668	I dvm_lock_sample: [system_server,0,android.ui,1001,ActivityManagerService.java,4523,-,1675,0]
06-12 10:48:53.481 1575 1668	I sysui_action: [317,2]
06-12 10:48:53.481 1575 1668	I sysui_multi_action: [757,317,758,4,759,2]
06-12 10:50:22.980 1575 1668	I dvm_lock_sample: [system_server,0,android.ui,724,LocationManagerService.java,351,-,3197,0]
```

该命令会将 bugreport 中线程号 1668 的 events log 输出到终端.

### 查看进程信息

```
$ hippo -f bugreport_1528772162307.log top | grep android.ui
 1575  1668 system       18  -2  0.0 S 2.5G 295M  ta android.ui      system_server
```

### 查看 uptime

```
$ hippo -f bugreport_1528772162307.log uptime        
 10:56:03 up 18:41,  0 users,  load average: 5.51, 9.09, 9.09
```

### 查看 meminfo

```
$ hippo -f bugreport_1528772162307.log meminfo
------ MEMORY INFO (/proc/meminfo) ------
MemTotal:        3815220 kB
MemFree:           66364 kB
MemAvailable:     506696 kB
Buffers:           17732 kB
Cached:           572644 kB
SwapCached:            0 kB
Active:          2481136 kB
Inactive:         277532 kB
Active(anon):    2255896 kB
Inactive(anon):    50692 kB
Active(file):     225240 kB
Inactive(file):   226840 kB
Unevictable:       82848 kB
Mlocked:           82848 kB
SwapTotal:             0 kB
SwapFree:              0 kB
Dirty:               568 kB
Writeback:             0 kB
AnonPages:       2251196 kB
Mapped:           369824 kB
Shmem:             55780 kB
Slab:             254296 kB
SReclaimable:      88548 kB
SUnreclaim:       165748 kB
KernelStack:       65296 kB
PageTables:        75108 kB
NFS_Unstable:          0 kB
Bounce:                0 kB
WritebackTmp:          0 kB
CommitLimit:     1907608 kB
Committed_AS:   137304840 kB
VmallocTotal:   258867136 kB
VmallocUsed:           0 kB
VmallocChunk:          0 kB
CmaTotal:         163840 kB
CmaFree:               0 kB
```

其他内容就不一一列举了, 可以通过 -l 查看.