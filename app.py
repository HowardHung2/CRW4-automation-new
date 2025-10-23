from flask_restx import Resource
from logger import logger

from payload import (
    api_ns, api, app, api_test,
    queue_list_payload,
    add_chemical_input_payload,
    general_output_payload
)
from tasks import CRW4Mechanization, CRW4Factory, CRW4Algorithm
from util import handle_request_exception


crw4_automation = CRW4Factory.get_crw4_automation()
mechanization = CRW4Mechanization(crw4_automation)
algorithom = CRW4Algorithm(mechanization)

@api.route("/auto")
class Auto(Resource):
    @handle_request_exception
    @api.expect(queue_list_payload)
    @api.marshal_with(general_output_payload)
    def post(self):
        data = api.payload
        cas_list = data.get("cas_list")
        id = data.get("id")
        try:
            result = mechanization.automate(cas_list=cas_list, id=id)
            return {'status': 0, "result": result}
        except Exception as e:
            return {"status": 1, "result": e.args[0], "error": e.__class__.__name__}

@api.route("/daily_append")
class DailyAppend(Resource):
    @handle_request_exception
    @api.expect(queue_list_payload)
    @api.marshal_with(general_output_payload)
    def post(self):
        data = api.payload
        cas_list = data.get("cas_list")
        id = data.get("id")
        try:
            result = algorithom.daily_algrthom()
            return {'status': 0, "result": result}
        except Exception as e:
            return {"status": 1, "result": e.args[0], "error": e.__class__.__name__}
        

@api.route("/check")
class Check(Resource):
    @handle_request_exception
    @api.expect(queue_list_payload)
    @api.marshal_with(general_output_payload)
    def post(self):
        data = api.payload
        cas_list = data.get("cas_list")
        id = data.get("id")
        try:
            result = mechanization.automate_check(cas_list=cas_list, id=id)
            return {'status': 0, "result": result}
        except Exception as e:
            return {"status": 1, "result": e.args[0], "error": e.__class__.__name__}

@api.route("/test")
class Test(Resource):
    @handle_request_exception
    @api.expect()
    @api.marshal_with(general_output_payload)
    def post(self):
        data = api.payload
        cas = data.get("cas")
        try:
            result = mechanization.test(cas=cas)
            return result
        except Exception as e:
            return {"status": 1, "result": e.args[0], "error": e.__class__.__name__}

@api.route("/add")
class Add(Resource):
    @handle_request_exception
    @api.expect(add_chemical_input_payload)
    @api.marshal_with(general_output_payload)
    def post(self):
        data = api.payload
        cas = data.get("cas")
        try:
            result = mechanization.test(cas=cas)
            return result
        except Exception as e:
            return {"status": 1, "result": e.args[0], "error": e.__class__.__name__}

# @api.route("/format")
# class Format(Resource):
#     @handle_request_exception
#     @api.expect(add_chemical_input_payload)
#     @api.marshal_with(general_output_payload)
#     def post(self):
#         # 1. 讀取 JSON 檔案，抽取 success_item 並取出 CAS 號碼列表
#     json_path = r"D:\Systex\CRW4-automation\data\json\test1.json"
#     with open(json_path, 'r', encoding='utf-8') as f:
#         data = json.load(f)
    
#     # success_item 格式預期為 [ {"10141-05-6": "COBALT NITRATE"}, ... ]
#     success_items = data.get("success_item", [])
#     cas_list = []
#     for item in success_items:
#         # 從字典取出 key（CAS 號碼）
#         cas_list.extend(list(item.keys()))
    
#     print(f"從 JSON 中抽取到 {len(cas_list)} 筆 CAS 號碼。")
        



if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=False, use_reloader=False)



