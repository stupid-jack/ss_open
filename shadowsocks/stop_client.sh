#!/bin/bash

cwd=$(cd `dirname $0` && pwd)
cd $cwd

server_path="$cwd/local.py"

pid=$(ps -e faux|egrep -v grep|egrep "$server_path"|awk '{print $2}')

kill $pid
