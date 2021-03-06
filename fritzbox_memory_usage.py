#!/usr/bin/env python
"""
  fritzbox_memory_usage - A munin plugin for Linux to monitor AVM Fritzbox
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

PAGE = '/system/ecostat.lua'
pattern = re.compile(".*/(StatRAM.*?)\".*=.*\"(.*?)\"")
USAGE_MAPPING = {'StatRAMCacheUsed': 'cache', 'StatRAMPhysFree': 'free', 'StatRAMStrictlyUsed': 'strict'}


def get_memory_usage():
    """get the current memory usage"""

    server = '${node.metadata['collectd'].get('fritzbox', {}).get('ip', '192.168.168.1')'
    password = '${node.metadata['collectd'].get('fritzbox', {}).get('password', 'fritzbox')}'

    sid = fh.get_sid(server, password)
    data = fh.get_page(server, sid, PAGE)
    matches = re.finditer(pattern, data)
    if matches:
        for m in matches:
            print'%s.value %d' % (USAGE_MAPPING[m.group(1)], int(m.group(2).split(',')[0]))


def print_config():
    print "graph_title AVM Fritz!Box Memory"
    print "graph_vlabel %"
    print "graph_args --base 1000 -r --lower-limit 0 --upper-limit 100"
    print "graph_category system"
    print "graph_order strict cache free"
    print "graph_info This graph shows what the Fritzbox uses memory for."
    print "graph_scale no"
    print "strict.label strict"
    print "strict.type GAUGE"
    print "strict.draw AREA"
    print "cache.label cache"
    print "cache.type GAUGE"
    print "cache.draw STACK"
    print "free.label free"
    print "free.type GAUGE"
    print "free.draw STACK"


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'config':
        print_config()
    elif len(sys.argv) == 2 and sys.argv[1] == 'autoconf':
        print 'yes'
    elif len(sys.argv) == 1 or len(sys.argv) == 2 and sys.argv[1] == 'fetch':
        # Some docs say it'll be called with fetch, some say no arg at all
        try:
            get_memory_usage()
        except:
            sys.exit("Couldn't retrieve fritzbox memory usage")
