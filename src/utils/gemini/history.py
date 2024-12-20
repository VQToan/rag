import json

import google.generativeai.protos as glm

from src.utils.other import parse_res


class History:
    def __init__(self, type):
        self.data = []

    def add_part(self, role, part):
        if (len(self.data) > 0) and (self.data[-1]['role'] == role):
            self.data[-1]['parts'].append(part)
        else:
            self.data.append({
                'role': role,
                'parts': [part]
            })
        return self.data

    def add_parts_function_response(self, name, response):
        self.add_part('user', glm.FunctionResponse(
            name=name,
            response={
                'response': response,
            }
        ))
        return self.data

    def update_input(self, data, request):
        if request is None:
            request = 'Tôi muốn tạo hợp đồng và cập nhật toàn bộ hợp đồng từ tài liệu này'
        self.data[0]['parts'][0] = self.data[0]['parts'][0].replace('[REQUEST]', request)
        self.data[0]['parts'][0] = self.data[0]['parts'][0].replace('[INPUT]', '\n'.join(data))

    def add_parts(self, role, parts):
        if (len(self.data) > 0) and (self.data[-1]['role'] == role):
            self.data[-1]['parts'] += parts
        else:
            self.data.append({
                'role': role,
                'parts': parts
            })
        return self.data

    def reformat_before(self):
        try:
            model_response = self.data[-2]['parts']
            model_response = ['function_call' + i['function_call']['name'] for i in parse_res(model_response)]
            user_response = self.data[-1]['parts']
            user_response = [json.dumps(i, ensure_ascii=False) for i in parse_res(user_response)]
            self.data[-2]['parts'] = model_response
            self.data[-1]['parts'] = user_response
        except:
            pass
        return self.data

    def __call__(self, *args, **kwargs):
        return self.data

    def clear(self, num=None):
        if num is None:
            self.data = []
        else:
            self.data = self.data[-num:]

    def remove_last(self):
        if len(self.data) > 0:
            self.data.pop()

    def edit_last_message(self, message):
        if len(self.data) > 0:
            self.data[-1]['parts'][-1] = message


