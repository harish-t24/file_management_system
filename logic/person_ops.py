import os
import json

persons = []  # (id, name)


def add_person(pid, name):
    persons.append((pid, name))


def update_person(pid, new_name):
    for i, (id_, _) in enumerate(persons):
        if id_ == pid:
            persons[i] = (pid, new_name)
            break


def delete_person_list(pid):
    for i, (id_, _) in enumerate(persons):
        if id_ == pid:
            persons.pop(i)
            break


# ===== LOAD FROM FOLDER STRUCTURE =====
def load_persons():
    global persons

    persons.clear()

    data_folder = "data"

    if not os.path.exists(data_folder):
        return

    for folder in os.listdir(data_folder):

        person_folder = os.path.join(data_folder, folder)

        # only folders (each person)
        if os.path.isdir(person_folder):

            file_path = os.path.join(person_folder, "data.json")

            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)

                    pid = data.get("ID")
                    name = data.get("Full Name", "Unknown")

                    if pid:
                        persons.append((pid, name))

                except:
                    continue