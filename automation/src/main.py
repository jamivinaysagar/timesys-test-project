#!/usr/bin/python

import paramiko
import ConfigParser
from os import path, mkdir
from scp import SCPClient
from shutil import copyfile, move
from config import Config


##################
# Global Variables
##################
SCRIPT_CONF = { 
               'TEST_SCRIPT'  : 'target/common/Test.sh',
               'CPU_FREQUENCY': 'target/cpu/test_cpufreq.sh',
               'GPIO_TOGGLE'  : 'target/gpiolib/gpio-toggle.sh',
               'LED_TOGGLE'   : 'target/leds/led-toggle.sh',
               'ADC'          : 'target/hwmon/test_adc.sh',
               'NOR_FLASH'    : 'target/mtd/test_nor.sh',
               'TEST_ADC'     : 'target/hwmon/test_adc.sh',
               'TEST_NAND'    : 'target/mtd/test_nand.sh',
               'PIPELINE'     : 'target/gst-fsl/test_pipelines.sh',
               'BACKLIGHT'    : 'target/backlight/backlight-test.sh',
               'ALTIMETER'    : 'target/iio/test_altimeter.sh',
               'ACCELEROMETER': 'target/iio/test_accelerometer.sh',
               'WLAN'         : 'target/net/test_wlan.sh',
               'MDIO'         : 'target/net/test_mdio.sh',
               'ETH'          : 'target/net/test_eth.sh',
               'EEPROM'       : 'target/eeprom/test_eeprom.sh',
               'PCIE_ENUM'    : 'target/pcie/test_pcie_enumeration.sh',
               'I2C_READ'     : 'target/i2c/i2c_read_verify.sh',
               'I2C_SEND'     : 'target/i2c/i2c_send_command.sh',
               'LINE_TEST'    : 'target/audio/test_line.sh',
               'SPEAKER'      : 'target/audio/test_speaker.sh',
               'MIC_TEST'     : 'target/audio/test_mic.sh',
               'X11_TEST'     : 'target/fb/test_x11.sh',
               'WESTON'       : 'target/fb/test_weston.sh',
               'FS_TEST'      : 'target/fs/test_fs.sh',
               'USBG_M'       : 'target/usb/test_usbg_m_storage.sh',
               'USB_TEST'     : 'target/usb/testusb.sh',
               'USBH_M'       : 'target/usb/test_usbh_m_storage.sh',
               'USBG_M_S'     : 'target/usb/setup_usbg_m_storage.sh',
}

cfg = Config('config.cfg')
ser_info = cfg.server_info()
board_info = cfg.board_info()
test_info = cfg.test_info()

############
# Functions
############

'''
   function copies files between 2 machines (one is existing machine and 2nd is remote
                                             machine)
   args: local_file_path = location of file path on local machine
         dest_path       = location of file path on remote machine
         host            = remote machine IP address
         port            = remote machine ssh port no (default 22)
         user, password  = access credentials of user
         mode            = PUT  (copy file from local machine to remote machine)
                           GET  (copy file from remote machine to local machine) 
'''
def copy_file(local_file_path, dest_path, host, port, user, password, mode = 'PUT'):
        transport = None
        if not path.exists(local_file_path):
                if mode is 'GET':
                        mkdir(local_file_path)
                else:
		        print "Local file path doesnt exist %s" %(local_file_path) 
	
        paramiko.util.log_to_file(ser_info['paramiko_log'])
        try:
               transport = paramiko.Transport((host, port))
               transport.connect(username=user, password=password)
               transport.get_exception()
               scp = SCPClient(transport)
        except:
               print "FAILED: Error while connecting to host %s:%s and copy file" %(host, port)
               return 0
        if mode is 'PUT':
                scp.put(local_file_path, dest_path)
        else:
                scp.get(dest_path, recursive=True)
                
        scp.close()
        return 1

'''
   function start and execute test program on remote machine 
   args: command         = command to start test program on Remote machine 
         host            = remote machine IP address
         port            = remote machine ssh port no (default 22)
         user, password  = access credentials of user
'''
def execute_cmd(command, host, port, user, password):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
                ssh.connect(hostname=host, port=port, username=user, password=password)
        except:
                print "FAILED: SSH connection is not establishd, Please ssh connectivity manually"
                return ""
        (stdin, stdout, stderr) = ssh.exec_command(command)
	out = stdout.readlines()
        if len(out):
                return out
        else:
                return stderr.readlines()
        ssh.close()

'''
   function join 2 path 
   args: prefix          = initial path of directory
         command         = test name which need to be executed
'''
def prepare_path(prefix, command):
        return path.join(prefix, SCRIPT_CONF[command])


'''
   function this function parses test list from config.cfg file and writes a automated.conf & interactive.conf 
                           to be copied to remote machine 
'''
def update_conf():
        fa = open("automated.conf", 'w')
        fi = open("interactive.conf", 'w')
        fa.write('#run_test "Test Name" "Test Command" "Test Parameters"\n')
        fi.write('#run_test "Test Name" "Test Command" "Test Parameters" "Pre-test Prompt" "Post-test Prompt"\n')

        if not (test_info.has_key('test_list') and len(test_info['test_list'])):
                print "FAILED: Please define set of Tests in config.cfg file which is required to execute"
                return 0

        for (test, args) in eval(test_info['test_list']):
                cmd = prepare_path(board_info['default_path_prefix'], test)      
                fa.write('run_test "%s" %s "%s"\n' %(test, cmd, args)) 

        #for name, test, dev in int_tests:
        #        cmd = prepare_path(board_info['default_path_prefix'], test)      
        #        fi.write('run_test "%s" %s "%s"\n' %(test, cmd, cmd_args(test, dev))) 
        fa.close()
        fi.close()
        return 1

'''
   function parses result logs and copies complete logs of execution of test 
                           from remote machine to local machine
   args: results         = execution log of Test program
         host            = remote machine IP address
         port            = remote machine ssh port no (default 22)
         user, password  = access credentials of user
'''
def parse_results(result, host, port, user, password):
        test_result = {}
        if len(result) > 2:
                res = str(result[2]).rstrip()
                
        if res:
                log_path = path.join(board_info['board_log_dir_path'], res)
                copy_file(ser_info['local_log_dir_path'], log_path, host, port, user, password, mode="GET")
                move(res, ser_info['local_log_dir_path'])

        for i in range(14, len(result)):
                if result[i] and str(result[i]).split(':') and  len(str(result[i]).split(':')) > 1:
                        if str(result[i]).split(':')[1].find('SUCCESS') > -1:
                                test_result[str(result[i]).split(':')[0].strip()] = 'SUCCESS'
                        else:
                                test_result[str(result[i]).split(':')[0].strip()] = 'FAILED'
        print test_result        

'''
   function executes test on remote machine
'''
def execute_tests():
        host = board_info['host']
        port = int(board_info['port'])
        user = board_info['user']
        password = board_info['password']

        #copy automated and interactive conf on destination host
        test = 'TEST_SCRIPT'
        if not copy_file("automated.conf", board_info['default_path_prefix'], host, port, user, password):
                return 0
        #copy_file("interactive.conf", board_info['default_path_prefix'], host, port, user, password)

        cmd = prepare_path(board_info['default_path_prefix'], test)
        cmd = "cd " + board_info['default_path_prefix'] + ";" + cmd
        parse_results(execute_cmd(cmd, host, port, user, password), host, port, user, password )
