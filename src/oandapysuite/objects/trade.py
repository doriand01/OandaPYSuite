

class Account:

    def __init__(self, details: dict):
        for key, value in details.items():
            setattr(self, key, value)
        print(f'Loaded account with id {self.id}')

    def __repr__(self):
        return f'Account {self.id}'

class Trade:

    def __init__(self, details: dict):
        for key, value in details.items():
            setattr(self, key, value)

    def __repr__(self):
        return f'Trade {self.id}'