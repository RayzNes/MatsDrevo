import uuid
import os


class FamilyTree:
    def __init__(self):
        self.people = {}  # {id: {surname, name, patronymic, birth_date, death_date, birth_place, death_place, notes, image_path, parents, children}}

    def add_person(self, data, parent_id=None):
        # Добавление человека с расширенными данными
        person_id = str(uuid.uuid4())
        person = {
            "surname": data.get("surname", ""),
            "name": data.get("name", ""),
            "patronymic": data.get("patronymic", ""),
            "birth_date": data.get("birth_date", ""),
            "death_date": data.get("death_date", ""),
            "birth_place": data.get("birth_place", ""),
            "death_place": data.get("death_place", ""),
            "notes": data.get("notes", ""),
            "image_path": data.get("image_path", ""),
            "parents": [],
            "children": []
        }
        self.people[person_id] = person

        if parent_id and parent_id in self.people:
            person["parents"].append(parent_id)
            self.people[parent_id]["children"].append(person_id)

        # Копирование изображения в папку images
        if person["image_path"] and os.path.exists(person["image_path"]):
            import shutil
            os.makedirs("images", exist_ok=True)
            dest_path = f"images/{person_id}{os.path.splitext(person['image_path'])[1]}"
            shutil.copy(person["image_path"], dest_path)
            person["image_path"] = dest_path

        return person_id

    def remove_person(self, person_id):
        # Удаление человека из дерева
        if person_id not in self.people:
            return
        person = self.people[person_id]

        # Удаление связей с родителями
        for parent_id in person["parents"]:
            if parent_id in self.people:
                self.people[parent_id]["children"].remove(person_id)

        # Удаление связей с детьми
        for child_id in person["children"]:
            if child_id in self.people:
                self.people[child_id]["parents"].remove(person_id)

        # Удаление изображения
        if person["image_path"] and os.path.exists(person["image_path"]):
            os.remove(person["image_path"])

        del self.people[person_id]

    def get_person(self, person_id):
        # Получение данных о человеке
        return self.people.get(person_id, None)