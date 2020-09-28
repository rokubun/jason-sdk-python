import os

API_URL=os.getenv('JASON_API_URL', 'http://api-argonaut.rokubun.cat/api')

class AuthenticationError(Exception):
    def __init__(self, message):

        super().__init__(message)

class InvalidResponse(Exception):
    def __init__(self, message):

        super().__init__(message)
