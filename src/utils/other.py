import datetime
import re

from src.utils.tools import function


def check_key_in_list_object(key_compare, list):
    for item in list:
        if key_compare in item:
            return True
    return False


def parse_res(parts):
    result = []
    for part in parts:
        if type(part) == str:
            result.append(part)
        else:
            result.append(type(part).to_dict(part))
    return result


def call_function(function_name, args, **kwargs):
    return function(function_name, args, **kwargs)


def history_reformat_function(history):
    result = []
    for item in history:
        if item['role'] == 'user':
            for part in item['parts']:
                if isinstance(part, str):
                    result.append({
                        'role': 'user',
                        'content': part
                    })
                else:
                    result.append({
                        'role': 'user',
                        'content': f'<function_response> {type(part).to_dict(part)} </function_response>'
                    })
        else:
            for part in item['parts']:
                if isinstance(part, str):
                    result.append({
                        'role': 'assistant',
                        'content': part
                    })
                    item['parts'].remove(part)
            if len(item['parts']) > 0:
                function_call = [{
                    'name': i['function_call']['name'],
                    'arguments': i['function_call']['args']
                } for i in parse_res(item['parts']) if 'function_call' in i]
                result.append({
                    'role': 'assistant',
                    'content': f'<function_call> {function_call} </function_call>'
                })
    return result


def generate_function_call_prompt(functions_metadata):
    return f"""You are a helpful assistant with access to the following functions: \n {str(functions_metadata)}\n\nTo use these functions respond with:\n<function_call> [{{ "name": "function_name1", "arguments": {{ "arg_1": "value_1", "arg_1": "value_1", ... }} }},
{{ "name": "function_name2", "arguments": {{ "arg_2": "value_2", "arg_2": "value_2", ... }} }}] </function_call>
    ] </function_call>\n\nEdge cases you must handle:\n - If there are no functions that match the user request, you will respond politely that you cannot help."""


def objectid_to_guid(id):
    hex_str = str(id)
    a = hex_str[6:8] + hex_str[4:6] + hex_str[2:4] + hex_str[0:2]
    b = hex_str[10:12] + hex_str[8:10]
    c = hex_str[14:16] + hex_str[12:14]
    d = hex_str[16:32]
    hex_str = a + b + c + d
    uuid_str = f'{hex_str[0:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}'
    return uuid_str


def guid_to_objectid(guid):
    guid = guid.replace('-', '')
    a = guid[0:8]
    b = guid[8:12]
    c = guid[12:16]
    d = guid[16:32]
    hex_str = a[6:8] + a[4:6] + a[2:4] + a[0:2] + b[2:4] + b[0:2] + c[2:4] + c[0:2] + d
    return bytes.fromhex(hex_str)


def covert_datetime_to_week_number(date: str) -> int:
    """
    Convert datetime to week number
    :param date:  datetime string format "2024-12-28T14:58:00.000+00:00"
    :return:  week number of year
    """
    date = date.split('T')[0]
    date = date.split('-')
    date = list(map(int, date))
    date = datetime.datetime(*date)
    week_number = date.isocalendar()[1]
    return week_number


def covert_range_datetime_to_week_number(start_date: str, end_date: str) -> list[int]:
    """
    Convert datetime to week number
    :param start_date:  datetime string format "2024-12-28T14:58:00.000+00:00"
    :param end_date:  datetime string format "2024-12-28T14:58:00.000+00:00"
    :return:  week number of year
    """
    start_date = start_date.split('T')[0]
    start_date = start_date.split('-')
    start_date = list(map(int, start_date))
    start_date = datetime.datetime(*start_date)
    end_date = end_date.split('T')[0]
    end_date = end_date.split('-')
    end_date = list(map(int, end_date))
    end_date = datetime.datetime(*end_date)
    start_week_number = start_date.isocalendar()[1]
    end_week_number = end_date.isocalendar()[1]
    if start_week_number > end_week_number:
        week_number = [i for i in range(start_week_number, 52 + 1)] + [i for i in range(1, end_week_number + 1)]
    else:
        week_number = [i for i in range(start_week_number, end_week_number + 1)]
    return week_number


def format_message(message: str = None) -> str:
    if message is None:
        return ""
    message = re.sub(r'^\s*(#{1,6})\s+(.*?)$', lambda m: f'<h{len(m.group(1))}>{m.group(2)}</h{len(m.group(1))}>',
                     message, flags=re.MULTILINE)
    # Break line
    message = re.sub(r'(?:\r\n|\r|\n)', '<br>', message)
    # Bold
    message = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', message)
    # Italic
    message = re.sub(r'\*(.*?)\*', r'<em>\1</em>', message)
    # Link
    message = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', message)
    # Code
    message = re.sub(r'`(.*?)`', r'<code>\1</code>', message)
    # List (flatten list items)
    message = re.sub(r'\n\* (.*?)(?=\n|$)', r'\1', message)
    message = re.sub(r'<li>(.*?)<\/li>', r'\1', message)

    return message


def decode_jwt_without_secret(token):
    from src.config import logger
    try:
        # Split the token into header, payload, and signature
        header, payload, signature = token.split('.')

        # Decode the payload (which is base64url encoded)
        import base64
        decoded_payload = base64.urlsafe_b64decode(payload + '=' * (4 - len(payload) % 4))

        # Parse the JSON payload
        import json
        payload_data = json.loads(decoded_payload)

        return payload_data
    except Exception as e:
        logger.error(f'[tripgo-hotel-api] Error decoding JWT token: {e}')
        return None
