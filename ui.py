from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsView, QGraphicsScene, \
    QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtGui import QPen, QFont
from PyQt5.QtCore import Qt, QRectF
from gedcom_handler import GedcomHandler
import os


class GenealogyApp(QMainWindow):
    def __init__(self, tree):
        super().__init__()
        self.tree = tree
        self.gedcom_handler = GedcomHandler(self.tree)
        self.init_ui()
        self.load_styles()

    def init_ui(self):
        # Установка заголовка окна
        self.setWindowTitle("Генеалогическое древо")
        self.setGeometry(100, 100, 1200, 800)

        # Основной контейнер
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Панель управления
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите имя")
        control_layout.addWidget(self.name_input)

        self.parent_input = QLineEdit()
        self.parent_input.setPlaceholderText("ID родителя (необязательно)")
        control_layout.addWidget(self.parent_input)

        add_button = QPushButton("Добавить человека")
        add_button.clicked.connect(self.add_person)
        control_layout.addWidget(add_button)

        remove_button = QPushButton("Удалить человека")
        remove_button.clicked.connect(self.remove_person)
        control_layout.addWidget(remove_button)

        import_button = QPushButton("Импортировать GEDCOM")
        import_button.clicked.connect(self.import_gedcom)
        control_layout.addWidget(import_button)

        export_button = QPushButton("Экспортировать GEDCOM")
        export_button.clicked.connect(self.export_gedcom)
        control_layout.addWidget(export_button)

        control_layout.addStretch()
        main_layout.addWidget(control_panel, 1)

        # Графическое представление дерева
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        main_layout.addWidget(self.view, 4)

        self.update_tree_view()

    def load_styles(self):
        # Загрузка стилей из файла styles.css
        if os.path.exists("styles.css"):
            with open("styles.css", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def add_person(self):
        # Добавление человека в дерево
        name = self.name_input.text()
        parent_id = self.parent_input.text()
        if name:
            self.tree.add_person(name, parent_id if parent_id else None)
            self.update_tree_view()
            self.name_input.clear()
            self.parent_input.clear()
        else:
            QMessageBox.warning(self, "Ошибка ввода", "Имя не может быть пустым")

    def remove_person(self):
        # Удаление человека из дерева
        person_id = self.parent_input.text()
        if person_id and person_id in self.tree.people:
            self.tree.remove_person(person_id)
            self.update_tree_view()
        else:
            QMessageBox.warning(self, "Ошибка ввода", "Неверный ID человека")

    def update_tree_view(self):
        # Обновление графического представления дерева
        try:
            self.scene.clear()
            if not self.tree.people:
                return

            positions = {}
            node_size = 100
            spacing_x = 150
            spacing_y = 100

            def assign_positions(person_id, x=0, y=0, level=0):
                if person_id not in self.tree.people:
                    return
                person = self.tree.people[person_id]
                positions[person_id] = (x, y + level * spacing_y)
                children = person.get("children", [])
                num_children = len(children)
                for i, child_id in enumerate(children):
                    child_x = x + (i - num_children / 2) * spacing_x
                    assign_positions(child_id, child_x, y, level + 1)

            # Поиск корневого узла
            root_id = next((pid for pid, p in self.tree.people.items() if not p.get("parents")), None)
            if root_id:
                assign_positions(root_id)

            # Отрисовка узлов и связей
            for pid, (x, y) in positions.items():
                person = self.tree.people[pid]
                rect = self.scene.addRect(x, y, node_size, 50, QPen(Qt.black), Qt.lightGray)
                text = self.scene.addText(f"{person['name']}\nID: {pid}")
                text.setFont(QFont("Arial", 10))
                text.setPos(x + 10, y + 10)

                for child_id in person.get("children", []):
                    if child_id in positions:
                        cx, cy = positions[child_id]
                        self.scene.addLine(x + node_size / 2, y + 50, cx + node_size / 2, cy, QPen(Qt.black))

            # Оптимизация отображения
            if positions:
                self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self.scene.setSceneRect(self.scene.itemsBoundingRect())
        except Exception as e:
            QMessageBox.critical(self, "Ошибка отображения", f"Не удалось обновить дерево: {str(e)}")

    def import_gedcom(self):
        # Импорт GEDCOM-файла
        file_name, _ = QFileDialog.getOpenFileName(self, "Импортировать GEDCOM", "", "GEDCOM Files (*.ged)")
        if file_name:
            try:
                self.gedcom_handler.import_gedcom(file_name)
                self.update_tree_view()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка импорта", f"Не удалось импортировать GEDCOM: {str(e)}")

    def export_gedcom(self):
        # Экспорт в GEDCOM-файл
        file_name, _ = QFileDialog.getSaveFileName(self, "Экспортировать GEDCOM", "", "GEDCOM Files (*.ged)")
        if file_name:
            try:
                self.gedcom_handler.export_gedcom(file_name)
                QMessageBox.information(self, "Успех", "GEDCOM-файл успешно экспортирован")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка экспорта", f"Не удалось экспортировать GEDCOM: {str(e)}")