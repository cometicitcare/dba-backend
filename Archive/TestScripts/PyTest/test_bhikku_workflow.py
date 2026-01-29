import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.models.bhikku import Bhikku
from app.services.bhikku_workflow_service import (
    WorkflowFlag,
    bhikku_workflow_service,
)


def _sample_bhikku() -> Bhikku:
    return Bhikku(
        br_regn="BH2025000001",
        br_gihiname="Ven. Soma",
    )


def test_workflow_flags_and_steps():
    workflow = bhikku_workflow_service.build_registration_flow(
        bhikku=_sample_bhikku()
    )

    assert workflow["registration"] == "BH2025000001"
    assert workflow["monkName"] == "Ven. Soma"
    assert workflow["currentFlag"] == WorkflowFlag.PENDING_VERIFICATION.value

    steps = workflow["steps"]
    assert len(steps) == 5

    data_entry = steps[0]
    assert data_entry["stage"] == "Data Entry Officer"
    assert data_entry["flag"] == WorkflowFlag.PENDING_VERIFICATION.value
    assert data_entry["notifications"][0]["message"] == "New data entry awaiting verification"

    authorizing = next(step for step in steps if step["stage"] == "Authorizing Officer")
    flags = {outcome["flag"] for outcome in authorizing["outcomes"]}
    assert WorkflowFlag.APPROVED.value in flags
    assert WorkflowFlag.REJECTED.value in flags

    final_step = steps[-1]
    assert final_step["stage"] == "Delivery Officer"
    assert final_step["flag"] == WorkflowFlag.COMPLETED.value
    assert final_step["notifications"][0]["message"].startswith("Form delivered")


def test_printing_step_mentions_qr_code():
    workflow = bhikku_workflow_service.build_registration_flow(
        bhikku=_sample_bhikku()
    )
    printing = next(step for step in workflow["steps"] if step["stage"] == "Printing Officer")
    details_blob = " ".join(printing["details"]).lower()
    assert "qr code" in details_blob
