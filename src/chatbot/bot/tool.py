
from typing import Callable

class Tool:

    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        params: dict
    ):
        """
        Initializes a Tool instance with a name, description, a callable function, and its parameters. 
        Used for OpenAI Function Calling.

        Args:
            name (str): The name of the tool.
            description (str): A brief description of what the tool does.
            func (Callable): The function that the tool will execute.
            params (dict): A dictionary representing the parameters the function requires, 
                            with the parameter names as keys and their details as values.
        """
        self.name = name
        self.description = description
        self.func = func
        self.params = params
        self.tool_dict = {
            'type': 'function',
            'function': {
                'name': name,
                'description': description,
                'parameters': {
                    'type': 'object',
                    'properties': params,
                    'required': list(params.keys())
                }
            }
        }
    
    def __call__(self, **kwargs):
        return self.func(**kwargs)
    

## Example 1
#
# def change_email(old_email, new_email):
#     return f'Email change {old_email} to {new_email} SUCCESS'
#
# change_email_params = {
#     'old_email': {
#         'type': 'string',
#         'description': 'existing email to change'
#     }, 
#     'new_email': {
#         'type': 'string',
#         'description': 'email to change to'
#     }
# }
# 
# change_email_tool = Tool('change_email', 'Updates a user\'s email', change_email, change_email_params)


## Example 2
#
# def change_phone(old_phone, new_phone):
#     return f'Phone change {old_phone} to {new_phone} FAILED - Old phone number does not match with account'
#
# change_phone_params = {
#     'old_phone': {
#         'type': 'string',
#         'description': 'existing phone number to change'
#     }, 
#     'new_phone': {
#         'type': 'string',
#         'description': 'new phone number to change to'
#     }
# }
#
# change_phone_tool = Tool('change_phone', 'Updates a user\'s phone number', change_phone, change_phone_params)