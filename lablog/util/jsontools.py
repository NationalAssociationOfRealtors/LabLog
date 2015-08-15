import json
import datetime
import time
from bson.objectid import ObjectId
from humongolus.field import DocumentId, DynamicDocument
from humongolus import Lazy
from flask import Response

class ElasticSearchEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime): return obj.strftime('%Y-%m-%dT%H:%M:%S')
        if isinstance(obj, ObjectId): return str(obj)
        if isinstance(obj, Exception): return str(obj)
        if isinstance(obj, DocumentId): return obj()
        if isinstance(obj, DynamicDocument): return obj()
        try: return obj.json()
        except Exception as e: pass

class JavascriptEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            try:
                return (time.mktime(obj.timetuple())+(obj.microsecond/1000000.0))*1000
            except:
                pass
        if isinstance(obj, ObjectId): return str(obj)
        if not isinstance(obj, (DocumentId, DynamicDocument, Lazy)):
            try:
                return obj.json()
            except:
                return str(obj)


def jsonify(*args, **kwargs):
    status_code = kwargs.pop('status_code', 200)
    res = json.dumps(args, cls=JavascriptEncoder) if len(args) else json.dumps(kwargs, cls=JavascriptEncoder)
    return Response(res, mimetype='application/json', status=status_code)
