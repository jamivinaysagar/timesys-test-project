#!/usr/bin/python

import paramiko
import ConfigParser
from os import path

###############
class Config():
        obj = {}
        def __init__(self, file_path):
                if not path.exists(file_path):
                        print "File path %s does not exist" %(file_path)
                cfg = ConfigParser.RawConfigParser()
                cfg.read(file_path)
                self.obj['board']      = dict(cfg.items('Board'))
                self.obj['testserver'] = dict(cfg.items('TestServer'))
                self.obj['tests']      = dict(cfg.items('Tests'))

        def board_info(self):
                return self.obj['board']

        def server_info(self):
                return self.obj['testserver']

        def test_info(self):
                return self.obj['tests']

''' 
# Example of parsed content from config.cfg 

{'TestServer': [('paramiko_log', '/tmp/paramiko_log.txt'),
  ('local_log_dir_path', '/tmp/logs/')],
 'Tests': [('test_list',
   "[('CPU_FREQUENCY', ' 0'),\n('GPIO_TOGGLE' , ' -v 1'),\n('LED_TOGGLE',' -c 10 -a'),\n('ADC', '')\n]")],
 'board': [('name', 'BBB'),
  ('host', '192.168.2.3'),
  ('port', '22'),
  ('user', 'root'),
  ('password', 'root'),
  ('default_path_prefix', '/root/test/timesys-test-project'),
  ('board_log_dir_path', '/tmp/logs/')]}
'''
