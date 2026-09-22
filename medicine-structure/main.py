"""Приклад роботи зі списком різних ліків без перевірки їхніх типів."""

from models import Antibiotic, Vitamin, Vaccine


def main() -> None:
    medicines = [
        Antibiotic("Амоксицилін", 10, 120.0),
        Vitamin("Вітамін C", 20, 80.0),
        Vaccine("Вакцина проти грипу", 5, 500.0),
    ]

    # Поліморфізм: однаковий виклик для всіх об'єктів без isinstance та if.
    for medicine in medicines:
        print(medicine.info())
        print("-" * 40)


if __name__ == "__main__":
    main()
