# HippoTool

## 工具介绍

hippo 是一个帮助分析 bugreport 的工具. 

bugreport 的内容非常多, 看起来很痛苦, 因此我们希望有这样一个工具, 它能帮助我们快速找到我们关注的性能信息, 并且使用简单.

## 使用方法

第一步, 下载该 git 仓库.

第二步, 为了更方便地使用, 我们建议您将 hippo.py 改为可执行, 并创建软链接, 将链接放在 PATH 路径中, 这里假设是 `/home/mi/bin`

```
$ sudo chmod a+x hippo.py
$ ln -s <仓库路径>/hippo.py /home/mi/bin/hippo
```

第三步, 开始使用, 通过 -h 查看说明

```
$ hippo -h
usage: hippo [-h] [-f FILE] [-p PID] [-t TID] [-l]
             [categories [categories ...]]

positional arguments:
  categories            需要显示的内容

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  指定文件作为数据源
  -p PID, --pid PID     指定进程 pid
  -t TID, --tid TID     指定线程 tid
  -l, --list-categories
                        list the available categories and exit
```

## 使用举例

hippo 的使用方法类似 systrace, 可以通过 -l 查看所有支持的 categories, 然后选择感兴趣的部分输出.

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
$ hippo -f bugreport_1526359678499.log log -p 1581 | grep input
```

该命令会将 bugreport 中进程号为 1581 的 system log 输出到终端. 

您还可以通过 grep 命令进行二次过滤.

### 查看 events log

```
$ hippo -f bugreport_1526359678499.log events -t 17699
```

该命令会将 bugreport 中线程号 17399的 events log 输出到终端.

### 查看 meminfo 和 pagetypeinfo

```
$ hippo -f bugreport_1526359678499.log meminfo pagetypeinfo
```
