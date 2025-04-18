from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsView, QGraphicsScene, \
    QLineEdit, QFileDialog, QMessageBox, QDialog, QFormLayout, QLabel, QTabWidget, QTableWidget, QTableWidgetItem, \
    QTextBrowser, QComboBox, QSpinBox, QMenu, QAction
from PyQt5.QtGui import QPen, QFont, QPixmap, QPainter
from PyQt5.QtCore import Qt, QRectF
from gedcom_handler import GedcomHandler
from stats import FamilyStats
from settings import SettingsManager
import os
import json
import zipfile
import shutil


class PersonDialog(QDialog):
    def __init__(self, parent=None, person_data=None):
        super().__init__(parent)
        self.person_data = person_data
        self.setWindowTitle("Добавить человека" if not person_data else "Изменить человека")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.surname = QLineEdit(self.person_data.get("surname", "") if self.person_data else "")
        self.name = QLineEdit(self.person_data.get("name", "") if self.person_data else "")
        self.patronymic = QLineEdit(self.person_data.get("patronymic", "") if self.person_data else "")
        self.birth_date = QLineEdit(self.person_data.get("birth_date", "") if self.person_data else "")
        self.death_date = QLineEdit(self.person_data.get("death_date", "") if self.person_data else "")
        self.birth_place = QLineEdit(self.person_data.get("birth_place", "") if self.person_data else "")
        self.death_place = QLineEdit(self.person_data.get("death_place", "") if self.person_data else "")
        self.notes = QLineEdit(self.person_data.get("notes", "") if self.person_data else "")
        self.image_path = QLineEdit(self.person_data.get("image_path", "") if self.person_data else "")
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
        ok_button = QPushButton("Сохранить" if self.person_data else "Добавить")
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
            "birth_place": self.birth_place.text().strip(),
            "death_place": self.death_place.text().strip(),
            "notes": self.notes.text().strip(),
            "image_path": self.image_path.text().strip()
        }


class GenealogyApp(QMainWindow):
    def __init__(self, tree):
        super().__init__()
        self.tree = tree
        self.gedcom_handler = GedcomHandler(self.tree)
        self.stats = FamilyStats(self.tree)
        self.settings = SettingsManager()
        self.scale_factor = self.settings.get_setting("default_scale", 1.0)
        self.node_to_id = {}  # Для контекстного меню: узел -> ID персоны
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

        # Вкладка "Персоны"
        persons_widget = QWidget()
        persons_layout = QVBoxLayout(persons_widget)

        # Панель управления для добавления/удаления
        persons_control = QWidget()
        persons_control_layout = QHBoxLayout(persons_control)

        self.parent_input = QLineEdit()
        self.parent_input.setPlaceholderText("ID родителя (необязательно)")
        persons_control_layout.addWidget(self.parent_input)

        add_button = QPushButton("Добавить человека")
        add_button.clicked.connect(self.add_person)
        persons_control_layout.addWidget(add_button)

        remove_button = QPushButton("Удалить человека")
        remove_button.clicked.connect(self.remove_person)
        persons_control_layout.addWidget(remove_button)

        persons_layout.addWidget(persons_control)

        # Таблица персон
        self.persons_table = QTableWidget()
        self.persons_table.setColumnCount(9)
        self.persons_table.setHorizontalHeaderLabels(
            ["ID", "Фамилия", "Имя", "Отчество", "Дата рождения", "Дата смерти", "Место рождения", "Место смерти",
             "Заметки"])
        self.persons_table.horizontalHeader().setStretchLastSection(True)
        persons_layout.addWidget(self.persons_table)
        self.tabs.addTab(persons_widget, "Персоны")

        # Вкладка "Древо"
        tree_widget = QWidget()
        tree_layout = QHBoxLayout(tree_widget)

        # Панель управления
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)

        import_button = QPushButton("Импортировать GEDCOM")
        import_button.clicked.connect(self.import_gedcom)
        control_layout.addWidget(import_button)

        export_button = QPushButton("Экспортировать GEDCOM")
        export_button.clicked.connect(self.export_gedcom)
        control_layout.addWidget(export_button)

        save_tree_button = QPushButton("Сохранить древо")
        save_tree_button.clicked.connect(self.save_tree)
        control_layout.addWidget(save_tree_button)

        load_tree_button = QPushButton("Загрузить древо")
        load_tree_button.clicked.connect(self.load_tree)
        control_layout.addWidget(load_tree_button)

        backup_button = QPushButton("Создать архивную копию")
        backup_button.clicked.connect(self.create_backup)
        control_layout.addWidget(backup_button)

        new_tree_button = QPushButton("Создать новое древо")
        new_tree_button.clicked.connect(self.create_new_tree)
        control_layout.addWidget(new_tree_button)

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
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.show_context_menu)
        tree_layout.addWidget(self.view, 4)
        self.tabs.addTab(tree_widget, "Древо")

        # Вкладка "Статистика"
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        self.stats_text = QTextBrowser()
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        update_stats_button = QPushButton("Обновить статистику")
        update_stats_button.clicked.connect(self.update_stats)
        stats_layout.addWidget(update_stats_button)
        self.tabs.addTab(stats_widget, "Статистика")

        # Вкладка "Настройки"
        settings_widget = QWidget()
        settings_layout = QFormLayout(settings_widget)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая", "Тёмная"])
        self.theme_combo.setCurrentText(self.settings.get_setting("theme", "Светлая"))
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        settings_layout.addRow("Тема:", self.theme_combo)

        self.scale_spin = QSpinBox()
        self.scale_spin.setRange(50, 200)
        self.scale_spin.setSingleStep(10)
        self.scale_spin.setValue(int(self.settings.get_setting("default_scale", 1.0) * 100))
        self.scale_spin.valueChanged.connect(self.change_scale)
        settings_layout.addRow("Масштаб (%):", self.scale_spin)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 16)
        self.font_size_spin.setValue(self.settings.get_setting("font_size", 10))
        self.font_size_spin.valueChanged.connect(self.change_font_size)
        settings_layout.addRow("Размер шрифта:", self.font_size_spin)

        save_settings_button = QPushButton("Сохранить настройки")
        save_settings_button.clicked.connect(self.save_settings)
        settings_layout.addRow(save_settings_button)

        self.tabs.addTab(settings_widget, "Настройки")

        # Вкладка "О программе"
        about_widget = QWidget()
        about_layout = QVBoxLayout(about_widget)
        about_text = QTextBrowser()
        about_text.setReadOnly(True)
        about_text.setOpenExternalLinks(True)
        about_text.setText("""
        <h2>MatsDrevo</h2>
        <p>Версия: 1.0</p>
        <p>Автор: xAI</p>
        <p>Описание: Программа для создания и управления генеалогическими деревьями. Поддерживает добавление до 1500 человек, импорт/экспорт GEDCOM, изображения, зум и расширенные данные о персонах.</p>
        <p>Канал студии: <a href="https://t.me/MatsStudio">https://t.me/MatsStudio</a></p>
        """)
        about_layout.addWidget(about_text)
        self.tabs.addTab(about_widget, "О программе")

        self.update_tree_view()
        self.update_persons_table()
        self.update_stats()

    def load_styles(self):
        # Загрузка стилей
        try:
            theme = self.settings.get_setting("theme", "Светлая")
            style_file = "styles_dark.css" if theme == "Тёмная" else "styles.css"
            if os.path.exists(style_file):
                with open(style_file, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
            self.update_tree_view()  # Перерисовка для применения шрифта
        except Exception as e:
            QMessageBox.critical(self, "Ошибка стилей", f"Не удалось загрузить стили: {str(e)}")

    def add_person(self):
        # Открытие диалогового окна для добавления человека
        try:
            dialog = PersonDialog(self)
            if dialog.exec_():
                data = dialog.get_data()
                parent_id = self.parent_input.text().strip()
                self.tree.add_person(data, parent_id if parent_id and parent_id in self.tree.people else None)
                self.update_tree_view()
                self.update_persons_table()
                self.update_stats()
                self.parent_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка добавления", f"Не удалось добавить человека: {str(e)}")

    def remove_person(self):
        # Удаление человека из дерева
        try:
            person_id = self.parent_input.text().strip()
            if person_id and person_id in self.tree.people:
                self.tree.remove_person(person_id)
                self.update_tree_view()
                self.update_persons_table()
                self.update_stats()
            else:
                QMessageBox.warning(self, "Ошибка ввода", "Неверный ID человека")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка удаления", f"Не удалось удалить человека: {str(e)}")

    def update_persons_table(self):
        # Обновление таблицы персон
        try:
            self.persons_table.setRowCount(len(self.tree.people))
            row = 0
            for pid, person in sorted(self.tree.people.items()):
                self.persons_table.setItem(row, 0, QTableWidgetItem(pid))
                self.persons_table.setItem(row, 1, QTableWidgetItem(person["surname"]))
                self.persons_table.setItem(row, 2, QTableWidgetItem(person["name"]))
                self.persons_table.setItem(row, 3, QTableWidgetItem(person["patronymic"]))
                self.persons_table.setItem(row, 4, QTableWidgetItem(person["birth_date"]))
                self.persons_table.setItem(row, 5, QTableWidgetItem(person["death_date"]))
                self.persons_table.setItem(row, 6, QTableWidgetItem(person["birth_place"]))
                self.persons_table.setItem(row, 7, QTableWidgetItem(person["death_place"]))
                self.persons_table.setItem(row, 8, QTableWidgetItem(person["notes"]))
                row += 1
            self.persons_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка таблицы", f"Не удалось обновить таблицу: {str(e)}")

    def update_tree_view(self):
        # Обновление графического представления дерева
        try:
            self.scene.clear()
            self.node_to_id.clear()
            if not self.tree.people:
                return

            positions = {}
            node_size = 120
            image_size = 50
            spacing_x = 180
            spacing_y = 120
            visited = set()

            def get_level(person_id, memo={}):
                if person_id in memo:
                    return memo[person_id]
                if person_id not in self.tree.people:
                    return 0
                person = self.tree.people[person_id]
                parent_levels = [get_level(parent_id, memo) + 1 for parent_id in person.get("parents", []) if
                                 parent_id in self.tree.people]
                level = max(parent_levels, default=0)
                memo[person_id] = level
                return level

            def assign_positions(person_id, x=0, level=0):
                if person_id in visited or person_id not in self.tree.people:
                    return x
                visited.add(person_id)
                person = self.tree.people[person_id]
                current_level = get_level(person_id)
                if level != current_level:
                    return x  # Пропускаем, если уровень не соответствует
                positions[person_id] = (x, level * spacing_y)
                children = person.get("children", [])
                num_children = len(children)
                next_x = x
                for i, child_id in enumerate(children):
                    if child_id in self.tree.people:
                        child_x = assign_positions(child_id, next_x, level + 1)
                        next_x = child_x + spacing_x
                return next_x

            # Поиск корневых узлов
            root_ids = [pid for pid, p in self.tree.people.items() if not p.get("parents")]
            if not root_ids:  # Если нет корневых, берём всех
                root_ids = list(self.tree.people.keys())

            x_offset = 0
            for root_id in root_ids:
                x_offset = assign_positions(root_id, x_offset, 0)

            # Отрисовка узлов и связей
            font_size = self.settings.get_setting("font_size", 10)
            for pid, (x, y) in positions.items():
                person = self.tree.people.get(pid)
                if not person:
                    continue
                # Отрисовка изображения
                image_path = person.get("image_path", "")
                if image_path and os.path.exists(image_path):
                    pixmap = QPixmap(image_path).scaled(image_size, image_size, Qt.KeepAspectRatio)
                    image_item = self.scene.addPixmap(pixmap)
                    image_item.setPos(x, y)
                    self.node_to_id[id(image_item)] = pid
                else:
                    rect_item = self.scene.addRect(x, y, image_size, image_size, QPen(Qt.gray), Qt.lightGray)
                    self.node_to_id[id(rect_item)] = pid

                # Отрисовка текста
                text = f"{person['surname']} {person['name']} {person['patronymic']}\nID: {pid}".strip()
                rect = self.scene.addRect(x + image_size + 5, y, node_size, image_size, QPen(Qt.black), Qt.lightGray)
                text_item = self.scene.addText(text)
                text_item.setFont(QFont("Arial", font_size))
                text_item.setPos(x + image_size + 10, y + 10)
                self.node_to_id[id(text_item)] = pid
                self.node_to_id[id(rect)] = pid

                # Отрисовка связей
                for child_id in person.get("children", []):
                    if child_id in positions:
                        cx, cy = positions[child_id]
                        self.scene.addLine(x + image_size / 2, y + image_size, cx + image_size / 2, cy, QPen(Qt.black))

            # Оптимизация отображения
            if positions:
                self.view.setSceneRect(self.scene.itemsBoundingRect())
                self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
                self.view.scale(self.scale_factor, self.scale_factor)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка отображения", f"Не удалось обновить дерево: {str(e)}")

    def show_context_menu(self, pos):
        # Контекстное меню для древа
        try:
            item = self.view.itemAt(pos)
            if not item or id(item) not in self.node_to_id:
                return
            person_id = self.node_to_id[id(item)]
            person = self.tree.get_person(person_id)
            if not person:
                return

            menu = QMenu(self)
            create_menu = QMenu("Создать", self)

            spouse_action = QAction("Супруга", self)
            spouse_action.triggered.connect(lambda: self.create_relative(person_id, "spouse"))
            create_menu.addAction(spouse_action)

            mother_action = QAction("Мать", self)
            mother_action.triggered.connect(lambda: self.create_relative(person_id, "mother"))
            create_menu.addAction(mother_action)

            father_action = QAction("Отец", self)
            father_action.triggered.connect(lambda: self.create_relative(person_id, "father"))
            create_menu.addAction(father_action)

            son_action = QAction("Сын", self)
            son_action.triggered.connect(lambda: self.create_relative(person_id, "son"))
            create_menu.addAction(son_action)

            daughter_action = QAction("Дочь", self)
            daughter_action.triggered.connect(lambda: self.create_relative(person_id, "daughter"))
            create_menu.addAction(daughter_action)

            brother_action = QAction("Брат", self)
            brother_action.triggered.connect(lambda: self.create_relative(person_id, "brother"))
            create_menu.addAction(brother_action)

            sister_action = QAction("Сестра", self)
            sister_action.triggered.connect(lambda: self.create_relative(person_id, "sister"))
            create_menu.addAction(sister_action)

            menu.addMenu(create_menu)

            edit_action = QAction("Изменить", self)
            edit_action.triggered.connect(lambda: self.edit_person(person_id))
            menu.addAction(edit_action)

            delete_action = QAction("Удалить", self)
            delete_action.triggered.connect(lambda: self.delete_person(person_id))
            menu.addAction(delete_action)

            menu.exec_(self.view.mapToGlobal(pos))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка меню", f"Не удалось открыть контекстное меню: {str(e)}")

    def create_relative(self, person_id, relation):
        # Создание родственника
        try:
            dialog = PersonDialog(self)
            if dialog.exec_():
                data = dialog.get_data()
                new_person_id = self.tree.add_person(data)
                person = self.tree.get_person(person_id)

                if relation == "spouse":
                    # Супруг не требует прямой связи в дереве
                    pass
                elif relation == "mother" or relation == "father":
                    self.tree.people[new_person_id]["children"].append(person_id)
                    self.tree.people[person_id]["parents"].append(new_person_id)
                elif relation == "son" or relation == "daughter":
                    self.tree.people[person_id]["children"].append(new_person_id)
                    self.tree.people[new_person_id]["parents"].append(person_id)
                elif relation == "brother" or relation == "sister":
                    for parent_id in person.get("parents", []):
                        self.tree.people[parent_id]["children"].append(new_person_id)
                        self.tree.people[new_person_id]["parents"].append(parent_id)

                self.update_tree_view()
                self.update_persons_table()
                self.update_stats()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка создания", f"Не удалось создать родственника: {str(e)}")

    def edit_person(self, person_id):
        # Редактирование персоны
        try:
            person = self.tree.get_person(person_id)
            dialog = PersonDialog(self, person)
            if dialog.exec_():
                new_data = dialog.get_data()
                # Обновляем данные, сохраняя связи
                self.tree.people[person_id].update({
                    "surname": new_data["surname"],
                    "name": new_data["name"],
                    "patronymic": new_data["patronymic"],
                    "birth_date": new_data["birth_date"],
                    "death_date": new_data["death_date"],
                    "birth_place": new_data["birth_place"],
                    "death_place": new_data["death_place"],
                    "notes": new_data["notes"],
                    "image_path": new_data["image_path"]
                })
                # Копирование нового изображения
                if new_data["image_path"] and os.path.exists(new_data["image_path"]):
                    import shutil
                    os.makedirs("images", exist_ok=True)
                    dest_path = f"images/{person_id}{os.path.splitext(new_data['image_path'])[1]}"
                    shutil.copy(new_data["image_path"], dest_path)
                    self.tree.people[person_id]["image_path"] = dest_path
                self.update_tree_view()
                self.update_persons_table()
                self.update_stats()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка редактирования", f"Не удалось изменить персону: {str(e)}")

    def delete_person(self, person_id):
        # Удаление персоны
        try:
            if QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить эту персону?") == QMessageBox.Yes:
                self.tree.remove_person(person_id)
                self.update_tree_view()
                self.update_persons_table()
                self.update_stats()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка удаления", f"Не удалось удалить персону: {str(e)}")

    def wheelEvent(self, event):
        # Обработка зума колесиком мыши
        try:
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
        except Exception as e:
            QMessageBox.critical(self, "Ошибка зума", f"Не удалось изменить масштаб: {str(e)}")

    def zoom_in(self):
        # Увеличение масштаба
        try:
            self.scale_factor *= 1.25
            if self.scale_factor > 5.0:
                self.scale_factor = 5.0
            self.view.scale(1.25, 1.25)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка зума", f"Не удалось увеличить масштаб: {str(e)}")

    def zoom_out(self):
        # Уменьшение масштаба
        try:
            self.scale_factor /= 1.25
            if self.scale_factor < 0.2:
                self.scale_factor = 0.2
            self.view.scale(0.8, 0.8)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка зума", f"Не удалось уменьшить масштаб: {str(e)}")

    def save_tree(self):
        # Сохранение дерева в JSON-файл
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить древо", "", "JSON Files (*.json)")
            if file_name:
                with open(file_name, "w", encoding="utf-8") as f:
                    json.dump(self.tree.people, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "Успех", "Древо успешно сохранено")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось сохранить древо: {str(e)}")

    def load_tree(self):
        # Загрузка дерева из JSON-файла
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Загрузить древо", "", "JSON Files (*.json)")
            if file_name:
                with open(file_name, "r", encoding="utf-8") as f:
                    self.tree.people = json.load(f)
                self.update_tree_view()
                self.update_persons_table()
                self.update_stats()
                QMessageBox.information(self, "Успех", "Древо успешно загружено")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки", f"Не удалось загрузить древо: {str(e)}")

    def create_backup(self):
        # Создание архивной копии (ZIP)
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, "Создать архивную копию", "", "ZIP Files (*.zip)")
            if file_name:
                with zipfile.ZipFile(file_name, "w", zipfile.ZIP_DEFLATED) as zf:
                    # Сохранение дерева в временный JSON
                    temp_json = "temp_tree.json"
                    with open(temp_json, "w", encoding="utf-8") as f:
                        json.dump(self.tree.people, f, ensure_ascii=False, indent=2)
                    zf.write(temp_json, "tree.json")
                    os.remove(temp_json)
                    # Добавление изображений
                    if os.path.exists("images"):
                        for img in os.listdir("images"):
                            zf.write(os.path.join("images", img), os.path.join("images", img))
                QMessageBox.information(self, "Успех", "Архивная копия успешно создана")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка архивации", f"Не удалось создать архив: {str(e)}")

    def create_new_tree(self):
        # Создание нового дерева
        try:
            if QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите создать новое древо? Все несохранённые данные будут потеряны.") == QMessageBox.Yes:
                self.tree.people.clear()
                if os.path.exists("images"):
                    shutil.rmtree("images")
                os.makedirs("images", exist_ok=True)
                self.update_tree_view()
                self.update_persons_table()
                self.update_stats()
                QMessageBox.information(self, "Успех", "Новое древо создано")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка создания", f"Не удалось создать новое древо: {str(e)}")

    def import_gedcom(self):
        # Импорт GEDCOM-файла
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Импортировать GEDCOM", "", "GEDCOM Files (*.ged)")
            if file_name:
                self.gedcom_handler.import_gedcom(file_name)
                self.update_tree_view()
                self.update_persons_table()
                self.update_stats()
                QMessageBox.information(self, "Успех", "GEDCOM-файл успешно импортирован")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка импорта", f"Не удалось импортировать GEDCOM: {str(e)}")

    def export_gedcom(self):
        # Экспорт в GEDCOM-файл
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, "Экспортировать GEDCOM", "", "GEDCOM Files (*.ged)")
            if file_name:
                self.gedcom_handler.export_gedcom(file_name)
                QMessageBox.information(self, "Успех", "GEDCOM-файл успешно экспортирован")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", f"Не удалось экспортировать GEDCOM: {str(e)}")

    def update_stats(self):
        # Обновление статистики
        try:
            stats = self.stats.get_statistics()
            stats_html = f"""
            <h2>Статистика семьи</h2>
            <p><b>Общее количество людей:</b> {stats['total_people']}</p>
            <p><b>Количество семей:</b> {stats['total_families']}</p>
            <p><b>Количество поколений:</b> {stats['generations']}</p>
            <p><b>Средний возраст:</b> {stats['average_age']:.1f} лет</p>
            """
            self.stats_text.setHtml(stats_html)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка статистики", f"Не удалось обновить статистику: {str(e)}")

    def change_theme(self, theme):
        # Изменение темы
        try:
            self.settings.set_setting("theme", theme)
            self.load_styles()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка темы", f"Не удалось изменить тему: {str(e)}")

    def change_scale(self, value):
        # Изменение масштаба
        try:
            self.scale_factor = value / 100.0
            self.settings.set_setting("default_scale", self.scale_factor)
            self.update_tree_view()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка масштаба", f"Не удалось изменить масштаб: {str(e)}")

    def change_font_size(self, size):
        # Изменение размера шрифта
        try:
            self.settings.set_setting("font_size", size)
            self.update_tree_view()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка шрифта", f"Не удалось изменить размер шрифта: {str(e)}")

    def save_settings(self):
        # Сохранение настроек
        try:
            self.settings.save_settings()
            self.load_styles()
            QMessageBox.information(self, "Успех", "Настройки сохранены")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось сохранить настройки: {str(e)}")