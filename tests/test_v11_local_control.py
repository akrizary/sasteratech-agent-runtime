import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "src"))
ROOT = pathlib.Path(__file__).parents[1]

from sasteratech_runtime.local_control import (
    AuditLedger,
    BudgetExceeded,
    BudgetLedger,
    CredentialUnavailable,
    DispatchDenied,
    InMemoryCredentialStore,
    KillSwitchStore,
    LocalProviderController,
    OperationMode,
)


class LocalControlTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT)
        root = pathlib.Path(self.tmp.name)
        self.credentials = InMemoryCredentialStore()
        self.metadata = self.credentials.put("deepseek", "synthetic-secret-value-1234")
        self.budgets = BudgetLedger(root / "budget.db")
        self.budgets.create_account("local", 0.10)
        self.switches = KillSwitchStore(root / "switches.db")
        self.audit_path = root / "audit.jsonl"
        self.controller = LocalProviderController(self.credentials, self.budgets, self.switches, AuditLedger(self.audit_path))

    def tearDown(self):
        self.switches.close()
        self.budgets.close()
        self.tmp.cleanup()

    def test_metadata_and_audit_never_contain_raw_secret(self):
        self.assertNotIn("synthetic-secret-value-1234", repr(self.metadata))
        reservation, secret = self.controller.prepare(
            mode=OperationMode.READ_ONLY, provider="deepseek", model="deepseek:deepseek-flash",
            credential_id=self.metadata.credential_id, account_id="local", request_id="request-1", maximum_cost_usd=0.01,
        )
        self.assertEqual(secret, "synthetic-secret-value-1234")
        self.budgets.release(reservation)
        self.assertNotIn(secret, self.audit_path.read_text(encoding="utf-8"))

    def test_budget_rejection_happens_before_secret_resolution(self):
        with self.assertRaises(BudgetExceeded):
            self.controller.prepare(
                mode=OperationMode.READ_ONLY, provider="deepseek", model="deepseek:deepseek-flash",
                credential_id=self.metadata.credential_id, account_id="local", request_id="request-2", maximum_cost_usd=0.11,
            )

    def test_global_kill_switch_blocks_before_dispatch(self):
        self.switches.disable("GLOBAL")
        with self.assertRaises(DispatchDenied):
            self.controller.prepare(
                mode=OperationMode.DRAFT, provider="deepseek", model="deepseek:deepseek-flash",
                credential_id=self.metadata.credential_id, account_id="local", request_id="request-3", maximum_cost_usd=0.01,
            )

    def test_unknown_model_and_disabled_credential_are_denied(self):
        with self.assertRaises(DispatchDenied):
            self.controller.prepare(
                mode=OperationMode.READ_ONLY, provider="deepseek", model="deepseek:other",
                credential_id=self.metadata.credential_id, account_id="local", request_id="request-4", maximum_cost_usd=0.01,
            )
        self.credentials.disable(self.metadata.credential_id, "test")
        with self.assertRaises(CredentialUnavailable):
            self.controller.prepare(
                mode=OperationMode.READ_ONLY, provider="deepseek", model="deepseek:deepseek-flash",
                credential_id=self.metadata.credential_id, account_id="local", request_id="request-5", maximum_cost_usd=0.01,
            )

    def test_audit_chain_links_records(self):
        chain_path = pathlib.Path(self.tmp.name) / "chain.jsonl"
        ledger = AuditLedger(chain_path)
        first = ledger.append({"kind": "one"})
        second = ledger.append({"kind": "two"})
        self.assertIsNone(first["previous_event_hash"])
        self.assertEqual(second["previous_event_hash"], first["event_hash"])
        self.assertEqual(len([json.loads(line) for line in chain_path.read_text(encoding="utf-8").splitlines()]), 2)

    def test_settlement_cannot_exceed_reserved_maximum(self):
        reservation = self.budgets.reserve("local", "request-6", 0.01)
        with self.assertRaises(BudgetExceeded):
            self.budgets.settle(reservation, 0.02, "CALCULATED")


if __name__ == "__main__":
    unittest.main()
