# HippoTool

## 工具介绍

hippo 是一个帮助查看 bugreport 的终端工具. 

bugreport 的内容非常多, 看起来很痛苦, 因此我们希望有这样一个工具, 它能帮助我们快速定位我们关注的性能信息, 并且使用简单.

## wiki

使用说明请移步 [wiki](http://wiki.n.miui.com/pages/viewpage.action?pageId=96999011)

## Release Note

v0.1:

将 bugreport 中的日志分割为 system log, events log, kernel log

v0.2:

支持 cpuinfo meminfo pagetyepinfo pss top ps 等内容

v0.3:

支持直接查看 zip 包, 比如 'hippo -f 2018-05-15-094808-48215937-4QUpycmkyR.zip kernel'

v0.4:

1. 支持 xml 文件中的自定义规则
1. 支持过滤最近 m 分钟的日志, 从 用户反馈 启动时间算起
1. 支持解析 perfevents

v0.5:

`<log/>` `<elog/>` 支持 mute 属性, 当 mute 为 true, 屏蔽满足条件的日志

v0.6:

自动翻译 sysui_multi_action 等 events log, 补充自定义规则

v0.7

1. 按时间顺序混排 system log 和 events log
1. 简化命令行参数: 第一个参数是 bugreport 文件, 第二个参数是规则, 比如 `hippo 2018-07-29-112838-59434332-k6ZXjO4LYb.zip slow`
1. `hippo -l` 改为显示所有可用规则
1. `hippo --hint` 显示常用 events log 含义提醒
1. 支持解析用户反馈信息, 使用方法 `hippo 2018-07-29-112838-59434332-k6ZXjO4LYb.zip` 或 `hippo 2018-07-29-112838-59434332-k6ZXjO4LYb.zip summary`