# Getting Started

## 1 工具介绍

hippo 是一个帮助查看 bugreport 的终端工具. 

bugreport 的内容非常多, 看起来很痛苦, 因此我们希望有这样一个工具, 它能帮助我们快速定位我们关注的性能信息, 并且使用简单.

## 2 准备

第一步, clone [仓库](http://git.n.xiaomi.com/sangyaohui/hippotool/tree/master) http://git.n.xiaomi.com/sangyaohui/hippotool.git

第二步, 为了更方便地使用, 建议您将 hippo.py 改为可执行, 并 **创建链接**, 将链接放在 PATH 路径中, 这里假设是 `/home/mi/bin`

```
$ sudo chmod a+x hippo.py
$ ln -s <仓库绝对路径>/hippo.py <PATH>/hippo
```

第三步, 开始使用, 通过 -h 查看说明

```
$ hippo -h
usage: hippo [-h] [-m MINUTE] [-l] [-v] [--hint] [file] [rule]

positional arguments:
  file                  指定文件作为数据源 (支持 zip 包)
  rule                  自定义规则

optional arguments:
  -h, --help            show this help message and exit
  -m MINUTE, --minute MINUTE
                        只显示最近 MINUTE 分钟的日志
  -l, --list-rules      显示可用的规则
  -v, --version         显示版本
  --hint                显示 events log 含义提示
```

## 3 使用

### 3.1 查看 bugreport

指定 bugreport 默认输出用户反馈信息.

```
$ hippo 2018-07-29-112838-59434332-k6ZXjO4LYb.zip          
反馈时间     2018-07-29-112717
反馈内容     微信界面，下拉通知，打字都非常卡。比如刚才的11点20多分的时候
机型         MI 6, sagit
平台         qcom, msm8998
Android      8.0.0
MIUI         8.7.26, V10
region       CN
buildType    user
buildId      OPR1.170623.027
imeiSha1     f1d9f47adc700531d3862c69d6138c062722acda
imeiSha2     1d213c56bc6637093a5aa1525fc76f83f8aec3b79ee8358f8f6eb7483cb06c15
networkName  中国移动
```

类似 systrace, 使用 `hippo -l` 显示可以使用的规则.

```
$ hippo -l
您可以直接使用以下规则:
           dmesg - dmesg
          uptime - uptime
         cpuinfo - dumpsys cpuinfo
             top - top
              ps - ps
             pss - total pss
         meminfo - cat /proc/meminfo
    pagetypeinfo - cat /proc/pagetypeinfo
          report - 用户启动用户反馈的时间
             key - 实体键事件处理
    notification - 通知相关
          screen - 锁屏与解锁
          events - events log
             log - system log
            perf - perfevents
             ams - AMS 相关
             wms - WMS 相关
           input - 输入相关
             cpu - cpu 负载
            home - 桌面进程
        systemui - systemui 进程
          system - system_server 进程
          weixin - com.tencent.mm 进程
              im - sogou 输入法进程
            lock - 等锁
            slow - 各种超时
        lockhold - perfevents: system_server 中超过 200ms 的持锁
             jni - perfevents: system_server 中超过 200ms 的 JNI 调用
        duration - perfevents: system_server 中超过 1000ms 的所有事件
            jank - perfevents: 超过 100ms 的绘制卡顿

您还可以在 /home/sang/gitProjects/hippotool/rules.xml 中扩展上面的规则
```

指定规则输出. 比如查看 meminfo, 第一个参数是 bugreport, 第二个参数是规则名

```
$ hippo 2018-07-29-112838-59434332-k6ZXjO4LYb.zip meminfo
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

### 3.2 按时间过滤

(1) 缩小时间范围

用 -m MINUTE, 只输出最近 MINUTE 分钟的 log, 结束时间是用户反馈 App 的启动时间.

比如, 只显示最近 1 分钟的超时日志.

```
$ hippo 2018-07-29-112838-59434332-k6ZXjO4LYb.zip slow -m 1
07-29 11:25:23.691  1354  1410 D BatteryStatsImpl: Reading cpu stats took 380 ms
07-29 11:25:33.374  1354  1354 I am_lifecycle_sample: [0,NULL,200,3797]
07-29 11:25:33.389 26758 26758 I Choreographer: Skipped 61 frames!  The application may be doing too much work on its main thread.
07-29 11:25:33.423  1354  1426 I sysui_multi_action: [APP_TRANSITION_DELAY,1107,WINDOWS_DRAWN_DELAY,1108,DEVICE_UPTIME_SECONDS,83324,CATEGORY,761,TYPE,9,SUBTYPE,2,PACKAGE,com.tencent.mm,ACTIVITY,com.tencent.mm.ui.LauncherUI,IS_EPHEMERAL,0]
07-29 11:25:35.019 26912 26912 I dvm_lock_sample: [com.tencent.mm:push,1,main,823,SourceFile,167,Binder.java,-2,0]
07-29 11:25:35.041 26758 26758 I Choreographer: Skipped 50 frames!  The application may be doing too much work on its main thread.
07-29 11:25:40.477 26758 26758 I Choreographer: Skipped 270 frames!  The application may be doing too much work on its main thread.
07-29 11:25:44.819 26758 26758 I Choreographer: Skipped 148 frames!  The application may be doing too much work on its main thread.
07-29 11:25:44.824  2174  2174 I Choreographer: Skipped 198 frames!  The application may be doing too much work on its main thread.
07-29 11:25:49.689 26758 26758 I Choreographer: Skipped 190 frames!  The application may be doing too much work on its main thread.
07-29 11:25:52.634 26758 26758 I Choreographer: Skipped 170 frames!  The application may be doing too much work on its main thread.
07-29 11:25:57.648  1354  1426 I sysui_multi_action: [APP_TRANSITION_DELAY,123,WINDOWS_DRAWN_DELAY,127,DEVICE_UPTIME_SECONDS,83349,CATEGORY,761,TYPE,9,SUBTYPE,2,PACKAGE,com.miui.home,ACTIVITY,com.miui.home.launcher.Launcher,IS_EPHEMERAL,0]
07-29 11:26:08.774  1354  1426 I sysui_multi_action: [APP_TRANSITION_DELAY,97,STARTING_WINDOW_DELAY,97,WINDOWS_DRAWN_DELAY,409,DEVICE_UPTIME_SECONDS,83360,CATEGORY,761,TYPE,7,SUBTYPE,1,PACKAGE,com.miui.userguide,ACTIVITY,com.miui.userguide.HomeActivity,IS_EPHEMERAL,0,BIND_APPLICATION_DELAY,76]
```

## 4 自定义规则

### 4.1 介绍

自定义规则可以帮忙您快速定义已知问题.

您可以将常见问题的关键日志补充到自定义规则. 使用自定义规则排查已知问题时, 可以减少重复的劳动.

### 4.2 如何使用

使用一个名为 slow 的自定义规则的方法是 `hippo -f 2018-05-15-094808-48215937-4QUpycmkyR.zip -r slow`

### 4.3 如何定义

所有的自定义规则都定义在 rules.xml 文件中, 每一个规则对应一个 rule 标签.

下面是一个名为 slow 的自定义规则, 它会帮您匹配出 dvm_lock_sample binder_sample 等 events log, 和包含关键字的 system log

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
priority | 优先级, 可以是 `VDIWE` | `<log priority="W"/>`
grep | 过滤关键词 | `<log grep="timeout"/>`
mute | 屏蔽 log | `<log tag="chatty" mute="true"/>`

说明:

当 `mute="true"` 则满足条件的 log 会被屏蔽.


(2) `<perfevent/>` 表示 perfevents (请先确认您的机型是否已经移植了 perfevents)

属性 | 含义 | 举例
--- | --- | ---
process | 进程名 | `<perfevent process="system_server"/>`
pid | 进程号 | `<perfevent pid="2100"/>`
tid | 线程号 | `<perfevent tid="2100"/>`
type | 类型 | `<perfevent type="JniMethod"/>`
duration | 耗时 | `<perfevent duration="200"/>`
