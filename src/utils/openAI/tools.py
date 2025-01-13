
tool_by_type = {
}


def convert_api_to_tool(api):
    """Chuyển đổi một API thành định dạng tool của OpenAI Assistant."""

    tool = {
        "type": "function",
        "function": {
            "name": api["name"],
            "description": api["description"],
            "parameters": {
                "type": "object",
                "properties": {},
                "required": api.get("parameters", {}).get("required", []),
            },
        },
    }

    def convert_param(param_info):
        prop = {}
        prop["type"] = param_info["type_"].lower()
        prop["description"] = param_info["description"]
        if param_info['type_'] == 'OBJECT':
            prop["properties"] = {
                k: convert_param(v)
                for k, v in param_info["properties"].items()
            }
            if "required" in param_info:
                prop["required"] = param_info["required"]
        if param_info['type_'] == 'ARRAY':
            prop["items"] = convert_param(param_info["items"])
        if param_info['type_'] == "STRING" and 'enum' in param_info:
            prop["enum"] = param_info["enum"]
        return prop

    # Chuyển đổi các properties của parameters
    if "parameters" in api:
        tool["function"]["parameters"]["properties"] = {
            k: convert_param(v)
            for k, v in api["parameters"]["properties"].items()
        }
    return tool


class Tools:
    def __init__(self, type):
        self.type = type
        self.tools = [convert_api_to_tool(i) for i in [] if i['name'] in tool_by_type.get(type, [])]

    def __call__(self):
        return self.tools
