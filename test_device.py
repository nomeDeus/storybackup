import subprocess
import json
import codecs

from collections import OrderedDict

class devices_info():
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
    
    def show(self):
        return '''
device: %s
model name: %s
CPU: %s
density: %s
size: %s
board specifications: %s
release: %s
API level: %s
status: %s''' % (self.name,self.model_name,self.CPU,self.density,self.size,self.board_spec,self.release,self.API_level,self.status)

dev_info = []

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

    info = devices_info(name, model_name, CPU, density, size, board_spec, release, API_level, status)
    dev_info.append(info)

for i in xrange(len(dev_info)):
    print dev_info[i].show()
