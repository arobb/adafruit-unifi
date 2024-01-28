#!/usr/bin/env python3
"""Daemon version of the main application"""
import syslog

import pidfile
import daemon

from main import run

if __name__ == '__main__':
    pid_path = '/tmp/adafruit-unifi.pid'
    pid_ctx = pidfile.PidFile(pid_path)

    try:
        with daemon.DaemonContext(pidfile=pid_ctx) as ctx:
            try:
                run()

            except Exception as e:
                syslog.syslog(syslog.LOG_ERR, e)

    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, e)
