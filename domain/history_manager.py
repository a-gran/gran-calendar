class HistoryManager:
    def __init__(self, limit):
        self.limit = limit
        self.undo_stack = []
        self.redo_stack = []

    def remember(self, undo_action, redo_action=None):
        self.undo_stack.append((undo_action, redo_action))
        self.redo_stack.clear()
        self.trim_undo_stack()

    def pop_undo(self):
        if not self.undo_stack:
            return None
        return self.undo_stack.pop()

    def pop_redo(self):
        if not self.redo_stack:
            return None
        return self.redo_stack.pop()

    def remember_redo(self, undo_action, redo_action):
        self.redo_stack.append((undo_action, redo_action))
        self.trim_redo_stack()

    def remember_undo(self, undo_action, redo_action):
        self.undo_stack.append((undo_action, redo_action))
        self.trim_undo_stack()

    def trim_undo_stack(self):
        if len(self.undo_stack) > self.limit:
            self.undo_stack.pop(0)

    def trim_redo_stack(self):
        if len(self.redo_stack) > self.limit:
            self.redo_stack.pop(0)
