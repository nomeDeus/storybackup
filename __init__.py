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
ALLOWED_EXTENSIONS_APK = set(['apk'])
ALLOWED_EXTENSIONS_JSON = set(['json'])

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
        data = json.load(data_file, object_pairs_hook=OrderedDict)
    return data

def write_JSON(path_filename, data_json):
    with open(path_filename, 'w') as f:
        f.write(json.dumps(data_json))

# Check directory exists
# if is not exists, then can create the <path_dir>
def check_dir_exists(path_dir):
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

def check_project_exists(path_dir):
    if os.path.exists(path_dir):
        return False
    return True

def check_file_is_file(path_filename):
    if os.path.isfile(path_filename):
        return False
    return True

# Check uploads file format in <ALLOWED_EXTENSIONS_APK>
def allowed_file_apk(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_APK

# Check uploads file format in <ALLOWED_EXTENSIONS_JSON>
def allowed_file_json(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_JSON

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
        
        if test_project_name is "" or apk_file.filename == '' or apk_test_file.filename == '':
            return '''
                input 'test_project_name','apk_file','apk_test_file' value.
                '''
        if apk_file and allowed_file_apk(apk_file.filename) and apk_test_file and allowed_file_apk(apk_test_file.filename):
            
            # Get <UPLOAD_FOLDER> / <test_project_name> / <APK_FILE_FOLDER> path
            test_project_apk_file_folder = os.path.join(app.config['UPLOAD_FOLDER'], test_project_name, app.config['APK_FILE_FOLDER'])
            
            check_dir_exists(test_project_apk_file_folder)
            
            # Get <UPLOAD_FOLDER> / <test_project_name> / <APK_TEST_FILE_FOLDER> path
            test_project_apk_test_file_folder = os.path.join(app.config['UPLOAD_FOLDER'], test_project_name, app.config['APK_TEST_FILE_FOLDER'])
            
            check_dir_exists(test_project_apk_test_file_folder)
            
            # Get upload <apk_file> filename
            apk_file_filename = secure_filename(apk_file.filename)
            # Save upload <apk_file> filename
            apk_file.save(os.path.join(test_project_apk_file_folder, apk_file_filename))
            
            # Get upload <apk_test_file> filename
            apk_test_file_filename = secure_filename(apk_test_file.filename)
            # Save upload <apk_test_file> filename
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
        check_devices_infortion(self.dev_name, 'busy')
        self.lock.acquire()
        cmd_get_apk_package_name = ['./testing_project.sh', self.pro_name, self.Time, self.dev_name]
        cmd_testing_output = subprocess.check_output(cmd_get_apk_package_name)
        self.lock.release()
        check_devices_infortion(self.dev_name, 'device')

# Uploads Json file to testing project
@app.route('/uploads_testing_project', methods=['GET', 'POST'])
def uploads_testing_project():
    if request.method == 'POST':
        threads = []
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
        if testing_project_json and allowed_file_json(testing_project_json.filename):

            check_dir_exists(app.config['UPLOAD_TESTING_PROJECT'])

            # Get upload <testing_regulation.json> filename
            testing_project_json_filename = secure_filename(testing_project_json.filename)
            
            # Save and <testing_regulation.json> filename to folder <testing_result>
            testing_project_json.save(os.path.join(app.config['UPLOAD_TESTING_PROJECT'], secure_filename(testing_project_json.filename)))
            
            # read <testing_project_json> file
            testing_project_json = read_JSON(os.path.join(app.config['UPLOAD_TESTING_PROJECT'], secure_filename(testing_project_json.filename)))
        
            test_project_name = testing_project_json['project']['project_name']
            
            if check_project_exists(os.path.join(app.config['UPLOAD_FOLDER'], test_project_name)):
                return '''
                    You input project name not exists.
                    '''
            devices_infomation_format = read_JSON(app.config['DATA_FORMAT'])
            
            if check_file_is_file(app.config['DEVICES_INFORNATION']):
                get_devices_info()
            
            devices_infomation = read_JSON(app.config['DEVICES_INFORNATION'])
            
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
                    devices_Through_rules.append(devices_infomation[i]['serialno'])
            
            # Get current time
            nowTime = strftime('%Y-%m-%d-%H-%M-%S', localtime())
            
            while len(devices_Through_rules) > 0:
                
                for devices_serialno in devices_Through_rules:
                    
                    if devices_infomation[devices_serialno]['status'] == "device":
                        check_dir_exists(os.path.join(app.config['TESTING_RESULT_PROJECT'], test_project_name, nowTime, devices_serialno))
                        project_thread = threadServer(test_project_name, nowTime, devices_serialno)
                        project_thread.start()
                        threads.append(project_thread)
                        devices_Through_rules.remove(devices_serialno)
                        count += 1

            # Wait for all threads to complete
            for t in threads:
                t.join()

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

def get_devices_info():
    command_adb_devices = split_lines(subprocess.check_output(['adb', 'devices']))
    
    count = 1
    array_devices_information = []
    
    # read data.json file to get `devices_info` data format
    with codecs.open('data_format.json') as data_file:
        devices_infomation_data = json.load(data_file)

    array_devices_information.append('{')
    for line in command_adb_devices[1:]:
        
        if not line.strip():
            continue
        
        if '* daemon not running. starting it now at tcp:5037 *' in line or 'daemon started successfully' in line:
            count += 1
            continue

        else:
            device_json_data_count = 0
            
            # Devices Serialno
            info = line.split('\t')
            array_devices_information.append('"')
            array_devices_information.append(info[0])
            array_devices_information.append('"')
            
            array_devices_information.append(':{')
            
            for key in devices_infomation_data['devices_info']:
                array_devices_information.append('"')
                array_devices_information.append(devices_infomation_data[key]['name'])
                array_devices_information.append('"')
                array_devices_information.append(':')
                
                if key == "serial_number":
                    
                    # Devices Serialno
                    array_devices_information.append('"')
                    array_devices_information.append(info[0])
                    array_devices_information.append('"')
                
                elif key == "status" or 'offline' in line :
                    
                    if key == "status":
                        array_devices_information.append('"')
                        array_devices_information.append(info[1])
                        array_devices_information.append('"')
                    else :
                        array_devices_information.append('"')
                        array_devices_information.append('"')
                        array_devices_information += 1
        
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
                    array_devices_information.append('"')
                    array_devices_information.append(cmd_adb_get_devices_lcd_density)
                    array_devices_information.append('"')

                elif key == "size":
                    cmd_adb_get_devices_size = ['adb']
                    cmd_adb_get_devices_size.extend(['-s' , info[0]])
                    cmd_adb_get_devices_size.extend(devices_infomation_data[key]['command'])
                    cmd_adb_get_devices_size = subprocess.check_output(cmd_adb_get_devices_size).strip('\r\n')
                    cmd_adb_get_devices_size_split = cmd_adb_get_devices_size.split(': ')
                    array_devices_information.append('"')
                    array_devices_information.append(cmd_adb_get_devices_size_split[1])
                    array_devices_information.append('"')
                
                elif key == "deviceType":
                    
                    devices_size = cmd_adb_get_devices_size_split[1].split('x')
                    display_size = math.sqrt(pow(float(devices_size[0])/float(cmd_adb_get_devices_lcd_density),2)+pow(float(devices_size[1])/float(cmd_adb_get_devices_lcd_density),2))
                    array_devices_information.append('"')
                    if display_size >= 7:
                        array_devices_information.append('Tablet')
                    else :
                        array_devices_information.append('Smartphone')
                    array_devices_information.append('"')

                else:
                    cmd_adb_get_devices_model = ['adb']
                    cmd_adb_get_devices_model.extend(['-s' , info[0]])
                    cmd_adb_get_devices_model.extend(devices_infomation_data[key]['command'])
                    cmd_adb_get_devices_model = subprocess.check_output(cmd_adb_get_devices_model).strip('\r\n')
                    array_devices_information.append('"')
                    array_devices_information.append(cmd_adb_get_devices_model)
                    array_devices_information.append('"')

                device_json_data_count += 1
                
                if device_json_data_count < len(devices_infomation_data['devices_info']):
                    array_devices_information.append(',')

            array_devices_information.append('}')
            count += 1
            if count < len(command_adb_devices):
                array_devices_information.append(',')

    array_devices_information.append('}')
    Json_devices_information = ''.join(array_devices_information)
    
    with codecs.open(app.config['DEVICES_INFORNATION'], 'w', 'utf-8') as f:
        f.write(Json_devices_information)

    return redirect(url_for('home'))

def change_devices_status(serialno, status):
    
    devices_infomation = read_JSON(app.config['DEVICES_INFORNATION'])
    
    devices_infomation[serialno]['status'] = status

    write_JSON(app.config['DEVICES_INFORNATION'], devices_infomation)

@app.route('/get_status')
def get_status():
    
    informations = []
    
    devices_infomation = read_JSON(app.config['DEVICES_INFORNATION'])
    
    command_adb_devices = split_lines(subprocess.check_output(['adb', 'devices']))

    for line in command_adb_devices[1:]:
        if not line.strip():
            continue
        
        if '* daemon not running. starting it now at tcp:5037 *' in line or 'daemon started successfully' in line:
            continue
        
        else:
            info = line.split('\t')
            informations.append(info[0])
            informations.append('\t')
            informations.append(devices_infomation[info[0]]['status'])
                
    ret = ''.join(informations)
    return Response(ret)

@app.route('/')
def home():
    
    if check_file_is_file(app.config['DEVICES_INFORNATION']):
        get_devices_info()
    
    devices_infomation_format = read_JSON(app.config['DATA_FORMAT'])
    
    devices_infomation = read_JSON(app.config['DEVICES_INFORNATION'])

    response_devices_info = []
    response_devices_info.append("<table>")

    response_devices_info.append("<tr>")
    for data_format in devices_infomation_format['devices_info']:
        response_devices_info.append("<td>")
        response_devices_info.append(data_format)
        response_devices_info.append("</td>")
    response_devices_info.append("<tr>")
    
    for i in devices_infomation:
        print i
        response_devices_info.append("<tr>")
        for j in devices_infomation[i]:
            
            response_devices_info.append("<td>")
            response_devices_info.append(devices_infomation[i][j])
            response_devices_info.append("</td>")
        
        response_devices_info.append("</tr>")

    response_devices_info.append("</table>")

    ret = ''.join(response_devices_info)
    return Response(ret)

if __name__ == "__main__":
    app.debug = True
    app.run(host)
