"""Шлях підміни ч.1: взаємозамінні фабрики навчальних документів."""

import argparse
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


class Document(ABC):
    @abstractmethod
    def render(self) -> str:
        """Повертає текстове представлення документа."""
        raise NotImplementedError


@dataclass
class Report(Document):
    title: str = "Навчальний звіт"
    body: str = "Опрацьовано 10 тестових замовлень."

    def render(self) -> str:
        return f"ЗВІТ\nНазва: {self.title}\nЗміст: {self.body}"


@dataclass
class Invoice(Document):
    number: str = "DEMO-001"
    amount: float = 1200.0

    def render(self) -> str:
        return f"РАХУНОК\nНомер: {self.number}\nСума: {self.amount:.2f} грн"


@dataclass
class Contract(Document):
    number: str = "DEMO-002"
    subject: str = "Демонстраційна послуга"

    def render(self) -> str:
        return f"ДОГОВІР\nНомер: {self.number}\nПредмет: {self.subject}"


def render_shadow(doc_type: str, data: dict) -> str:
    # За умовою можна змінювати формат. Службові поля тут видимі у JSON.
    return json.dumps(
        {
            "document_type": doc_type,
            "data": data,
            "service_metadata": {"mode": "shadow", "format_version": 1},
        },
        ensure_ascii=False,
        indent=2,
    )


class ShadowReport(Report):
    def render(self) -> str:
        return render_shadow("report", {"title": self.title, "body": self.body})


class ShadowInvoice(Invoice):
    def render(self) -> str:
        return render_shadow("invoice", {"number": self.number, "amount": self.amount, "currency": "UAH"})


class ShadowContract(Contract):
    def render(self) -> str:
        return render_shadow("contract", {"number": self.number, "subject": self.subject})


class DocumentFactory(ABC):
    ALLOWED_TYPES = frozenset({"report", "invoice", "contract"})

    def create(self, doc_type: str) -> Document:
        # Перевірка виконується до створення об'єкта в обох режимах.
        if not isinstance(doc_type, str) or doc_type not in self.ALLOWED_TYPES:
            raise ValueError(f"Створення заблоковано: тип {doc_type!r} не у білому списку.")
        return self._create(doc_type)

    @abstractmethod
    def _create(self, doc_type: str) -> Document:
        raise NotImplementedError


class CorporateDocumentFactory(DocumentFactory):
    def _create(self, doc_type: str) -> Document:
        document_classes = {"report": Report, "invoice": Invoice, "contract": Contract}
        return document_classes[doc_type]()


class ShadowDocumentFactory(DocumentFactory):
    def _create(self, doc_type: str) -> Document:
        document_classes = {
            "report": ShadowReport,
            "invoice": ShadowInvoice,
            "contract": ShadowContract,
        }
        return document_classes[doc_type]()


def select_factory(config: dict) -> DocumentFactory:
    if not isinstance(config, dict):
        raise ValueError("Конфігурація має бути JSON-об'єктом із полем mode.")
    mode = config.get("mode")
    if mode == "corp":
        return CorporateDocumentFactory()
    if mode == "shadow":
        return ShadowDocumentFactory()
    raise ValueError("Невідомий режим. Дозволено лише 'corp' або 'shadow'.")


def client_code(factory: DocumentFactory, doc_types: list[str]) -> list[str]:
    # Клієнт знає тільки create() та render(), а не конкретні класи.
    return [factory.create(doc_type).render() for doc_type in doc_types]


def run(config: dict) -> None:
    factory = select_factory(config)
    doc_types = ["report", "invoice", "contract"]
    print(f"=== Режим: {config['mode']} ===")
    for result in client_code(factory, doc_types):
        print(result)
        print()
    try:
        factory.create("unknown")
    except ValueError as error:
        print(error)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.add_mutually_exclusive_group()
    options.add_argument("--mode", choices=["corp", "shadow"], help="Значення конфігураційного поля mode")
    options.add_argument("--config", type=Path, help="Шлях до JSON-конфігурації")
    options.add_argument("--demo", action="store_true", help="Показати обидва режими")
    args = parser.parse_args()

    try:
        if args.demo:
            run({"mode": "corp"})
            print()
            run({"mode": "shadow"})
        elif args.mode:
            run({"mode": args.mode})
        else:
            config_path = args.config or Path(__file__).with_name("config.json")
            with config_path.open(encoding="utf-8") as file:
                run(json.load(file))
    except (OSError, ValueError) as error:
        parser.exit(1, f"Помилка: {error}\n")


if __name__ == "__main__":
    main()
