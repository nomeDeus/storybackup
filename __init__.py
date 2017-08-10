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

host='0.0.0.0'

# Global variable to uploads `testing_projects` json file
UPLOAD_TESTING_PROJECT = 'uploads_project_json'
# Global variable to uploads `testing_projects` apk file
UPLOAD_FOLDER = 'uploads'
APK_FILE_FOLDER = 'apk_file'
APK_TEST_FILE_FOLDER = 'apk_test_file'
ALLOWED_EXTENSIONS = set(['apk','json'])

app = Flask(__name__)

# Global variable to uploads `testing_projects` json file
app.config['UPLOAD_TESTING_PROJECT'] = UPLOAD_TESTING_PROJECT
# Global variable to uploads `testing_projects` apk file
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['APK_FILE_FOLDER'] = APK_FILE_FOLDER
app.config['APK_TEST_FILE_FOLDER'] = APK_TEST_FILE_FOLDER

class dev_info():
    def __init__(self, name, model_name, CPU, density, size, board_spec, release, API_level, status):
        self.name = name
        self.model_name = model_name
        self.CPU = CPU
        self.density = density
        self.size = size
        self.board_spec = board_spec
        self.release = release
        self.API_level = API_level
        self.status = status

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
                devices.append('SmartPhone')
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
            
            test_project_folder = os.path.join(app.config['UPLOAD_FOLDER'], test_project_name)
            
            if not os.path.exists(test_project_folder):
                os.makedirs(test_project_folder)
            
            test_project_apk_file_folder = os.path.join(test_project_folder, app.config['APK_FILE_FOLDER'])
            
            if not os.path.exists(test_project_apk_file_folder):
                os.makedirs(test_project_apk_file_folder)
            
            test_project_apk_test_file_folder = os.path.join(test_project_folder, app.config['APK_TEST_FILE_FOLDER'])
            
            if not os.path.exists(test_project_apk_test_file_folder):
                os.makedirs(test_project_apk_test_file_folder)
            
            print test_project_folder
            print test_project_apk_file_folder
            print test_project_apk_test_file_folder

            apk_file_filename = secure_filename(apk_file.filename)
            apk_file.save(os.path.join(test_project_apk_file_folder, apk_file_filename))
            
            apk_test_file_filename = secure_filename(apk_test_file.filename)
            apk_test_file.save(os.path.join(test_project_apk_test_file_folder, apk_test_file_filename))
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
        self.lock.acquire()
        cmd_get_apk_package_name = ['./testing_project.sh', self.pro_name, self.Time, self.dev_name]
        cmd_testing_output = subprocess.check_output(cmd_get_apk_package_name)
        self.lock.release()

# Uploads Json file to testing project
@app.route('/uploads_testint_project', methods=['GET', 'POST'])
def uploads_testint_project():
    if request.method == 'POST':
        threads = []
        devices_info = []
        count = 0
        # check if the post request has the file part
        if 'testint_project_json' not in request.files:
            
            return redirect(request.url)
        
        testing_project_json = request.files['testint_project_json']
        
        if (testing_project_json == ''):
            return '''
                input 'testint_project_json' key and value.
                '''
        else:
            testing_project_folder = os.path.join(app.config['UPLOAD_TESTING_PROJECT'])
            
            # To determine whether there is `uploads` folder
            if not os.path.exists(testing_project_folder):
                os.makedirs(testing_project_folder)
            
            testing_project_json_filename = secure_filename(testing_project_json.filename)
            
            testing_file_str = os.path.join(testing_project_folder, testing_project_json_filename)
	    print testing_file_str
            testing_project_json.save(testing_file_str)
            
            # read `testing_project_json` file
            with open(os.path.join(testing_project_folder, testing_project_json_filename)) as data_file:
                data = json.load(data_file)
            
            for key in data.keys():
                if key == "project":
                    for k, v in data[key].items():
                        test_project_name = v
                if key == "devices":
                    for k, v in data[key].items():
                        if k == "os":
                            test_device_android_release = v
                        if k == "API Level":
                            test_device_os = v
                        if k == "deviceType":
                            test_device_deviceType = v
                        if k == "display":
                            test_device_display = v
                        if k == "arch":
                            test_device_arch = v

            #get current time
            nowTime = strftime('%Y-%m-%d_%H_%M_%S', localtime())

	    # read all connect devices information
            with codecs.open('devices.json', 'r', 'utf-8') as f:
                parsed_json = f.read()

            json_text = json.loads(parsed_json)
            json_dict = json.loads(json_text, object_pairs_hook=OrderedDict)
            
            for i in xrange(len(json_dict)):
                for key, value in json_dict[i].items():
                    if key == "devices":
                        name = value
                    elif key == "model_name":
                        model_name = value
                    elif key == "CPU":
                        CPU = value
                    elif key == "density":
                        density = value
                    elif key == "size":
                        size = value
                    elif key == "board_spec":
                        board_spec = value
                    elif key == "release":
                        release = value
                    elif key == "API_level":
                        API_level = value
                    elif key == "status":
                        status = value
            
            	info = dev_info(name, model_name, CPU, density, size, board_spec, release, API_level, status)
            	devices_info.append(info)

            # processins multi-threading
            for i in xrange(len(devices_info)):
                test_device_condition = [False, False, False, False, False]
                if test_device_android_release == "" or test_device_android_release == devices_info[i].release:
                    test_device_condition[0] = True
                if test_device_os == "" or test_device_os == devices_info[i].API_level:
                    test_device_condition[1] = True
                if test_device_deviceType == "" or test_device_deviceType == devices_info[i].board_spec:
                    test_device_condition[2] = True
                if test_device_display == "" or test_device_display == devices_info[i].density:
                    test_device_condition[3] = True
                if test_device_arch == "" or test_device_arch == devices_info[i].CPU:
                    test_device_condition[4] = True

                print test_device_condition
            
                #to create and start the thread then append it to threads
                if all(test_device_condition):
                    t = threadServer(test_project_name, nowTime, devices_info[i].name)
                    t.start()
                    threads.append(t)
                    count += 1

            if count == len(devices_info):
                return "All projects complete."
            else:
                return "{0} tested. {1} left.".format(count, len(devices_info) - count)

    return '''
        input 'testint_project_json' key and value.
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
        nowTime = strftime('%Y-%m-%d_%H_%M_%S', localtime())
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
def get_devices_status():
    out = split_lines(subprocess.check_output(['adb', 'devices']))
    
    count = 0
    devices = []
    
    devices.append('[')
    for line in out[1:]:
        if not line.strip():
            continue
        if 'offline' in line:
            continue
        
        if '* daemon not running. starting it now at tcp:5037 *' in line or 'daemon started successfully' in line:
            continue
        else:
            devices.append('{')
            
            # Devices Serialno
            info = line.split('\t')
            devices.append('"devices":')
            devices.append('"')
            devices.append(info[0])
            devices.append('"')
            
            devices.append(',')
            
            # Devices Model Name
            devices.append('"model_name":')
            cmd_adb_get_devices_model = ['adb']
            cmd_adb_get_devices_model.extend(['-s' , info[0]])
            cmd_adb_get_devices_model.extend(['shell' , 'getprop ro.product.model'])
            cmd_adb_get_devices_model = subprocess.check_output(cmd_adb_get_devices_model).strip('\r\n')
            devices.append('"')
            devices.append(cmd_adb_get_devices_model)
            devices.append('"')
            
            devices.append(',')
            
            # Devices CPU
            devices.append('"CPU":')
            cmd_adb_get_devices_cpu = ['adb']
            cmd_adb_get_devices_cpu.extend(['-s' , info[0]])
            cmd_adb_get_devices_cpu.extend(['shell' , 'getprop ro.product.cpu.abi'])
            cmd_adb_get_devices_cpu = subprocess.check_output(cmd_adb_get_devices_cpu).strip('\r\n')
            devices.append('"')
            devices.append(cmd_adb_get_devices_cpu)
            devices.append('"')
            
            devices.append(',')
            
            # Devices Density
            devices.append('"density":')
            cmd_adb_get_devices_lcd_density = ['adb']
            cmd_adb_get_devices_lcd_density.extend(['-s' , info[0]])
            cmd_adb_get_devices_lcd_density.extend(['shell' , 'getprop qemu.sf.lcd_density'])
            cmd_adb_get_devices_lcd_density = subprocess.check_output(cmd_adb_get_devices_lcd_density).strip('\r\n')
            try:
                x = float(cmd_adb_get_devices_lcd_density)
            except ValueError:
                cmd_adb_get_devices_lcd_density = ['adb']
                cmd_adb_get_devices_lcd_density.extend(['-s' , info[0]])
                cmd_adb_get_devices_lcd_density.extend(['shell' , 'getprop ro.sf.lcd_density'])
                cmd_adb_get_devices_lcd_density = subprocess.check_output(cmd_adb_get_devices_lcd_density).strip('\r\n')
            
            devices.append('"')
            devices.append(cmd_adb_get_devices_lcd_density)
            devices.append('"')
            
            devices.append(',')
            
            # Devices Size
            devices.append('"size":')
            cmd_adb_get_devices_size = ['adb']
            cmd_adb_get_devices_size.extend(['-s' , info[0]])
            cmd_adb_get_devices_size.extend(['shell' , 'wm size'])
            cmd_adb_get_devices_size = subprocess.check_output(cmd_adb_get_devices_size).strip('\r\n')
            devices_split = cmd_adb_get_devices_size.split(':')
            devices.append('"')
            devices.append(devices_split[1])
            devices.append('"')
            
            devices.append(',')
            
            # Devices Board Specifications
            devices.append('"board_spec":')
            devices_size = devices_split[1].split('x')
            display_size = math.sqrt(pow(float(devices_size[0])/float(cmd_adb_get_devices_lcd_density),2)+pow(float(devices_size[1])/float(cmd_adb_get_devices_lcd_density),2))
            devices.append('"')
            if display_size >= 7:
                devices.append('Tablet')
            else :
                devices.append('SmartPhone')
            devices.append('"')
            
            devices.append(',')
            
            # Devices release
            devices.append('"release":')
            cmd_adb_get_devices_version_release = ['adb']
            cmd_adb_get_devices_version_release.extend(['-s' , info[0]])
            cmd_adb_get_devices_version_release.extend(['shell' , 'getprop ro.build.version.release'])
            cmd_adb_get_devices_version_release = subprocess.check_output(cmd_adb_get_devices_version_release).strip('\r\n')
            devices.append('"Android ')
            devices.append(cmd_adb_get_devices_version_release)
            devices.append('"')
            
            devices.append(',')
            
            # Devices API Level
            devices.append('"API_level":')
            cmd_adb_get_devices_api_level = ['adb']
            cmd_adb_get_devices_api_level.extend(['-s' , info[0]])
            cmd_adb_get_devices_api_level.extend(['shell' , 'getprop ro.build.version.sdk'])
            cmd_adb_get_devices_api_level = subprocess.check_output(cmd_adb_get_devices_api_level).strip('\r\n')
            devices.append('"API ')
            devices.append(cmd_adb_get_devices_api_level)
            devices.append('"')
            
            devices.append(',')
            
            devices.append('"status":')
            devices.append('"')
            devices.append(info[1])
            devices.append('"')
            
            devices.append('}')
            if not count == (len(out) - 2):
                devices.append(',')
            count += 1

    devices.append(']')
    ret = ''.join(devices)
    parsed_json = json.dumps(ret)
    with codecs.open('devices.json', 'w', 'utf-8') as f:
        f.write(parsed_json)

    json_dict = json.loads(parsed_json)
    
    return Response(json_dict)

if __name__ == "__main__":
    app.debug = True
    app.run(host)
