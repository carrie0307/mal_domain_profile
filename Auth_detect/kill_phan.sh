#!/bin/sh

# shell脚本 杀掉phantomjs的进程

ppid=$(ps -ef | grep phantomjs | grep -v grep | awk '{print $2}')
# ppid = $(pgrep -f phantomjs)

for element in $ppid
do
    echo $element
    kill $element
done
