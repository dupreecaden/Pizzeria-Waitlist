import json
import os

class Reservation:
    def __init__(self, name, time, party_size):
        self.name = name
        self.time = time
        self.party_size = party_size

    def __str__(self):
        return f"{self.name} | {self.time} | Party of {self.party_size}"

def save_reservation(res):
    data = {
        "name": res.name,
        "time": res.time,
        "party_size": res.party_size
    }
    with open("reservations.json", "a", encoding='utf-8') as f:
        f.write(json.dumps(data) + "\n")

def load_reservations():
    if not os.path.exists("reservations.json"):
        return []
    reservations = []
    with open("reservations.json", "r", encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    reservations.append(Reservation(data["name"], data["time"], data["party_size"]))
                except json.JSONDecodeError:
                    continue
    return reservations

def clear_all_reservations():
    open("reservations.json", "w", encoding='utf-8').close()

