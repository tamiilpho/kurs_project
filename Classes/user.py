class User:
    def __init__(self, id, telegram_id, username, role, favorites):
        self.id = id
        self.telegram_id = telegram_id
        self.username = username
        self.role = role
        self.favorites = favorites
