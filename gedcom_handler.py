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
                        continue
                    name_parts = element.get_name()
                    surname = name_parts[1].strip() if name_parts[1] else ""
                    name = name_parts[0].strip() if name_parts[0] else ""
                    data = {
                        "surname": surname,
                        "name": name,
                        "patronymic": "",
                        "birth_date": "",
                        "death_date": "",
                        "birth_place": "",
                        "death_place": "",
                        "notes": "",
                        "image_path": ""
                    }
                    # Извлечение дополнительных данных
                    for child in element.get_child_elements():
                        if child.get_tag() == "BIRT":
                            for subchild in child.get_child_elements():
                                if subchild.get_tag() == "DATE":
                                    data["birth_date"] = subchild.get_value()
                                if subchild.get_tag() == "PLAC":
                                    data["birth_place"] = subchild.get_value()
                        if child.get_tag() == "DEAT":
                            for subchild in child.get_child_elements():
                                if subchild.get_tag() == "DATE":
                                    data["death_date"] = subchild.get_value()
                                if subchild.get_tag() == "PLAC":
                                    data["death_place"] = subchild.get_value()
                        if child.get_tag() == "NOTE":
                            data["notes"] = child.get_value()
                    self.tree.add_person(data)

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
                lines.append(f"0 {person_id} INDI")
                name = person["name"]
                surname = person["surname"]
                lines.append(f"1 NAME {name} /{surname}/")
                if person["patronymic"]:
                    lines.append(f"2 GIVN {person['patronymic']}")
                if person["birth_date"]:
                    lines.append("1 BIRT")
                    lines.append(f"2 DATE {person['birth_date']}")
                    if person["birth_place"]:
                        lines.append(f"2 PLAC {person['birth_place']}")
                if person["death_date"]:
                    lines.append("1 DEAT")
                    lines.append(f"2 DATE {person['death_date']}")
                    if person["death_place"]:
                        lines.append(f"2 PLAC {person['death_place']}")
                if person["notes"]:
                    lines.append(f"1 NOTE {person['notes']}")
                if person["image_path"]:
                    lines.append("1 OBJE")
                    lines.append(f"2 FILE {person['image_path']}")

            # Завершение файла
            lines.append("0 TRLR")

            # Запись в файл
            with open(file_path, "w", encoding="utf-8") as f:
                for line in lines:
                    f.write(line + "\n")
        except Exception as e:
            raise ValueError(f"Ошибка при экспорте GEDCOM: {str(e)}")