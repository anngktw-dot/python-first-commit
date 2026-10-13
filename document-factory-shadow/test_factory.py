import json
import unittest
from unittest.mock import patch

from main import (
    Contract, CorporateDocumentFactory, Document, DocumentFactory, Invoice,
    Report, ShadowContract, ShadowDocumentFactory, ShadowInvoice,
    ShadowReport, client_code, select_factory,
)


class FactoryTests(unittest.TestCase):
    def test_abstract_interfaces_cannot_be_instantiated(self):
        for cls in (Document, DocumentFactory):
            with self.subTest(cls=cls), self.assertRaises(TypeError):
                cls()

    def test_mode_selects_factory(self):
        self.assertIsInstance(select_factory({"mode": "corp"}), CorporateDocumentFactory)
        self.assertIsInstance(select_factory({"mode": "shadow"}), ShadowDocumentFactory)
        for invalid in ({}, {"mode": "other"}, {"mode": None}, []):
            with self.subTest(config=invalid), self.assertRaises(ValueError):
                select_factory(invalid)

    def test_factories_create_correct_document_classes(self):
        for factory, classes in (
            (CorporateDocumentFactory(), (Report, Invoice, Contract)),
            (ShadowDocumentFactory(), (ShadowReport, ShadowInvoice, ShadowContract)),
        ):
            for doc_type, cls in zip(("report", "invoice", "contract"), classes):
                with self.subTest(factory=type(factory).__name__, doc_type=doc_type):
                    document = factory.create(doc_type)
                    self.assertIs(type(document), cls)
                    self.assertIsInstance(document, Document)
                    self.assertIsInstance(document.render(), str)

    def test_disallowed_types_blocked_before_construction(self):
        for factory in (CorporateDocumentFactory(), ShadowDocumentFactory()):
            with patch.object(factory, "_create") as constructor:
                for invalid in ("unknown", "", "REPORT", "report ", "__import__", None, []):
                    with self.subTest(doc_type=invalid), self.assertRaises(ValueError):
                        factory.create(invalid)
                constructor.assert_not_called()

    def test_same_client_renders_different_formats(self):
        doc_types = ["report", "invoice", "contract"]
        corp = client_code(select_factory({"mode": "corp"}), doc_types)
        shadow = client_code(select_factory({"mode": "shadow"}), doc_types)
        self.assertEqual(len(corp), 3)
        self.assertEqual(len(shadow), 3)
        for doc_type, ordinary, alternate in zip(doc_types, corp, shadow):
            with self.subTest(doc_type=doc_type):
                self.assertNotEqual(ordinary, alternate)
                payload = json.loads(alternate)
                self.assertEqual(payload["document_type"], doc_type)
                self.assertEqual(payload["service_metadata"]["mode"], "shadow")

    def test_shadow_preserves_business_data(self):
        report = ShadowReport("Новий звіт", "Тестовий зміст")
        invoice = ShadowInvoice("TEST-005", 99.5)
        contract = ShadowContract("TEST-006", "Тестовий предмет")
        self.assertEqual(json.loads(report.render())["data"], {"title": "Новий звіт", "body": "Тестовий зміст"})
        self.assertEqual(json.loads(invoice.render())["data"]["amount"], 99.5)
        self.assertEqual(json.loads(contract.render())["data"]["subject"], "Тестовий предмет")


if __name__ == "__main__":
    unittest.main()
