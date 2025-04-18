import uuid


class FamilyTree:
    def __init__(self):
        self.people = {}  # {id: {name, parents, children}}

    def add_person(self, name, parent_id=None):
        person_id = str(uuid.uuid4())
        person = {"name": name, "parents": [], "children": []}
        self.people[person_id] = person

        if parent_id and parent_id in self.people:
            person["parents"].append(parent_id)
            self.people[parent_id]["children"].append(person_id)

    def remove_person(self, person_id):
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

        del self.people[person_id]

    def get_person(self, person_id):
        return self.people.get(person_id, None)