class User():
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash


    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._username
