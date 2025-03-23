from PySide6.QtWidgets import QTextEdit, QListWidget, QListWidgetItem, QApplication, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeyEvent, QTextCursor
import sys
import re

class SmartTextEdit(QTextEdit):
    def __init__(self, suggestions=None):
        super().__init__()
        self.setPlaceholderText("Digite aqui...")

        self.suggestions = suggestions or {}

        self.popup = QListWidget()
        self.popup.setWindowFlags(Qt.ToolTip)
        self.popup.setFocusPolicy(Qt.StrongFocus)
        self.popup.setMouseTracking(True)
        self.popup.setFocusProxy(self)
        self.popup.itemClicked.connect(self.insert_completion)
        self.popup.hide()

        self.current_base = None
        self.partial_prefix = ""
        self.just_inserted = False
        self.waiting_dot_completion = False

    def adjust_height_by_lines(self, line_count: int):
        """Ajusta a altura do QTextEdit baseado no número de linhas visíveis desejadas."""
        font_metrics = self.fontMetrics()
        line_spacing = font_metrics.lineSpacing()
        padding = 12  # margem interna extra para evitar corte
        total_height = (line_spacing * line_count) + padding
        self.setFixedHeight(total_height)

    def keyPressEvent(self, event: QKeyEvent):
        handled_keys = (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Down, Qt.Key_Up, Qt.Key_Escape, Qt.Key_Tab)
        if self.popup.isVisible() and event.key() in handled_keys:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab):
                current_item = self.popup.currentItem()
                if current_item:
                    self.insert_completion(current_item)
                return
            elif event.key() == Qt.Key_Down:
                self.popup.setCurrentRow((self.popup.currentRow() + 1) % self.popup.count())
                return
            elif event.key() == Qt.Key_Up:
                self.popup.setCurrentRow((self.popup.currentRow() - 1 + self.popup.count()) % self.popup.count())
                return
            elif event.key() == Qt.Key_Escape:
                self.popup.hide()
                return

        if event.key() == Qt.Key_Period and self.just_inserted:
            self.waiting_dot_completion = True

        if event.key() == Qt.Key_Tab:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
            if cursor.selectedText() in ('', ' ') or self.just_inserted:
                self.current_base = None
                self.popup.hide()
                self.trigger_root_suggestions()
                self.just_inserted = False
                return

        super().keyPressEvent(event)
        QTimer.singleShot(0, self.trigger_inline_completion)

    def get_current_word(self, cursor):
        block_text = cursor.block().text()
        pos_in_block = cursor.position() - cursor.block().position()
        left = re.findall(r"[\w.]+", block_text[:pos_in_block][::-1])
        right = re.findall(r"[\w.]+", block_text[pos_in_block:])
        left_part = left[0][::-1] if left else ""
        right_part = right[0] if right else ""
        return left_part + right_part

    def trigger_inline_completion(self):
        if self.waiting_dot_completion:
            self.waiting_dot_completion = False
            self.just_inserted = False
        elif self.just_inserted:
            self.just_inserted = False
            return

        cursor = self.textCursor()
        cursor_word = self.get_current_word(cursor)
        current_word = cursor_word.strip()

        if not current_word:
            self.popup.hide()
            return

        parts = current_word.split(".")
        node = self.suggestions
        entries = []
        valid = True

        for i, part in enumerate(parts[:-1]):  # Navega até o penúltimo nível
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                valid = False
                break

        if valid and isinstance(node, dict):
            last_part = parts[-1]
            self.current_base = ".".join(parts[:-1]) if len(parts) > 1 else None
            self.partial_prefix = current_word
            entries = [k for k in node.keys() if k.lower().startswith(last_part.lower())]

        if entries:
            self.show_popup(entries)
        else:
            self.popup.hide()

    def trigger_root_suggestions(self):
        if isinstance(self.suggestions, dict):
            entries = list(self.suggestions.keys())
            self.show_popup(entries)

    def show_popup(self, entries):
        self.popup.clear()
        for entry in sorted(entries):
            self.popup.addItem(QListWidgetItem(entry))

        self.popup.setCurrentRow(0)
        cursor_rect = self.cursorRect()
        popup_pos = self.mapToGlobal(cursor_rect.bottomLeft())
        self.popup.move(popup_pos)
        self.popup.resize(300, min(150, self.popup.sizeHintForRow(0) * len(entries) + 2))
        self.popup.show()

    def insert_completion(self, item):
        try:
            completion = item.text()
            cursor = self.textCursor()

            word = self.get_current_word(cursor)
            if self.current_base:
                full_prefix = f"{self.current_base}."
                if word.startswith(full_prefix):
                    for _ in range(len(word)):
                        cursor.deletePreviousChar()
                    cursor.insertText(f"{full_prefix}{completion}")
                else:
                    cursor.insertText(f"{full_prefix}{completion}")
            else:
                cursor.select(QTextCursor.WordUnderCursor)
                cursor.insertText(completion)

            self.setTextCursor(cursor)
            self.popup.hide()
            self.current_base = None
            self.partial_prefix = ""
            self.just_inserted = True
        except Exception as e:
            print("Erro ao inserir autocompletar:", e)

# --- Execução ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)

    # Sugestões com múltiplos níveis
    suggestions = {
        "Python": {
            "Django": {
                "Admin": {},
                "ORM": {},
                "Templates": {}
            },
            "Flask": {},
            "FastAPI": {}
        },
        "Java": {
            "Spring": {
                "Security": {},
                "Boot": {}
            },
            "Hibernate": {}
        },
        "JavaScript": {
            "React": {
                "Hooks": {},
                "Components": {}
            },
            "Vue": {},
            "Node.js": {}
        }
    }

    editor = SmartTextEdit(suggestions=suggestions)
    editor.adjust_height_by_lines(1)
    layout.addWidget(editor)

    window.resize(600, 160)
    window.setWindowTitle("Autocomplete com Subníveis Ilimitados")
    window.show()

    sys.exit(app.exec())