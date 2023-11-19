

class AuthorizedUser:

    def __init__(self, path_to_auth_token):
        self.auth_token = open(path_to_auth_token, 'r').read()

class Subaccount:

    def __init__(self):
        pass