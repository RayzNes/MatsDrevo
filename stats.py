from datetime import datetime

class FamilyStats:
    def __init__(self, tree):
        self.tree = tree

    def get_statistics(self):
        # Подсчёт статистики семьи
        total_people = len(self.tree.people)
        total_families = 0
        generations = 0
        ages = []

        # Подсчёт семей (родители с детьми)
        for person_id, person in self.tree.people.items():
            if person.get("children"):
                total_families += 1

        # Подсчёт поколений
        visited = set()
        def get_depth(person_id, depth=0):
            if person_id in visited or person_id not in self.tree.people:
                return depth
            visited.add(person_id)
            person = self.tree.people[person_id]
            max_child_depth = depth
            for child_id in person.get("children", []):
                child_depth = get_depth(child_id, depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
            return max_child_depth

        for person_id in self.tree.people:
            if not self.tree.people[person_id].get("parents"):
                generations = max(generations, get_depth(person_id))

        # Подсчёт среднего возраста
        current_year = datetime.now().year
        for person in self.tree.people.values():
            birth_date = person.get("birth_date", "")
            death_date = person.get("death_date", "")
            try:
                birth_year = int(birth_date.split()[-1]) if birth_date else None
                death_year = int(death_date.split()[-1]) if death_date else current_year
                if birth_year:
                    age = death_year - birth_year
                    if 0 < age < 120:  # Фильтрация нереальных возрастов
                        ages.append(age)
            except (ValueError, IndexError):
                continue

        average_age = sum(ages) / len(ages) if ages else 0

        return {
            "total_people": total_people,
            "total_families": total_families,
            "generations": generations,
            "average_age": average_age
        }