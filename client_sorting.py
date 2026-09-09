clients = [
    {"name": "Олег", "amount": 75, "status": "clean"},
    {"name": "Марина", "amount": 450.5, "status": "suspicious"},
    {"name": "Ігор", "amount": 1500, "status": "fraud"},
    {"name": "Анна", "amount": 1000.0, "status": "clean"},
    {"name": "Невідомий", "amount": 300, "status": "pending"},
    {"name": "Помилковий клієнт", "amount": "багато", "status": "clean"},
]

for client in clients:
    name = client["name"]
    amount = client["amount"]
    status = client["status"]

    if type(amount) not in (int, float):
        print(f"{name}: Фальшиві дані")
        continue

    if amount < 100:
        amount_category = "Дрібнота"
    elif amount < 1000:
        amount_category = "Середнячок"
    else:
        amount_category = "Великий клієнт"

    match status:
        case "clean":
            status_decision = "Працювати без питань"
        case "suspicious":
            status_decision = "Перевірити документи"
        case "fraud":
            status_decision = "У чорний список"
        case _:
            status_decision = "Невідомий статус"

    print(f"{name}: {amount_category}; {status_decision}")
