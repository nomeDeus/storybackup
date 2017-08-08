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

@app.route("/")
def home():
    out = split_lines(subprocess.check_output(['adb', 'devices']))
    
    devices_info = []
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
    
    # Devices status
    devices.append("<td>")
    devices.append("status")
    devices.append("</td>")
    
    devices.append("</tr>")
    
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

    for i in xrange(len(devices_info)):
        devices.append("<tr>")
        
        devices.append("<td>")
        devices.append(devices_info[i].name)
        devices.append("</td>")
        
        devices.append("<td>")
        devices.append(devices_info[i].model_name)
        devices.append("</td>")
        
        devices.append("<td>")
        devices.append(devices_info[i].CPU)
        devices.append("</td>")
        
        devices.append("<td>")
        devices.append(devices_info[i].density)
        devices.append("</td>")
        
        devices.append("<td>")
        devices.append(devices_info[i].size)
        devices.append("</td>")
        
        devices.append("<td>")
        devices.append(devices_info[i].board_spec)
        devices.append("</td>")
        
        devices.append("<td>")
        devices.append(devices_info[i].release)
        devices.append("</td>")
        
        devices.append("<td>")
        devices.append(devices_info[i].API_level)
        devices.append("</td>")
        
        devices.append("<td>")
        devices.append(devices_info[i].status)
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
    devices = []
    mode = "Idle"
    
    with codecs.open('devices.json', 'r', 'utf-8') as f:
        parsed_json = f.read()
    json_text = json.loads(parsed_json)
    json_dict = json.loads(json_text, object_pairs_hook=OrderedDict)

    devices.append("<table>")

    for i in xrange(len(json_dict)):
        devices.append("<tr>")
        for key, value in json_dict[i].items():
            devices.append("<td>")
            devices.append(value)
            devices.append("</td>")
            
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

        devices.append("<td>")
        devices.append(mode)
        devices.append("</td>")
        devices.append("</tr>")

    devices.append("</table>")

    ret = ''.join(devices)
    return Response(ret)

@app.route('/testing_project', methods=['GET', 'POST'])
def testing_project():
    if request.method == 'POST':
        threads = []
        devices_info = []
        count = 0
        
        #catch serial number
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
        
        #get project name
        test_project_name = request.form.get('test_project_name')
        
        #get Android release
        test_device_android_release = request.form.get('test_device_android_release')
        
        #get API Level
        test_device_os = request.form.get('test_device_os')
        
        #get board specification
        test_device_deviceType = request.form.get('test_device_deviceType')
        
        #get density
        test_device_display = request.form.get('test_device_display')
        
        #get CPU
        test_device_arch = request.form.get('test_device_arch')
    
        #get current time
        nowTime = strftime('%Y-%m-%d_%H_%M_%S', localtime())
        
        #processins multi-threading
        for i in xrange(len(devices_info)):
            test_device_condition = [False, False, False, False, False]
            if test_device_android_release is None or test_device_android_release == devices_info[i].release:
                test_device_condition[0] = True
            if test_device_os is None or test_device_os == devices_info[i].API_level:
                test_device_condition[1] = True
            if test_device_deviceType is None or test_device_deviceType == devices_info[i].board_spec:
                test_device_condition[2] = True
            if test_device_display is None or test_device_display == devices_info[i].density:
                test_device_condition[3] = True
            if test_device_arch is None or test_device_arch == devices_info[i].CPU:
                test_device_condition[4] = True
            
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
