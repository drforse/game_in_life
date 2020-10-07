class ActionsStorage:
    def __init__(self):
        self._data = {}
        return

    def update(self, chat_id, user_id, data):
        chat = self._data.get(chat_id)
        if not chat:
            self._data[chat_id] = {}
            chat = self._data.get(chat_id)
        user = chat.get(user_id)
        if not user:
            self._data[chat_id][user_id] = data
            return
        self._data[chat_id][user_id].update(data)

    def get(self, chat_id, user_id, key):
        chat = self._data.get(chat_id)
        if not chat:
            return
        user = chat.get(user_id)
        if not user:
            return
        return user.get(key)
