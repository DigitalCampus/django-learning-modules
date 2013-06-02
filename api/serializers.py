# learning_modules/api/serializers.py
from django.core.serializers import json
from django.utils import simplejson
from tastypie.serializers import Serializer

class PrettyJSONSerializer(Serializer):
    json_indent = 4

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        return simplejson.dumps(data, cls=json.DjangoJSONEncoder,
                sort_keys=True, ensure_ascii=False, indent=self.json_indent)
     
class ModuleJSONSerializer(Serializer):

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
    
        if 'objects' in data:
            data['modules'] = data['objects']
            del data['objects']

        return simplejson.dumps(data, cls=json.DjangoJSONEncoder,
               sort_keys=True)

class TagJSONSerializer(Serializer):
    json_indent = 4
    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
    
        if 'objects' in data:
            data['tags'] = data['objects']
            del data['objects']
            for t in data['tags']:
                del t['modules'] 
        
        if 'modules' in data:
            new_modules = []
            for m in data['modules']:
                new_modules.append(m['module'])
            del data['modules']
            data['modules'] = new_modules
        return simplejson.dumps(data, cls=json.DjangoJSONEncoder,
               sort_keys=True, ensure_ascii=False)