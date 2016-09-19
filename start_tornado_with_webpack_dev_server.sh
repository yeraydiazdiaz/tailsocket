#!/bin/sh

echo "Start" > tailsocket.log
PYTHONASYNCIODEBUG=1 python tailsocket/application.py --webpackdevserver=http://localhost:8080/static/bin --logging=debug
