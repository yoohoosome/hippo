# Getting Started

## 1 工具介绍

hippo 是一个帮助查看 bugreport 的终端工具. 

bugreport 的内容非常多, 看起来很痛苦, 因此我们希望有这样一个工具, 它能帮助我们快速定位我们关注的性能信息, 并且使用简单.

## 2 准备

第一步, clone [仓库](http://git.n.xiaomi.com/sangyaohui/hippotool/tree/master) http://git.n.xiaomi.com/sangyaohui/hippotool.git

第二步, 为了更方便地使用, 建议您将 hippo.py 改为可执行, 并**创建链接**, 将链接放在 PATH 路径中, 这里假设是 `/home/mi/bin`

```
$ sudo chmod a+x hippo.py
$ ln -s <仓库绝对路径>/hippo.py <PATH>/hippo
```

第三步, 开始使用, 通过 -h 查看说明

```
$ hippo -h
usage: hippo [-h] [-f FILE] [-p PID] [-t TID] [-m MINUTE] [-r RULE] [-l] [-v]
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
  -r RULE, --rule RULE  使用自定义规则
  -l, --list-categories
                        显示可用的内容分类
  -v, --version         显示版本

```

## 3 使用

### 3.1 查看 bugreport

使用方法类似 systrace, 可以通过 `hippo -l` 查看所有支持的 categories, 然后选择感兴趣的部分输出.

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

比如查看 meminfo

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

### 3.2 支持 zip 包

两种方式都可以

    hippo -f bugreport_1526359678499.log meminfo

或

    hippo -f 2018-05-15-094808-48215937-4QUpycmkyR.zip meminfo

### 3.3 过滤 log

(1) 缩小时间范围

用 -m MINUTE, 只输出最近 MINUTE 分钟的 log, 结束时间是用户反馈 App 的启动时间.

比如, 只显示最近 3 分钟的 events log.


    hippo -f 2018-05-15-094808-48215937-4QUpycmkyR.zip events -m 3

(2) 指定 pid 或 tid

    hippo -f 2018-05-15-094808-48215937-4QUpycmkyR.zip log -p 2102
    hippo -f 2018-05-15-094808-48215937-4QUpycmkyR.zip log -t 2105

## 4 自定义规则

### 4.1 介绍

自定义规则可以帮忙您快速定义已知问题.

您可以将常见问题的关键日志补充到自定义规则. 使用自定义规则排查已知问题时, 可以减少重复的劳动.

### 4.2 如何使用

使用一个名为 slow 的自定义规则的方法是 `hippo -f 2018-05-15-094808-48215937-4QUpycmkyR.zip -r slow`

### 4.3 如何定义

所有的自定义规则都定义在 rules.xml 文件中, 每一个规则对应一个 rule 标签.

下面是一个名为 slow 的自定义规则, 它会帮您匹配出 dvm_lock_sample binder_sample 等 events log, 和包含制定关键字的 system log

```
<rule name="slow">
    <elog tag="dvm_lock_sample"/>
    <elog tag="binder_sample"/>
    <elog tag="am_lifecycle_sample"/>
    <log grep="Slow Operation" />
    <log grep="Slow Input" />
    <log grep="timeout" />
    <log tag="Looper" grep="Dispatch took" />
</rule>
```

rule 由规则项组成, 目前支持的规则项有 `<log/>` `<elog/>` `<perfevents/>`

(1) `<log/>` 和 `<elog/>` 分别表示 system log 和 events log, 它们都支持下面的属性:

属性 | 含义 | 举例
--- | --- | ---
tag | log 中的 tag | `<log tag="ActivityManager"/>`
process | 进程名 | `<log process="system_server"/>`
pid | 进程号 | `<log pid="2100"/>`
tid | 线程号 | `<log tid="2100"/>`
priority | 优先级, 可以是 VDIWE | `<log priority="W"/>`
grep | 过滤关键词 | `<log grep="timeout"/>`


(2) `<perfevent/>` 表示 perfevents (请先确认您的机型是否已经移植了 perfevents)

属性 | 含义 | 举例
--- | --- | ---
process | 进程名 | `<perfevent process="system_server"/>`
pid | 进程号 | `<perfevent pid="2100"/>`
tid | 线程号 | `<perfevent tid="2100"/>`
type | 类型 | `<perfevent type="JniMethod"/>`
duration | 耗时 | `<perfevent duration="200"/>`
