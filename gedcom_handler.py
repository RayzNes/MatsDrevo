from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser

class GedcomHandler:
    def __init__(self, tree):
        self.tree = tree

    def import_gedcom(self, file_path):
        # Импорт GEDCOM-файла
        try:
            parser = Parser()
            parser.parse_file(file_path)
            root = parser.get_root_element()

            # Очистка текущего дерева
            self.tree.people.clear()

            # Получение всех индивидуумов
            individuals = parser.get_element_list()
            for element in individuals:
                if isinstance(element, IndividualElement):
                    person_id = element.get_pointer()
                    if not person_id:
                        continue  # Пропуск некорректных записей
                    name = " ".join(filter(None, element.get_name())).strip() or "Без имени"
                    self.tree.add_person(name)

            # Обработка семей
            for element in individuals:
                if isinstance(element, IndividualElement):
                    person_id = element.get_pointer()
                    if not person_id or person_id not in self.tree.people:
                        continue
                    families = element.get_families()
                    for family in families:
                        children = family.get_children()
                        for child in children:
                            child_id = child.get_pointer()
                            if child_id and child_id in self.tree.people:
                                self.tree.people[child_id]["parents"].append(person_id)
                                self.tree.people[person_id]["children"].append(child_id)
        except Exception as e:
            raise ValueError(f"Ошибка при импорте GEDCOM: {str(e)}")

    def export_gedcom(self, file_path):
        # Экспорт данных в GEDCOM-файл
        try:
            lines = [
                "0 HEAD",
                "1 GEDC",
                "2 VERS 5.5.1",
                "2 FORM LINEAGE-LINKED",
                "1 CHAR UTF-8",
            ]

            # Добавление индивидуумов
            for person_id, person in self.tree.people.items():
                name = person["name"].split()
                first_name = name[0]
                last_name = name[-1] if len(name) > 1 else ""
                lines.append(f"0 {person_id} INDI")
                lines.append(f"1 NAME {first_name} /{last_name}/")

            # Завершение файла
            lines.append("0 TRLR")

            # Запись в файл
            with open(file_path, "w", encoding="utf-8") as f:
                for line in lines:
                    f.write(line + "\n")
        except Exception as e:
            raise ValueError(f"Ошибка при экспорте GEDCOM: {str(e)}")