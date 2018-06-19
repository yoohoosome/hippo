# HippoTool

## 工具介绍

hippo 是一个帮助分析 bugreport 的工具. 

bugreport 的内容非常多, 看起来很痛苦, 因此我们希望有这样一个工具, 它能帮助我们快速找到我们关注的性能信息, 并且使用简单.

## 使用方法

第一步, 下载该 git 仓库.

第二步, 为了更方便地使用, 我们建议您将 hippo.py 改为可执行, 并创建软链接, 将链接放在 PATH 路径中, 这里假设是 `/home/mi/bin`

```
$ sudo chmod a+x hippo.py
$ ln -s /home/mi/bin/hippo <仓库路径>/hippo.py
```

第三步, 开始使用, 通过 -h 查看说明

```
$ hippo -h
usage: parse_bugreport.py [-h] [-p PID] [-e] file

positional arguments:
  file               指定文件作为数据源

optional arguments:
  -h, --help         show this help message and exit
  -p PID, --pid PID  进程 pid
  -e, --events       解析 events log
```

## 使用举例

### 查看 system log

```
$ hippo bugreport_1526359678499.log -p 1024
```

该命令会将 bugreport 中进程号为 1024 的 system log 输出到终端. 

您还可以通过 grep 命令进行二次过滤.

### 查看 events log

```
$ hippo bugreport_1526359678499.log -e
```

该命令会将 bugreport 中 events log 输出到终端.