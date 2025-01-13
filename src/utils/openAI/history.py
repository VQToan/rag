import uuid


class History:
    def __init__(self):
        self.data = []

    def add_part(self, role, content):
        self.data.append({
            'messageId': str(uuid.uuid4()),
            "role": 'assistant' if role == 'model' else role,
            "content": content
        })

    def add_content(self, role, content):
        self.data.append({
            'messageId': str(uuid.uuid4()),
            'role': role,
            'content': content
        })

    def add_system_response(self, response):
        self.data.append(response)

    def add_user_response(self, response):
        self.data.append({
            'messageId': str(uuid.uuid4()),
            'role': 'user',
            'content': response
        })

    def add_function_response(self, tool, response):
        self.data.append({
            'messageId': str(uuid.uuid4()),
            "tool_call_id": tool['id'],
            'role': 'tool',
            'name': tool['function']['name'],
            'content': str(response)
        })

    def clear(self, num=None):
        if num is None:
            self.data = []
        else:
            self.data = self.data[-num:]

    def remove_last(self):
        if len(self.data) > 0:
            self.data.pop()

    def __call__(self, *args, **kwargs):
        return self.data

    def __set__(self, instance, value):
        self.data = value
