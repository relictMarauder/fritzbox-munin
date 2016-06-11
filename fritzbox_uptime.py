#!/usr/bin/env python
"""
  fritzbox_uptime - A munin plugin for Linux to monitor AVM Fritzbox
  Copyright (C) 2015 Christian Stade-Schuldt
  Author: Christian Stade-Schuldt
  Like Munin, this plugin is licensed under the GNU GPL v2 license
  http://www.opensource.org/licenses/GPL-2.0
  Add the following section to your munin-node's plugin configuration:

  [fritzbox_*]
  env.fritzbox_ip [ip address of the fritzbox]
  env.fritzbox_password [fritzbox password]

  This plugin supports the following munin configuration parameters:
  #%# family=auto contrib
  #%# capabilities=autoconf
"""

import os
import re
import sys
import fritzbox_helper as fh

PAGE = '/system/energy.lua'
pattern = re.compile(".*/(.*uptime_\w+?)\".*=.*\"(.*?)\"")


def get_uptime():
    """get the current uptime"""

    server = ${node.metadata['collectd'].get('fritzbox', {}).get('ip', '192.168.168.1')}
    password = ${node.metadata['collectd'].get('fritzbox', {}).get('password', 'fritzbox')}

    sid = fh.get_sid(server, password)
    data = fh.get_page(server, sid, PAGE)
    matches = re.finditer(pattern, data)
    if matches:
        hours = 0.0
        for m in matches:
            if m.group(1) == "uptime_hours":
                hours += int(m.group(2))
            if m.group(1) == "uptime_minutes":
                hours += int(m.group(2)) / 60.0
        uptime = hours / 24
        print "uptime.value %.2f" % uptime


def print_config():
    print "graph_title AVM Fritz!Box Uptime"
    print "graph_args --base 1000 -l 0"
    print 'graph_vlabel uptime in days'
    print "graph_scale no'"
    print "graph_category system"
    print "uptime.label uptime"
    print "uptime.draw AREA"


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'config':
        print_config()
    elif len(sys.argv) == 2 and sys.argv[1] == 'autoconf':
        print 'yes'
    elif len(sys.argv) == 1 or len(sys.argv) == 2 and sys.argv[1] == 'fetch':
        # Some docs say it'll be called with fetch, some say no arg at all
        try:
            get_uptime()
        except:
            sys.exit("Couldn't retrieve fritzbox uptime")
