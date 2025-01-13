import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from src.utils.openAI.history import History
from src.utils.openAI.tools import Tools
from src.utils.tools.main import function

load_dotenv()


class OpenAIClient:
    def __init__(self, type='', instruction='', **args):
        self.memory_enabled = args.get('memory_enabled', True)
        self.base_url = args.get('base_url', None)
        self.api_key = args.get('api_key', os.getenv('GPT_API_KEY'))
        self.type = type
        self.model = args.get('model', 'gpt-4o-mini')
        self.history = History()
        self.tools = Tools(type)
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.instructions = instruction + '\n\n'
        self.history.add_part('system', self.instructions)
        self.args = args

    def encode(self, texts: list[str], **kwargs):
        res = self.client.embeddings.create(model='text-embedding-3-small', input=texts, dimensions=384)
        return [d.embedding for d in res.data]

    def generate_content(self, messages=None, functions=None, tool_config=None):
        rs = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
            tools=functions if len(functions) > 0 else None,
            # functions=functions if len(functions) > 0 else None,
        )
        return rs.choices[0].message.to_dict()

    def generate_content_retry(self, data, tools=None, tool_config=None, retry=3):
        try:
            if tools is None:
                return self.generate_content(messages=data, tool_config=tool_config)
            if tool_config is None:
                return self.generate_content(messages=data, functions=tools)
            return self.generate_content(messages=data, functions=tools, tool_config=tool_config)
        except Exception as e:
            if retry == 0:
                self.history.clear()
                return None
            max_time = max(3, retry)
            time.sleep(2 * (max_time - retry + 1))
            return self.generate_content_retry(data, tools, tool_config, retry - 1)

    def format_response(self, response):
        functions = response.get('tool_calls', [])
        is_has_function = len(functions) > 0
        return response, functions, is_has_function, response['content']

    def call_function(self, function_name, args, **kwargs):
        return function(function_name, args, **kwargs)

    def excuted_function(self, part, **kwargs):
        res = self.call_function(part['function']['name'],
                                 json.loads(part['function']['arguments']), **kwargs)
        self.history.add_function_response(
            part,
            res
        )
        return res

    def __call__(self, text=None, **kwargs):
        return_function = kwargs.get('return_function', None)
        if text is not None:
            self.history.add_user_response(text)
        response = self.generate_content_retry(
            self.history(),
            tools=self.tools()
        )
        response_base, functions, has_function_call, response = self.format_response(response)
        if self.memory_enabled:
            self.history.add_system_response(response_base)
        else:
            self.history.remove_last()
        while has_function_call:
            for i in range(len(functions)):
                if return_function == functions[i]['function']['name']:
                    return functions[i]['function']['arguments']
                self.excuted_function(
                    functions[i],
                    type=self.type,
                    **self.args,
                    **kwargs)
            response = self.generate_content_retry(
                self.history(),
                tools=self.tools()
            )
            response_base, functions, has_function_call, response = self.format_response(response)
            if self.memory_enabled:
                self.history.add_system_response(response_base)
            else:
                self.history.remove_last()
        return response
