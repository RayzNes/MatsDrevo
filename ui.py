from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsView, QGraphicsScene, \
    QLineEdit, QFileDialog, QMessageBox, QDialog, QFormLayout, QLabel, QTabWidget, QTableWidget, QTableWidgetItem, \
    QTextEdit
from PyQt5.QtGui import QPen, QFont, QPixmap, QPainter
from PyQt5.QtCore import Qt, QRectF
from gedcom_handler import GedcomHandler
import os


class PersonDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить человека")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.surname = QLineEdit()
        self.name = QLineEdit()
        self.patronymic = QLineEdit()
        self.birth_date = QLineEdit()
        self.death_date = QLineEdit()
        self.birth_place = QLineEdit()
        self.death_place = QLineEdit()
        self.notes = QLineEdit()
        self.image_path = QLineEdit()
        self.image_path.setReadOnly(True)

        layout.addRow("Фамилия:", self.surname)
        layout.addRow("Имя:", self.name)
        layout.addRow("Отчество:", self.patronymic)
        layout.addRow("Дата рождения:", self.birth_date)
        layout.addRow("Дата смерти:", self.death_date)
        layout.addRow("Место рождения:", self.birth_place)
        layout.addRow("Место смерти:", self.death_place)
        layout.addRow("Заметки:", self.notes)
        layout.addRow("Изображение:", self.image_path)

        choose_image = QPushButton("Выбрать изображение")
        choose_image.clicked.connect(self.choose_image)
        layout.addRow(choose_image)

        buttons = QHBoxLayout()
        ok_button = QPushButton("Добавить")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addRow(buttons)

        self.setLayout(layout)

    def choose_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Выбрать изображение", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_name:
            self.image_path.setText(file_name)

    def get_data(self):
        return {
            "surname": self.surname.text().strip(),
            "name": self.name.text().strip(),
            "patronymic": self.patronymic.text().strip(),
            "birth_date": self.birth_date.text().strip(),
            "death_date": self.death_date.text().strip(),
            "birth_place": self_birth_place.text().strip(),
            "death_place": self.death_place.text().strip(),
            "notes": self.notes.text().strip(),
            "image_path": self.image_path.text().strip()
        }


class GenealogyApp(QMainWindow):
    def __init__(self, tree):
        super().__init__()
        self.tree = tree
        self.gedcom_handler = GedcomHandler(self.tree)
        self.scale_factor = 1.0  # Для зума
        self.init_ui()
        self.load_styles()

    def init_ui(self):
        # Установка заголовка окна
        self.setWindowTitle("MatsDrevo")
        self.setGeometry(100, 100, 1200, 800)

        # Основной контейнер
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Вкладки
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Вкладка "Люди"
        people_widget = QWidget()
        people_layout = QVBoxLayout(people_widget)
        self.people_table = QTableWidget()
        self.people_table.setColumnCount(9)
        self.people_table.setHorizontalHeaderLabels(
            ["ID", "Фамилия", "Имя", "Отчество", "Дата рождения", "Дата смерти", "Место рождения", "Место смерти",
             "Заметки"])
        self.people_table.horizontalHeader().setStretchLastSection(True)
        people_layout.addWidget(self.people_table)
        self.tabs.addTab(people_widget, "Люди")

        # Вкладка "Древо"
        tree_widget = QWidget()
        tree_layout = QHBoxLayout(tree_widget)

        # Панель управления
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)

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

        # Кнопки зума
        zoom_in_button = QPushButton("Увеличить")
        zoom_in_button.clicked.connect(self.zoom_in)
        control_layout.addWidget(zoom_in_button)

        zoom_out_button = QPushButton("Уменьшить")
        zoom_out_button.clicked.connect(self.zoom_out)
        control_layout.addWidget(zoom_out_button)

        control_layout.addStretch()
        tree_layout.addWidget(control_panel, 1)

        # Графическое представление дерева
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        tree_layout.addWidget(self.view, 4)
        self.tabs.addTab(tree_widget, "Древо")

        # Вкладка "О программе"
        about_widget = QWidget()
        about_layout = QVBoxLayout(about_widget)
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setText("""
        <h2>MatsDrevo</h2>
        <p>Версия: 1.0</p>
        <p>Автор: xAI</p>
        <p>Описание: Программа для создания и управления генеалогическими деревьями. Поддерживает добавление до 1500 человек, импорт/экспорт GEDCOM, изображения и расширенные данные о персонах.</p>
        """)
        about_layout.addWidget(about_text)
        self.tabs.addTab(about_widget, "О программе")

        self.update_tree_view()
        self.update_people_table()

    def load_styles(self):
        # Загрузка стилей из файла styles.css
        if os.path.exists("styles.css"):
            with open("styles.css", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def add_person(self):
        # Открытие диалогового окна для добавления человека
        dialog = PersonDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            parent_id = self.parent_input.text().strip()
            self.tree.add_person(data, parent_id if parent_id else None)
            self.update_tree_view()
            self.update_people_table()
            self.parent_input.clear()

    def remove_person(self):
        # Удаление человека из дерева
        person_id = self.parent_input.text()
        if person_id and person_id in self.tree.people:
            self.tree.remove_person(person_id)
            self.update_tree_view()
            self.update_people_table()
        else:
            QMessageBox.warning(self, "Ошибка ввода", "Неверный ID человека")

    def update_people_table(self):
        # Обновление таблицы людей
        self.people_table.setRowCount(len(self.tree.people))
        row = 0
        for pid, person in self.tree.people.items():
            self.people_table.setItem(row, 0, QTableWidgetItem(pid))
            self.people_table.setItem(row, 1, QTableWidgetItem(person["surname"]))
            self.people_table.setItem(row, 2, QTableWidgetItem(person["name"]))
            self.people_table.setItem(row, 3, QTableWidgetItem(person["patronymic"]))
            self.people_table.setItem(row, 4, QTableWidgetItem(person["birth_date"]))
            self.people_table.setItem(row, 5, QTableWidgetItem(person["death_date"]))
            self.people_table.setItem(row, 6, QTableWidgetItem(person["birth_place"]))
            self.people_table.setItem(row, 7, QTableWidgetItem(person["death_place"]))
            self.people_table.setItem(row, 8, QTableWidgetItem(person["notes"]))
            row += 1
        self.people_table.resizeColumnsToContents()

    def update_tree_view(self):
        # Обновление графического представления дерева
        try:
            self.scene.clear()
            if not self.tree.people:
                return

            positions = {}
            node_size = 120
            image_size = 50
            spacing_x = 180
            spacing_y = 120

            def assign_positions(person_id, x=0, y=0, level=0):
                if person_id not in self.tree.people or person_id in positions:
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
                # Отрисовка изображения
                image_path = person.get("image_path", "")
                if image_path and os.path.exists(image_path):
                    pixmap = QPixmap(image_path).scaled(image_size, image_size, Qt.KeepAspectRatio)
                    self.scene.addPixmap(pixmap).setPos(x, y)
                else:
                    self.scene.addRect(x, y, image_size, image_size, QPen(Qt.gray), Qt.lightGray)

                # Отрисовка текста
                text = f"{person['surname']} {person['name']} {person['patronymic']}\nID: {pid}".strip()
                rect = self.scene.addRect(x + image_size + 5, y, node_size, image_size, QPen(Qt.black), Qt.lightGray)
                text_item = self.scene.addText(text)
                text_item.setFont(QFont("Arial", 10))
                text_item.setPos(x + image_size + 10, y + 10)

                # Отрисовка связей
                for child_id in person.get("children", []):
                    if child_id in positions:
                        cx, cy = positions[child_id]
                        self.scene.addLine(x + image_size / 2, y + image_size, cx + image_size / 2, cy, QPen(Qt.black))

            # Оптимизация отображения
            if positions:
                self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
                self.view.setSceneRect(self.scene.itemsBoundingRect())
        except Exception as e:
            QMessageBox.critical(self, "Ошибка отображения", f"Не удалось обновить дерево: {str(e)}")

    def wheelEvent(self, event):
        # Обработка зума колесиком мыши
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        old_pos = self.view.mapToScene(event.pos())
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.scale_factor *= zoom_factor
        if self.scale_factor < 0.2:
            self.scale_factor = 0.2
        elif self.scale_factor > 5.0:
            self.scale_factor = 5.0
        self.view.scale(zoom_factor, zoom_factor)
        new_pos = self.view.mapToScene(event.pos())
        delta = new_pos - old_pos
        self.view.translate(delta.x(), delta.y())

    def zoom_in(self):
        # Увеличение масштаба
        self.scale_factor *= 1.25
        if self.scale_factor > 5.0:
            self.scale_factor = 5.0
        self.view.scale(1.25, 1.25)

    def zoom_out(self):
        # Уменьшение масштаба
        self.scale_factor /= 1.25
        if self.scale_factor < 0.2:
            self.scale_factor = 0.2
        self.view.scale(0.8, 0.8)

    def import_gedcom(self):
        # Импорт GEDCOM-файла
        file_name, _ = QFileDialog.getOpenFileName(self, "Импортировать GEDCOM", "", "GEDCOM Files (*.ged)")
        if file_name:
            try:
                self.gedcom_handler.import_gedcom(file_name)
                self.update_tree_view()
                self.update_people_table()
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