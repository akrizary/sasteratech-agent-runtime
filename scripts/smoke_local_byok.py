"""One bounded READ_ONLY DeepSeek smoke call using a Credential Manager entry.

The process-scoped environment assignment is only for Pydantic AI's current
DeepSeek provider integration. It is removed before the command exits.
"""
import argparse
import asyncio
import os
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sasteratech_runtime.local_control import AuditLedger, BudgetLedger, KillSwitchStore, LocalProviderController, OperationMode, WindowsKeyringCredentialStore
from sasteratech_runtime.runtime_models import ModelProfile, RuntimeRequest
from sasteratech_runtime.adapters.pydantic_ai import PydanticAIRuntimeAdapter
from sasteratech_runtime.roles import Role
from sasteratech_runtime.task_packet import TaskBudget


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--credential-id", required=True)
    parser.add_argument("--max-cost-usd", type=float, default=0.01)
    args = parser.parse_args()
    if args.max_cost_usd <= 0 or args.max_cost_usd > 0.01:
        raise SystemExit("max-cost-usd must be greater than zero and no more than 0.01")

    state = ROOT / "state"
    credentials = WindowsKeyringCredentialStore(state / "local_byok_metadata.db")
    budgets = BudgetLedger(state / "local_byok_budget.db")
    switches = KillSwitchStore(state / "local_byok_switches.db")
    audit = AuditLedger(state / "local_byok_audit.jsonl")
    try:
        try:
            budgets.create_account("local-owner", 0.01)
        except Exception:
            pass  # Existing account preserves its configured hard cap.
        controller = LocalProviderController(credentials, budgets, switches, audit)
        request_id = f"local-byok-smoke-{uuid.uuid4().hex}"
        reservation_id, secret = controller.prepare(
            mode=OperationMode.READ_ONLY, provider="deepseek", model="deepseek:deepseek-flash",
            credential_id=args.credential_id, account_id="local-owner", request_id=request_id, maximum_cost_usd=args.max_cost_usd,
        )
        old_value = os.environ.get("DEEPSEEK_API_KEY")
        os.environ["DEEPSEEK_API_KEY"] = secret
        secret = ""
        try:
            request = RuntimeRequest(
                run_id=request_id, packet_id=request_id, task_id=request_id, role=Role.RESEARCHER,
                model=ModelProfile("deepseek-flash", "pydantic_ai", "deepseek:deepseek-flash"),
                prompt="Return exactly: SASTERATECH_LOCAL_BYOK_SMOKE_OK", instructions="Return only the requested token.",
                # DeepSeek's response path can exceed a tiny 32-token limit even
                # for an exact-output smoke probe. Cost remains hard-capped above.
                budget=TaskBudget(max_model_requests=1, max_tokens=512, max_seconds=30, max_cost_usd=args.max_cost_usd),
            )
            response = await PydanticAIRuntimeAdapter().run(request)
        finally:
            if old_value is None:
                os.environ.pop("DEEPSEEK_API_KEY", None)
            else:
                os.environ["DEEPSEEK_API_KEY"] = old_value
        if response.status.value != "COMPLETE" or str(response.output).strip() != "SASTERATECH_LOCAL_BYOK_SMOKE_OK":
            budgets.release(reservation_id)
            if response.error_type == "ModelAuthenticationError":
                credentials.disable(args.credential_id, "provider_authentication_failed")
            raise SystemExit(f"Smoke failed: {response.status.value}/{response.error_type or 'unexpected_output'}")
        actual = response.usage.cost_usd
        if actual is None:
            budgets.release(reservation_id)
            raise SystemExit("Smoke blocked: provider cost evidence unavailable; reservation released.")
        budgets.settle(reservation_id, actual, "PROVIDER_REPORTED")
        print(f"PASS: local BYOK smoke complete; cost_usd={actual:.8f}; raw key was not printed.")
    finally:
        credentials.close(); budgets.close(); switches.close()


if __name__ == "__main__":
    asyncio.run(main())
