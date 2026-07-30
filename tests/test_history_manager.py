from domain.history_manager import HistoryManager


def test_history_manager_remembers_undo_and_clears_redo():
    manager = HistoryManager(limit=10)
    manager.remember(lambda: None, lambda: None)
    manager.redo_stack = [("old", "redo")]

    manager.remember(lambda: None)

    assert len(manager.undo_stack) == 2
    assert manager.redo_stack == []


def test_history_manager_limits_undo_stack():
    manager = HistoryManager(limit=2)

    manager.remember(lambda: None)
    manager.remember(lambda: None)
    manager.remember(lambda: None)

    assert len(manager.undo_stack) == 2


def test_history_manager_moves_actions_between_stacks():
    manager = HistoryManager(limit=10)

    def undo_action():
        return None

    def redo_action():
        return None

    manager.remember(undo_action, redo_action)

    action = manager.pop_undo()
    manager.remember_redo(*action)
    restored_action = manager.pop_redo()
    manager.remember_undo(*restored_action)

    assert manager.undo_stack == [(undo_action, redo_action)]
    assert manager.redo_stack == []
