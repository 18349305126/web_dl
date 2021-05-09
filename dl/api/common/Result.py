from django.http import JsonResponse
import json


class Result():
    """响应体处理、格式化"""
    @staticmethod
    def response(code: int, msg: str, data=None):
        return JsonResponse({'code': code, 'msg': msg, 'data': data})

    @staticmethod
    def parse_request_params(request):
        if request.content_type == 'application/json':
            return json.loads(request.body.decode('utf-8'))
        raise Exception('Request body should be in type of JSON')

    @staticmethod
    def response_success(code: int = 200, msg: str = 'success', data=None):
        return JsonResponse({'code': code, 'msg': msg, 'data': data})

    @staticmethod
    def response_invalid(code: int = 400,
                         msg: str = 'invalid parameters',
                         data=None):
        return JsonResponse({'code': code, 'msg': msg, 'data': data})

    @staticmethod
    def response_fail(code: int = 500, msg: str = 'failed', data=None):
        return JsonResponse({'code': code, 'msg': msg, 'data': data})
