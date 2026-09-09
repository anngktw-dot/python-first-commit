medicines = [
    {
        "name": "Амоксицилін",
        "quantity": 25,
        "category": "antibiotic",
        "temperature": 18.5,
    },
    {
        "name": "Вітамін C",
        "quantity": 40,
        "category": "vitamin",
        "temperature": 26.0,
    },
    {
        "name": "Вакцина",
        "quantity": 10,
        "category": "vaccine",
        "temperature": 3.5,
    },
    {
        "name": "Тестовий препарат",
        "quantity": "п'ять",
        "category": "other",
        "temperature": 20.0,
    },
]

for medicine in medicines:
    name = medicine["name"]
    quantity = medicine["quantity"]
    category = medicine["category"]
    temperature = medicine["temperature"]

    if type(quantity) is not int or type(temperature) is not float:
        print(f"{name}: Помилка даних")
        continue

    match category:
        case "antibiotic":
            category_status = "Рецептурний препарат"
        case "vitamin":
            category_status = "Вільний продаж"
        case "vaccine":
            category_status = "Потребує спецзберігання"
        case _:
            category_status = "Невідома категорія"

    if temperature < 5:
        temperature_status = "Надто холодно"
    elif temperature > 25:
        temperature_status = "Надто жарко"
    else:
        temperature_status = "Норма"

    print(f"{name}: {category_status}; {temperature_status}")
