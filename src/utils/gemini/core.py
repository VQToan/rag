import json
import os
import time

import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from src.utils.gemini.history import History
from src.utils.gemini.tools import Tools
from src.utils.other import parse_res, check_key_in_list_object, call_function

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))


def GeminiEmbedding(text, type='RETRIEVAL_QUERY', ):
    query_emb = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type=type,
        output_dimensionality=768,
    )
    return query_emb['embedding']


class GeminiClient:
    def __init__(self, type=None, instruction='', **args):

        self.generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 10,
            "max_output_tokens": 8192,
        }
        if 'generation_config' in args:
            self.generation_config.update(**args['generation_config'])
        self.memory_enabled = args.get('memory_enabled', True)
        self.type = type
        self.model = args.get('model', 'gemini-1.5-flash')
        self.instructions = instruction
        self.client = genai.GenerativeModel(
            self.model,
            system_instruction=self.instructions if self.instructions else None,
            generation_config=self.generation_config,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
            },
        )
        self.history = History(type)
        self.tools = Tools(type)
        self.args = args

    def format_response(self, response):
        if response is None:
            raise Exception('Error in generate_content_retry')
        parts = parse_res(response.parts)
        has_function_call = check_key_in_list_object('function_call', parts)
        return parts, has_function_call

    def validate_response(self, response):
        formated_response = parse_res(response.parts)
        if response is None:
            raise Exception('Error in generate_content_retry')
        text_compare = str(json.dumps(formated_response, ensure_ascii=False))
        text_compare = text_compare.replace(r'\\n', r'\n')
        text_compare = text_compare.replace(r'\\\n', r'\n')
        if r'\\' in text_compare:
            self.history.add_parts('model', response.parts)
            self.history.add_part('user', 'Response not valid, it should be not has "\\", not is unicode string')
            raise Exception('Please check the response')
        if '```python' in text_compare:
            self.history.add_parts('model', response.parts)
            self.history.add_part('user', 'Response not valid, it should be not has "```python"')
            raise Exception('Please check the response')
        if 'tool_code' in text_compare:
            self.history.add_parts('model', response.parts)
            self.history.add_part('user',
                                  'Please check the tool code in the response,  it should be continue to full function call or separate to more small function call and continue to full function call')
            raise Exception('Please check the tool code in the response, it should be continue to full function call')

    def generate_content_retry(self, data, tools=None, tool_config=None, retry=3):
        from src.config import logger
        try:
            if tools is None and tool_config is not None:
                res = self.client.generate_content(data, tool_config=tool_config)
            elif tool_config is None and tools is not None:
                res = self.client.generate_content(data, tools=tools)
            else:
                res = self.client.generate_content(
                    data,
                    tools=tools,
                    tool_config=tool_config)
            self.validate_response(res)
            return res
        except Exception as e:
            logger.error(f'Error: {e}')
            if retry == 0:
                self.history.clear()
                return None
            max_time = max(3, retry)
            time.sleep(2 * (max_time - retry + 1))
            return self.generate_content_retry(data, tools, tool_config, retry - 1)

    def executed_function(self, part, **kwargs):
        if 'function_call' in part:
            res = call_function(part['function_call']['name'],
                                part['function_call']['args'], **kwargs)
            self.history.add_parts_function_response(part['function_call']['name'], res)

    def __call__(self, text=None, token=None, **kwargs):
        return_function = kwargs.get('return_function', None)
        if text is not None:
            self.history.add_parts('user', text)
        response = self.generate_content_retry(
            self.history(),
            tools=self.tools(),
        )
        parts, has_function_call = self.format_response(response)
        if self.memory_enabled:
            self.history.add_parts('model', response.parts)
        else:
            self.history.remove_last()
        while has_function_call:
            for part in parts:
                if 'function_call' in part:
                    if return_function == part['function_call']['name']:
                        return part
                    self.executed_function(
                        part,
                        token=token,
                        type=self.type,
                        **kwargs,
                        **self.args
                    )
            response = self.generate_content_retry(
                self.history(),
                tools=self.tools(),
            )
            parts, has_function_call = self.format_response(response)
            if self.memory_enabled:
                try:
                    self.history.add_part('model', response.text)
                except:
                    self.history.add_parts('model', response.parts)
            else:
                self.history.remove_last()
        return response.text

    def __del__(self):
        del self.client
        del self.history
        del self.tools
