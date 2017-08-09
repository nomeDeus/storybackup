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

UPLOAD_FOLDER = 'uploads'
APK_FILE_FOLDER = 'apk_file'
APK_TEST_FILE_FOLDER = 'apk_test_file'
ALLOWED_EXTENSIONS = set(['apk','json'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['APK_FILE_FOLDER'] = APK_FILE_FOLDER
app.config['APK_TEST_FILE_FOLDER'] = APK_TEST_FILE_FOLDER

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
    devices_info = []
    devices_info.append("<table>")
    devices_info.append("<tr>")
    
    # Devices Serialno
    devices_info.append("<td>")
    devices_info.append("serialno")
    devices_info.append("</td>")
    
    # Devices Model Name
    devices_info.append("<td>")
    devices_info.append("model name")
    devices_info.append("</td>")
    
    # Devices CPU
    devices_info.append("<td>")
    devices_info.append("cpu")
    devices_info.append("</td>")
    
    # Devices Density
    devices_info.append("<td>")
    devices_info.append("density")
    devices_info.append("</td>")
    
    # Devices Size
    devices_info.append("<td>")
    devices_info.append("size")
    devices_info.append("</td>")
    
    # Devices Board Specifications
    devices_info.append("<td>")
    devices_info.append("Board Specifications")
    devices_info.append("</td>")
    
    # Devices release
    devices_info.append("<td>")
    devices_info.append("release")
    devices_info.append("</td>")
    
    # Devices API Level
    devices_info.append("<td>")
    devices_info.append("API Level")
    devices_info.append("</td>")
    
    # Devices status
    devices_info.append("<td>")
    devices_info.append("status")
    devices_info.append("</td>")
    
    devices_info.append("</tr>")
    
    with codecs.open('devices.json', 'r', 'utf-8') as f:
        parsed_json = f.read()
    
    json_text = json.loads(parsed_json)
    json_dict = json.loads(json_text, object_pairs_hook=OrderedDict)

    for i in xrange(len(json_dict)):
        devices_info.append("<tr>")
        
        for key, value in json_dict[i].items():
            devices_info.append("<td>")
            devices_info.append(value)
            devices_info.append("</td>")

        devices_info.append("</tr>")
    
    devices_info.append("<table>")
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
            cmd_get_apk_package_name = ['./apk_package.sh', test_project_name, apk_file_filename, apk_test_file_filename]
            cmd_testing_output = subprocess.check_output(cmd_get_apk_package_name)
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

@app.route('/check')
def check_status():
    devices_info = []
    mode = "Idle"
    
    with codecs.open('devices.json', 'r', 'utf-8') as f:
        parsed_json = f.read()
    json_text = json.loads(parsed_json)
    json_dict = json.loads(json_text, object_pairs_hook=OrderedDict)

    devices_info.append("<table>")

    for i in xrange(len(json_dict)):
        devices_info.append("<tr>")
        for key, value in json_dict[i].items():
            devices_info.append("<td>")
            devices_info.append(value)
            devices_info.append("</td>")
            
            if key == "devices":
                check = ['./test.sh', value]
                output = subprocess.check_output(check)
                f = open('tmp', 'r')
                status = f.read()
                str = "com.example.android"
                if not status.find(str):
                    mode = "Busy"
                else:
                    mode = "Idle"

        devices_info.append("<td>")
        devices_info.append(mode)
        devices_info.append("</td>")
        devices_info.append("</tr>")

    devices_info.append("</table>")

    ret = ''.join(devices)
    return Response(ret)

@app.route('/testing_project', methods=['GET', 'POST'])
def testing_project():
    if request.method == 'POST':
        threads = []
        test_info = []
        devices_match = []
        num = 0
        
        #get devices information
        with codecs.open('devices.json', 'r', 'utf-8') as f:
            devices_parsed_json = f.read()
        devices_json_text = json.loads(devices_parsed_json)
        devices_json_dict = json.loads(devices_json_text, object_pairs_hook=OrderedDict)
        f.close()
        
        for i in xrange(len(devices_json_dict)):
            devices_match.append(True)
        
        #get test json
        testing_project = request.files['testing_project']
        
        #get test information
        with codecs.open(testing_project.filename, 'r', 'utf-8') as f:
            test_parsed_json = f.read()
        test_json_dict = json.loads(test_parsed_json, object_pairs_hook=OrderedDict)
        f.close()
        
        #get current time
        nowTime = strftime('%Y-%m-%d_%H_%M_%S', localtime())
        
        #get test project name
        test_project_name = test_json_dict['project']['project_name']
        
        #check conditions
        for key, value in test_json_dict['devices'].items():
            if test_json_dict['devices'][key] == '':
                continue
            else:
                for i in xrange(len(devices_json_dict)):
                    if not devices_match[i]:
                        continue

                    for dev_key in devices_json_dict[i].keys():
                        if not test_json_dict['devices'][key] in devices_json_dict[i][dev_key]:
                            devices_match[i] = False
                        else:
                            devices_match[i] = True
                            break;
                            
        for count in xrange(len(devices_json_dict)):
            #processins multi-threading
            if devices_match[count]:
                t = threadServer(test_project_name, nowTime, devices_json_dict[count]['devices'])
                t.start()
                threads.append(t)
                num += 1

        if num == len(devices_json_dict):
            return "All projects complete."
        else:
            return "{0} tested. {1} left.".format(num, len(devices_json_dict) - num)

    return '''
        Please re-enter the command
        '''

@app.route('/get_devices_info')
def get_devices_status():
    out = split_lines(subprocess.check_output(['adb', 'devices']))

    count = 0
    devices_info = []

    devices_info.append('[')
    for line in out[1:]:
        if not line.strip():
            continue
        if 'offline' in line:
            continue
        
        if '* daemon not running. starting it now at tcp:5037 *' in line or 'daemon started successfully' in line:
            continue
        else:
            devices_info.append('{')
            
            # Devices Serialno
            info = line.split('\t')
            devices_info.append('"devices":')
            devices_info.append('"')
            devices_info.append(info[0])
            devices_info.append('"')
            
            devices_info.append(',')
            
            # Devices Model Name
            devices_info.append('"model_name":')
            cmd_adb_get_devices_model = ['adb']
            cmd_adb_get_devices_model.extend(['-s' , info[0]])
            cmd_adb_get_devices_model.extend(['shell' , 'getprop ro.product.model'])
            cmd_adb_get_devices_model = subprocess.check_output(cmd_adb_get_devices_model).strip('\r\n')
            devices_info.append('"')
            devices_info.append(cmd_adb_get_devices_model)
            devices_info.append('"')
            
            devices_info.append(',')
            
            # Devices CPU
            devices_info.append('"CPU":')
            cmd_adb_get_devices_cpu = ['adb']
            cmd_adb_get_devices_cpu.extend(['-s' , info[0]])
            cmd_adb_get_devices_cpu.extend(['shell' , 'getprop ro.product.cpu.abi'])
            cmd_adb_get_devices_cpu = subprocess.check_output(cmd_adb_get_devices_cpu).strip('\r\n')
            devices_info.append('"')
            devices_info.append(cmd_adb_get_devices_cpu)
            devices_info.append('"')
            
            devices_info.append(',')
            
            # Devices Density
            devices_info.append('"density":')
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
            
            devices_info.append('"')
            devices_info.append(cmd_adb_get_devices_lcd_density)
            devices_info.append('"')
            
            devices_info.append(',')
            
            # Devices Size
            devices_info.append('"size":')
            cmd_adb_get_devices_size = ['adb']
            cmd_adb_get_devices_size.extend(['-s' , info[0]])
            cmd_adb_get_devices_size.extend(['shell' , 'wm size'])
            cmd_adb_get_devices_size = subprocess.check_output(cmd_adb_get_devices_size).strip('\r\n')
            devices_split = cmd_adb_get_devices_size.split(':')
            devices_info.append('"')
            devices_info.append(devices_split[1])
            devices_info.append('"')
            
            devices_info.append(',')
            
            # Devices Board Specifications
            devices_info.append('"board_spec":')
            devices_size = devices_split[1].split('x')
            display_size = math.sqrt(pow(float(devices_size[0])/float(cmd_adb_get_devices_lcd_density),2)+pow(float(devices_size[1])/float(cmd_adb_get_devices_lcd_density),2))
            devices_info.append('"')
            if display_size >= 7:
                devices_info.append('Tablet')
            else :
                devices_info.append('SmartPhone')
            devices_info.append('"')
            
            devices_info.append(',')
            
            # Devices release
            devices_info.append('"release":')
            cmd_adb_get_devices_version_release = ['adb']
            cmd_adb_get_devices_version_release.extend(['-s' , info[0]])
            cmd_adb_get_devices_version_release.extend(['shell' , 'getprop ro.build.version.release'])
            cmd_adb_get_devices_version_release = subprocess.check_output(cmd_adb_get_devices_version_release).strip('\r\n')
            devices_info.append('"Android ')
            devices_info.append(cmd_adb_get_devices_version_release)
            devices_info.append('"')
            
            devices_info.append(',')

            # Devices API Level
            devices_info.append('"API_level":')
            cmd_adb_get_devices_api_level = ['adb']
            cmd_adb_get_devices_api_level.extend(['-s' , info[0]])
            cmd_adb_get_devices_api_level.extend(['shell' , 'getprop ro.build.version.sdk'])
            cmd_adb_get_devices_api_level = subprocess.check_output(cmd_adb_get_devices_api_level).strip('\r\n')
            devices_info.append('"API ')
            devices_info.append(cmd_adb_get_devices_api_level)
            devices_info.append('"')

            devices_info.append(',')
                
            devices_info.append('"status":')
            devices_info.append('"')
            devices_info.append(info[1])
            devices_info.append('"')
                
            devices_info.append('}')
            if not count == (len(out) - 2):
                devices_info.append(',')
            count += 1

    devices_info.append(']')
    ret = ''.join(devices_info)
    parsed_json = json.dumps(ret)
    with codecs.open('devices.json', 'w', 'utf-8') as f:
        f.write(parsed_json)

    json_dict = json.loads(parsed_json)

    return Response(json_dict)

if __name__ == "__main__":
    app.debug = True
    app.run(host)
