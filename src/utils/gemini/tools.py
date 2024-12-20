tool_by_type = {
    'RAG': ['get_knowledge'],
}


class Tools:
    def __init__(self, type):
        from src.config import TOOLS
        self.type = type
        self.tools = [i for i in TOOLS if i['name'] in tool_by_type.get(type, [])]

    def __call__(self):
        return self.tools
