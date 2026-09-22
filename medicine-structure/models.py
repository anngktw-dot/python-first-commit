"""Моделі ліків: абстракція, успадкування та поліморфізм."""

from abc import ABC, abstractmethod
from math import isfinite


class Medicine(ABC):
    """Абстрактний базовий клас для всіх видів ліків."""

    def __init__(self, name: str, quantity: int, price: float) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Назва має бути непорожнім рядком.")
        if type(quantity) is not int or quantity < 0:
            raise ValueError("Кількість має бути цілим невід'ємним числом.")
        if isinstance(price, bool) or not isinstance(price, (int, float)):
            raise ValueError("Ціна має бути числом.")
        if not isfinite(price) or price < 0:
            raise ValueError("Ціна має бути скінченним невід'ємним числом.")

        self.name = name.strip()
        self.quantity = quantity
        self.price = float(price)

    @abstractmethod
    def requires_prescription(self) -> bool:
        """Чи потрібен рецепт на препарат."""

    @abstractmethod
    def storage_requirements(self) -> str:
        """Умови зберігання препарату."""

    @abstractmethod
    def total_price(self) -> float:
        """Загальна ціна; підкласи можуть змінити її обчислення."""
        return self.quantity * self.price

    @abstractmethod
    def info(self) -> str:
        """Текстова інформація про препарат."""
        prescription = "Так" if self.requires_prescription() else "Ні"
        return (
            f"Тип: {self.__class__.__name__}\n"
            f"Назва: {self.name}\n"
            f"Кількість: {self.quantity}\n"
            f"Ціна за одиницю: {self.price:.2f} грн\n"
            f"Потрібен рецепт: {prescription}\n"
            f"Зберігання: {self.storage_requirements()}\n"
            f"Загальна вартість: {self.total_price():.2f} грн"
        )


class Antibiotic(Medicine):
    def requires_prescription(self) -> bool:
        return True

    def storage_requirements(self) -> str:
        return "8–15°C, темне місце"

    def total_price(self) -> float:
        return super().total_price()

    def info(self) -> str:
        return super().info()


class Vitamin(Medicine):
    def requires_prescription(self) -> bool:
        return False

    def storage_requirements(self) -> str:
        return "15–25°C, сухо"

    def total_price(self) -> float:
        return super().total_price()

    def info(self) -> str:
        return super().info()


class Vaccine(Medicine):
    def requires_prescription(self) -> bool:
        return True

    def storage_requirements(self) -> str:
        return "2–8°C, холодильник"

    def total_price(self) -> float:
        return super().total_price() * 1.10

    def info(self) -> str:
        return super().info()
