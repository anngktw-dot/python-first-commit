"""Завдання «Глибина пізнання»: абстракція, наслідування і поліморфізм."""

from abc import ABC, abstractmethod
from math import isfinite


def check_non_negative(value: float, field: str) -> None:
    if not isfinite(value) or value < 0:
        raise ValueError(f"{field} має бути скінченним невід'ємним числом.")


class Transport(ABC):
    def __init__(self, name: str, speed: int, capacity: int):
        if not isinstance(speed, int) or isinstance(speed, bool) or speed <= 0:
            raise ValueError("Швидкість має бути додатним цілим числом.")
        if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 0:
            raise ValueError("Місткість має бути невід'ємним цілим числом.")
        self.name = name
        self.speed = speed
        self.capacity = capacity

    @abstractmethod
    def move(self, distance: float) -> float:
        """Повертає час у годинах для відстані в кілометрах."""
        check_non_negative(distance, "Відстань")
        return float(distance / self.speed)

    @abstractmethod
    def fuel_consumption(self, distance: float) -> float:
        """Повертає витрату пального в літрах."""
        raise NotImplementedError

    @abstractmethod
    def info(self) -> str:
        return f"{self.name}: швидкість {self.speed} км/год, місткість {self.capacity}"

    def energy_consumption(self, distance: float) -> float:
        """Для звичайного транспорту оплачуваний ресурс — пальне."""
        return self.fuel_consumption(distance)

    def calculate_cost(self, distance: float, price_per_unit: float) -> float:
        check_non_negative(distance, "Відстань")
        check_non_negative(price_per_unit, "Ціна")
        return float(self.energy_consumption(distance) * price_per_unit)


class Car(Transport):
    def move(self, distance: float) -> float:
        return super().move(distance)

    def fuel_consumption(self, distance: float) -> float:
        check_non_negative(distance, "Відстань")
        return float(distance * 0.07)

    def info(self) -> str:
        return f"Автомобіль — {super().info()}"


class Bus(Transport):
    def __init__(self, name: str, speed: int, capacity: int, passengers: int = 0):
        super().__init__(name, speed, capacity)
        if not isinstance(passengers, int) or isinstance(passengers, bool) or passengers < 0:
            raise ValueError("Кількість пасажирів має бути невід'ємним цілим числом.")
        self.passengers = passengers

    def move(self, distance: float) -> float:
        return super().move(distance)

    def fuel_consumption(self, distance: float) -> float:
        check_non_negative(distance, "Відстань")
        return float(distance * 0.15)

    def info(self) -> str:
        result = f"Автобус — {super().info()}, пасажирів {self.passengers}"
        if self.passengers > self.capacity:
            result += " — Перевантажено!"
        return result


class Bicycle(Transport):
    def __init__(self, name: str, speed: int, capacity: int = 1):
        # Спочатку перевіряємо швидкість, потім обмежуємо її до 20 км/год.
        super().__init__(name, speed, capacity)
        self.speed = min(self.speed, 20)

    def move(self, distance: float) -> float:
        return super().move(distance)

    def fuel_consumption(self, distance: float) -> float:
        check_non_negative(distance, "Відстань")
        return 0.0

    def info(self) -> str:
        return f"Велосипед — {super().info()}"


class ElectricCar(Car):
    def battery_usage(self, distance: float) -> float:
        """Повертає витрату електроенергії в кВт·год."""
        check_non_negative(distance, "Відстань")
        return float(distance * 0.2)

    def fuel_consumption(self, distance: float) -> float:
        check_non_negative(distance, "Відстань")
        return 0.0

    def energy_consumption(self, distance: float) -> float:
        # Успадкований calculate_cost рахує оплату електрики, а не пального.
        return self.battery_usage(distance)

    def info(self) -> str:
        return f"Електромобіль — {Transport.info(self)}"


def main() -> None:
    distance = 100
    fuel_price = 60.0  # Умовна ціна за літр, не поточна ринкова ціна.
    electricity_price = 5.0  # Умовна ціна за кВт·год.
    transports: list[Transport] = [
        Car("Toyota", speed=100, capacity=5),
        Bus("Богдан", speed=50, capacity=40, passengers=30),
        Bicycle("Trek", speed=30),
        ElectricCar("Nissan Leaf", speed=80, capacity=5),
    ]

    print(f"Розрахунки для поїздки на {distance} км\n")
    # Однакові виклики для різних класів демонструють поліморфізм.
    for transport in transports:
        print(transport.info())
        print(f"Час у дорозі: {transport.move(distance):.2f} год")
        print(f"Витрати пального: {transport.fuel_consumption(distance):.2f} л")
        price = fuel_price
        if isinstance(transport, ElectricCar):
            print(f"Витрати електроенергії: {transport.battery_usage(distance):.2f} кВт·год")
            price = electricity_price
        print(f"Вартість поїздки: {transport.calculate_cost(distance, price):.2f} грн\n")

    overloaded_bus = Bus("Переповнений автобус", speed=50, capacity=40, passengers=45)
    print("Перевірка перевантаження:")
    print(overloaded_bus.info())


if __name__ == "__main__":
    main()
