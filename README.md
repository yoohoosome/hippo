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
