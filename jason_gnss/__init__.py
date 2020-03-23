
API_URL='http://api-argonaut.rokubun.cat/api'
API_KEY_ENV_NAME='JASON_API_KEY'
SECRET_TOKEN_ENV_NAME='JASON_SECRET_TOKEN'



class AuthenticationError(Exception):
    def __init__(self, message):

        super().__init__(message)

class InvalidResponse(Exception):
    def __init__(self, message):

        super().__init__(message)
