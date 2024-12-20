import copy

from src.utils.tools import get_knowledge


def function(function_name, payload, **kwargs):
    """
    This function is used to call the function from the function controller
    """
    from src.config import logger
    function_list = {
        'get_knowledge': get_knowledge,
    }
    payload_dup = copy.deepcopy(payload)
    logger.info(f'Function: {function_name} Payload: {payload_dup}')
    response = function_list[function_name](payload_dup, **kwargs)
    logger.info(f'Response: {response}')
    return response
