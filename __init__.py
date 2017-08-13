#!/usr/bin/env python
import subprocess
import sys
import os
import re
import math
import string
import threading
import json
import codecs

from subprocess import check_output, CalledProcessError
from flask import Flask, Response, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from time import localtime, strftime
from collections import OrderedDict

host='127.0.0.1'

app = Flask(__name__)

# Global variable to uploads `testing_projects` json file
UPLOAD_TESTING_PROJECT = 'uploads_project_json'
# Global variable to test_result `testing_result`
TESTING_RESULT_PROJECT = 'testing_result'
# Global variable to uploads `testing_projects` apk file
UPLOAD_FOLDER = 'uploads'
APK_FILE_FOLDER = 'apk_file'
APK_TEST_FILE_FOLDER = 'apk_test_file'
ALLOWED_EXTENSIONS = set(['apk','json'])

# Global variable to uploads `testing_projects` json file
app.config['UPLOAD_TESTING_PROJECT'] = UPLOAD_TESTING_PROJECT
# Global variable to test_result `testing_result`
app.config['TESTING_RESULT_PROJECT'] = TESTING_RESULT_PROJECT
# Global variable to uploads `testing_projects` apk file
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['APK_FILE_FOLDER'] = APK_FILE_FOLDER
app.config['APK_TEST_FILE_FOLDER'] = APK_TEST_FILE_FOLDER

DATA_FORMAT = 'data_format.json'
DEVICES_INFORNATION = 'devices.json'

app.config['DATA_FORMAT'] = DATA_FORMAT
app.config['DEVICES_INFORNATION'] = DEVICES_INFORNATION



def split_lines(s):
    """Splits lines in a way that works even on Windows and old devices.
        Windows will see \r\n instead of \n, old devices do the same, old devices
        on Windows will see \r\r\n.
        """
    # rstrip is used here to workaround a difference between splineslines and
    # re.split:
    # >>> 'foo\n'.splitlines()
    # ['foo']
    # >>> re.split(r'\n', 'foo\n')
    # ['foo', '']
    return re.split(r'[\r\n]+', s.rstrip())

def read_JSON(path_filename):
    with open(path_filename) as data_file:
        data = json.load(data_file)
    return data

def write_JSON(path_filename, str_status):
    with codecs.open('devices.json', 'w', 'utf-8') as f:
        f.write(str_status)

def check_dir_exists(path_dir):
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

def save_upload_files(request_file, path, filename):
    request_file.save(os.path.join(path, filename))


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    out = split_lines(subprocess.check_output(['adb', 'devices']))
    
    devices = []
    devices.append("<table>")
    devices.append("<tr>")
    
    # Devices Serialno
    devices.append("<td>")
    devices.append("serialno")
    devices.append("</td>")
    
    # Devices Model Name
    devices.append("<td>")
    devices.append("model name")
    devices.append("</td>")
    
    # Devices CPU
    devices.append("<td>")
    devices.append("cpu")
    devices.append("</td>")
    
    # Devices Density
    devices.append("<td>")
    devices.append("density")
    devices.append("</td>")
    
    # Devices Size
    devices.append("<td>")
    devices.append("size")
    devices.append("</td>")
    
    # Devices Board Specifications
    devices.append("<td>")
    devices.append("Board Specifications")
    devices.append("</td>")
    
    # Devices release
    devices.append("<td>")
    devices.append("release")
    devices.append("</td>")
    
    # Devices API Level
    devices.append("<td>")
    devices.append("API Level")
    devices.append("</td>")
    
    devices.append("</tr>")
    for line in out[1:]:
        devices.append("<tr>")
        if not line.strip():
            continue
        if 'offline' in line:
            continue
        
        if '* daemon not running. starting it now at tcp:5037 *' in line or 'daemon started successfully' in line:
            continue
        else:
            # Devices Serialno
            devices.append("<td>")
            info = line.split('\t')
            devices.append(info[0])
            devices.append("</td>")
            
            # Devices Model Name
            devices.append("<td>")
            cmd_adb_get_devices_model = ['adb']
            cmd_adb_get_devices_model.extend(['-s' , info[0]])
            cmd_adb_get_devices_model.extend(['shell' , 'getprop ro.product.model'])
            cmd_adb_get_devices_model = subprocess.check_output(cmd_adb_get_devices_model)
            devices.append(cmd_adb_get_devices_model)
            devices.append("</td>")
            
            # Devices CPU
            devices.append("<td>")
            cmd_adb_get_devices_cpu = ['adb']
            cmd_adb_get_devices_cpu.extend(['-s' , info[0]])
            cmd_adb_get_devices_cpu.extend(['shell' , 'getprop ro.product.cpu.abi'])
            cmd_adb_get_devices_cpu = subprocess.check_output(cmd_adb_get_devices_cpu)
            devices.append(cmd_adb_get_devices_cpu)
            devices.append("</td>")
            
            # Devices Density
            devices.append("<td>")
            cmd_adb_get_devices_lcd_density = ['adb']
            cmd_adb_get_devices_lcd_density.extend(['-s' , info[0]])
            cmd_adb_get_devices_lcd_density.extend(['shell' , 'getprop qemu.sf.lcd_density'])
            cmd_adb_get_devices_lcd_density = subprocess.check_output(cmd_adb_get_devices_lcd_density)
            
            try:
                # if `getprop qemu.sf.lcd_density` is not None can be try it
                x = float(cmd_adb_get_devices_lcd_density)
            except ValueError:
                cmd_adb_get_devices_lcd_density = ['adb']
                cmd_adb_get_devices_lcd_density.extend(['-s' , info[0]])
                cmd_adb_get_devices_lcd_density.extend(['shell' , 'getprop ro.sf.lcd_density'])
                cmd_adb_get_devices_lcd_density = subprocess.check_output(cmd_adb_get_devices_lcd_density)
            
            devices.append(cmd_adb_get_devices_lcd_density)
            devices.append("</td>")
            
            # Devices Size
            devices.append("<td>")
            cmd_adb_get_devices_size = ['adb']
            cmd_adb_get_devices_size.extend(['-s' , info[0]])
            cmd_adb_get_devices_size.extend(['shell' , 'wm size'])
            cmd_adb_get_devices_size = subprocess.check_output(cmd_adb_get_devices_size)
            devices_split = cmd_adb_get_devices_size.split(':')
            devices.append(devices_split[1])
            devices.append("</td>")
            
            # Devices Board Specifications
            devices.append("<td>")
            devices_size = devices_split[1].split('x')
            display_size = math.sqrt(pow(float(devices_size[0])/float(cmd_adb_get_devices_lcd_density),2)+pow(float(devices_size[1])/float(cmd_adb_get_devices_lcd_density),2))
            if display_size >= 7:
                devices.append('Tablet')
            else :
                devices.append('Smartphone')
            devices.append("</td>")
            
            # Devices release
            devices.append("<td>")
            cmd_adb_get_devices_version_release = ['adb']
            cmd_adb_get_devices_version_release.extend(['-s' , info[0]])
            cmd_adb_get_devices_version_release.extend(['shell' , 'getprop ro.build.version.release'])
            cmd_adb_get_devices_version_release = subprocess.check_output(cmd_adb_get_devices_version_release)
            devices.append("Android ")
            devices.append(cmd_adb_get_devices_version_release)
            devices.append("</td>")
            
            # Devices API Level
            devices.append("<td>")
            cmd_adb_get_devices_api_level = ['adb']
            cmd_adb_get_devices_api_level.extend(['-s' , info[0]])
            cmd_adb_get_devices_api_level.extend(['shell' , 'getprop ro.build.version.sdk'])
            cmd_adb_get_devices_api_level = subprocess.check_output(cmd_adb_get_devices_api_level)
            devices.append("API ")
            devices.append(cmd_adb_get_devices_api_level)
            devices.append("</td>")

        devices.append("</tr>")
    
    devices.append("<table>")
    ret = ''.join(devices)
    return Response(ret)

@app.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'apk_file' not in request.files:
            
            return redirect(request.url)
        
        if 'apk_test_file' not in request.files:
            
            return redirect(request.url)
        
        test_project_name = request.form.get('test_project_name')
        apk_file = request.files['apk_file']
        apk_test_file = request.files['apk_test_file']
        print test_project_name
        if (test_project_name is "" or apk_file.filename == '' or apk_test_file.filename == ''):
            return '''
                input 'test_project_name','apk_file','apk_test_file' value.
                '''
        else:
            # Get <UPLOAD_FOLDER> / <test_project_name> path
            test_project_folder = os.path.join(app.config['UPLOAD_FOLDER'], test_project_name)
            
            # Get <UPLOAD_FOLDER> / <test_project_name> / <APK_FILE_FOLDER> path
            test_project_apk_file_folder = os.path.join(test_project_folder, app.config['APK_FILE_FOLDER'])
            
            check_dir_exists(test_project_apk_file_folder)
            
            # Get <UPLOAD_FOLDER> / <test_project_name> / <APK_TEST_FILE_FOLDER> path
            test_project_apk_test_file_folder = os.path.join(test_project_folder, app.config['APK_TEST_FILE_FOLDER'])
            
            check_dir_exists(test_project_apk_test_file_folder)
            
            save_upload_files(apk_file, test_project_apk_file_folder, secure_filename(apk_file.filename))
            
            save_upload_files(apk_test_file, test_project_apk_test_file_folder, secure_filename(apk_test_file.filename))
            
            return '''
                uploads ok!
                '''
    return '''
        input 'test_project_name','apk_file','apk_test_file' value.
        '''

class threadServer(threading.Thread):
    def __init__(self, test_project_name, nowTime, device_name):
        threading.Thread.__init__(self)
        self.pro_name = test_project_name
        self.Time = nowTime
        self.dev_name = device_name
        self.lock = threading.Lock()
    
    def run(self):
        #devices_infomation = read_JSON(app.config['DEVICES_INFORNATION'])
        #devices_infomation[self.dev_name]['status'] = 'busy'
        #str_status = json.dumps(devices_infomation)
        #write_JSON(app.config['DEVICES_INFORNATION'], str_status)
        self.lock.acquire()
        cmd_get_apk_package_name = ['./testing_project.sh', self.pro_name, self.Time, self.dev_name]
        cmd_testing_output = subprocess.check_output(cmd_get_apk_package_name)
        self.lock.release()

# Uploads Json file to testing project
@app.route('/uploads_testing_project', methods=['GET', 'POST'])
def uploads_testing_project():
    if request.method == 'POST':
        threads = []
        devices_info = []
        count = 0
        # check if the post request has the file part
        if 'testing_project_json' not in request.files:
            return redirect(request.url)
        
        testing_project_json = request.files['testing_project_json']
        
        if testing_project_json.filename == '':
            print testing_project_json.filename
            return '''
                input 'testing_project_json' key and value.
                '''
        if testing_project_json and allowed_file(testing_project_json.filename):
            testing_project_folder = os.path.join(app.config['UPLOAD_TESTING_PROJECT'])
            
            check_dir_exists(testing_project_folder)
            
            save_upload_files(testing_project_json, testing_project_folder, secure_filename(testing_project_json.filename))
            
            # read <testing_project_json> file
            testing_project_json = read_JSON(os.path.join(testing_project_folder, secure_filename(testing_project_json.filename)))
        
            test_project_name = testing_project_json['project']['project_name']
            
            devices_infomation_format = read_JSON(app.config['DATA_FORMAT'])
            
            devices_infomation = read_JSON(app.config['DEVICES_INFORNATION'])
            
            # Get current time
            nowTime = strftime('%Y-%m-%d-%H-%M-%S', localtime())
            
            devices_Through_rules = []
        
            for i in devices_infomation:
                # check devices status in devices
                if devices_infomation[i]['status'] == "offline":
                    continue
                
                check_testing_qualifications = False
                count_testing_qualifications_j = 0
                
                for j in testing_project_json['devices']:
                    for k in xrange(len(testing_project_json['devices'][j])):
                        if testing_project_json['devices'][j][k] == "" or devices_infomation[i][devices_infomation_format[j]['name']] == testing_project_json['devices'][j][k]:
                            count_testing_qualifications_j += 1
                            break

                if count_testing_qualifications_j == len(testing_project_json['devices']):
                    check_testing_qualifications = True
                    devices_Through_rules.append(i)
            
            if len(devices_Through_rules) > 0:
                
                for devices_serialno in devices_Through_rules:
                    check_dir_exists(os.path.join(app.config['TESTING_RESULT_PROJECT'], test_project_name, nowTime, devices_serialno))
                    t = threadServer(test_project_name, nowTime, devices_serialno)
                    t.start()
                    threads.append(t)
                    count += 1

            if count == 0:
                return "Not devices run projects complete."
            #elif count == len(devices_infomation):
                #return "All projects complete."
            else:
                return "{0} tested. {1} left.".format(count, len(devices_infomation) - count)

    return '''
        input 'testing_project_json' key and value.
        '''

@app.route('/testing_project', methods=['GET', 'POST'])
def testing_project():
    if request.method == 'POST':
        threads = []
        devices = []
        #catch serial number
        out = split_lines(subprocess.check_output(['adb', 'devices']))
        for line in out[1:]:
            if '* daemon not running. starting it now at tcp:5037 *' in line or 'daemon started successfully' in line:
                continue
            else:
                info = line.split('\t')
                devices.append(info[0])
        
        #catch project name
        print "Getting test project name."
        test_project_name = request.form.get('test_project_name')
        if not test_project_name == 'null':
            print "Test project name: {0}".format(test_project_name)
        else:
            print "Can't get test project name."
            return "Error. Can't get test project name."
        #catch device amount
        print "Getting test device amount."
        test_device_amount = request.form.get('test_device_amount')
        if not test_project_name == 'null':
            print "Test device amount: {0}".format(test_device_amount)
        else:
            print "Can't get test device amount."
            return "Error. Can't get test device amount."
        
        count = 0
        isCompleteAll = False
        device_amount = int(test_device_amount, 10)
        
        if device_amount == 0:
            return "Error: test_device_amout = 0"
        
        #get current time
        print "Getting time."
        nowTime = strftime('%Y-%m-%d-%H-%M-%S', localtime())
        
        print "Current time: " + nowTime
        
        #processins multi-threading
        for i in xrange(device_amount):
            print "{0} processing...".format(devices[count])
            #to create and start the thread then append it to threads
            t = threadServer(test_project_name, nowTime, devices[count])
            t.start()
            threads.append(t)
            count += 1
            if count == device_amount:
                isCompleteAll = True
                break
    
        if isCompleteAll:
            return "All projects complete."
        else:
            return "{0} tested. {1} left.".format(count, device_amount)
    
    return '''
        Please re-enter the command
        '''

@app.route('/get_devices_info')
def get_devices_info():
    out = split_lines(subprocess.check_output(['adb', 'devices']))
    
    count = 1
    devices = []
    
    # read data.json file to get `devices_info` data format
    with codecs.open('data_format.json') as data_file:
        devices_infomation_data = json.load(data_file)

    devices.append('{')
    for line in out[1:]:
        
        if not line.strip():
            continue
        
        if '* daemon not running. starting it now at tcp:5037 *' in line or 'daemon started successfully' in line:
            count += 1
            continue

        else:
            # Devices Serialno
            info = line.split('\t')
            devices.append('"')
            devices.append(info[0])
            devices.append('"')
            devices.append(':')

            device_json_data_count = 0
            devices.append('{')
            
            for key in devices_infomation_data['devices_info']:
                devices.append('"')
                devices.append(devices_infomation_data[key]['name'])
                devices.append('"')
                devices.append(':')
                if 'offline' in line:
                    
                    if key == "serial_number":
                        
                        # Devices Serialno
                        devices.append('"')
                        devices.append(info[0])
                        devices.append('"')
                    
                    elif key == "status":
                        info = line.split('\t')
                        devices.append('"')
                        devices.append(info[1])
                        devices.append('"')
                    else :
                        devices.append('"')
                        devices.append('"')
                        device_json_data_count += 1
                    
                    if device_json_data_count < len(devices_infomation_data['devices_info']):
                        devices.append(',')
                    continue
                
                if key == "serial_number":
                    
                    # Devices Serialno
                    devices.append('"')
                    devices.append(info[0])
                    devices.append('"')
        
                elif key == "display":
                
                    # Devices Density
                    cmd_adb_get_devices_lcd_density = ['adb']
                    cmd_adb_get_devices_lcd_density.extend(['-s' , info[0]])
                    cmd_adb_get_devices_lcd_density.extend(devices_infomation_data[key]['command1'])
                    cmd_adb_get_devices_lcd_density = subprocess.check_output(cmd_adb_get_devices_lcd_density).strip('\r\n')
                    try:
                        x = float(cmd_adb_get_devices_lcd_density)
                    except ValueError:
                        cmd_adb_get_devices_lcd_density = ['adb']
                        cmd_adb_get_devices_lcd_density.extend(['-s' , info[0]])
                        cmd_adb_get_devices_lcd_density.extend(devices_infomation_data[key]['command2'])
                        cmd_adb_get_devices_lcd_density = subprocess.check_output(cmd_adb_get_devices_lcd_density).strip('\r\n')
                    devices.append('"')
                    devices.append(cmd_adb_get_devices_lcd_density)
                    devices.append('"')

                elif key == "size":
                    cmd_adb_get_devices_size = ['adb']
                    cmd_adb_get_devices_size.extend(['-s' , info[0]])
                    cmd_adb_get_devices_size.extend(devices_infomation_data[key]['command'])
                    cmd_adb_get_devices_size = subprocess.check_output(cmd_adb_get_devices_size).strip('\r\n')
                    devices_split = cmd_adb_get_devices_size.split(': ')
                    devices.append('"')
                    devices.append(devices_split[1])
                    devices.append('"')
                
                elif key == "deviceType":
                    
                    devices_size = devices_split[1].split('x')
                    display_size = math.sqrt(pow(float(devices_size[0])/float(cmd_adb_get_devices_lcd_density),2)+pow(float(devices_size[1])/float(cmd_adb_get_devices_lcd_density),2))
                    devices.append('"')
                    if display_size >= 7:
                        devices.append('Tablet')
                    else :
                        devices.append('Smartphone')
                    devices.append('"')
        
                elif key == "status":
                
                    devices.append('"')
                    devices.append(info[1])
                    devices.append('"')
                
                else:
                    cmd_adb_get_devices_model = ['adb']
                    cmd_adb_get_devices_model.extend(['-s' , info[0]])
                    cmd_adb_get_devices_model.extend(devices_infomation_data[key]['command'])
                    cmd_adb_get_devices_model = subprocess.check_output(cmd_adb_get_devices_model).strip('\r\n')
                    devices.append('"')
                    devices.append(cmd_adb_get_devices_model)
                    devices.append('"')
                device_json_data_count += 1
                
                if device_json_data_count < len(devices_infomation_data['devices_info']):
                    devices.append(',')

            devices.append('}')
            count += 1
            if count < len(out):
                devices.append(',')

    devices.append('}')
    ret = ''.join(devices)
    print type(ret)
    
    with codecs.open('devices.json', 'w', 'utf-8') as f:
        f.write(ret)

    return Response(ret)

if __name__ == "__main__":
    app.debug = True
    app.run(host)
