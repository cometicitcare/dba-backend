from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List

from app.models.bhikku import Bhikku


class WorkflowFlag(str, Enum):
    """Supported status flags for the bhikku registration workflow."""

    PENDING_VERIFICATION = "Pending Verification"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PRINTED = "Printed"
    SCANNED = "Scanned"
    COMPLETED = "Completed"


@dataclass(frozen=True)
class WorkflowNotification:
    recipient_role: str
    message: str


@dataclass(frozen=True)
class WorkflowOutcome:
    result: str
    flag: WorkflowFlag
    notification: WorkflowNotification


@dataclass(frozen=True)
class WorkflowStep:
    stage: str
    action: str
    trigger: str
    flag: WorkflowFlag
    notifications: List[WorkflowNotification] = field(default_factory=list)
    details: List[str] = field(default_factory=list)
    outcomes: List[WorkflowOutcome] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": self.stage,
            "action": self.action,
            "trigger": self.trigger,
            "flag": self.flag.value,
            "details": self.details,
            "notifications": [asdict(item) for item in self.notifications],
            "outcomes": [
                {
                    "result": outcome.result,
                    "flag": outcome.flag.value,
                    "notification": asdict(outcome.notification),
                }
                for outcome in self.outcomes
            ],
        }


class BhikkuWorkflowService:
    """Encapsulates the bhikku registration workflow."""

    def build_registration_flow(self, *, bhikku: Bhikku) -> Dict[str, Any]:
        regn = getattr(bhikku, "br_regn", "") or "pending assignment"
        monk_name = getattr(bhikku, "br_gihiname", "") or "the monk"
        steps: List[WorkflowStep] = [
            WorkflowStep(
                stage="Data Entry Officer",
                action="Enter the monk's registration details into the system.",
                trigger=(
                    "Once the entry is saved, the system flags it as "
                    f"'{WorkflowFlag.PENDING_VERIFICATION.value}' and alerts the Authorizing Officer."
                ),
                flag=WorkflowFlag.PENDING_VERIFICATION,
                notifications=[
                    WorkflowNotification(
                        recipient_role="Authorizing Officer",
                        message="New data entry awaiting verification",
                    )
                ],
                details=[
                    f"Registration number: {regn}",
                    f"Monk name: {monk_name}",
                ],
            ),
            WorkflowStep(
                stage="Authorizing Officer",
                action="Review the captured data for accuracy and completeness.",
                trigger=(
                    "After verification the officer either approves the form or rejects it for corrections."
                ),
                flag=WorkflowFlag.PENDING_VERIFICATION,
                outcomes=[
                    WorkflowOutcome(
                        result="approved",
                        flag=WorkflowFlag.APPROVED,
                        notification=WorkflowNotification(
                            recipient_role="Printing Officer",
                            message="Data verified and approved. Ready for printing",
                        ),
                    ),
                    WorkflowOutcome(
                        result="rejected",
                        flag=WorkflowFlag.REJECTED,
                        notification=WorkflowNotification(
                            recipient_role="Data Entry Officer",
                            message="Entry rejected. Please correct the form.",
                        ),
                    ),
                ],
            ),
            WorkflowStep(
                stage="Printing Officer",
                action=(
                    "Print the approved form, including monk information and a QR code "
                    "linking back to the digital profile."
                ),
                trigger=(
                    "Once printing is finished, the system flags the form as "
                    f"'{WorkflowFlag.PRINTED.value}' and notifies the Scanning Officer."
                ),
                flag=WorkflowFlag.PRINTED,
                notifications=[
                    WorkflowNotification(
                        recipient_role="Scanning Officer",
                        message="Form printed. Ready for scanning",
                    )
                ],
                details=[
                    "Output includes monk's personal and temple information.",
                    "A QR code on the form links to the monk's profile in the system.",
                ],
            ),
            WorkflowStep(
                stage="Scanning Officer",
                action="Scan the printed form to create a digital image.",
                trigger=(
                    "After scanning, the system flags the form as "
                    f"'{WorkflowFlag.SCANNED.value}' and alerts the Delivery Officer."
                ),
                flag=WorkflowFlag.SCANNED,
                notifications=[
                    WorkflowNotification(
                        recipient_role="Delivery Officer",
                        message="Form scanned. Ready for delivery",
                    )
                ],
            ),
            WorkflowStep(
                stage="Delivery Officer",
                action="Deliver the final form to the monk either in person or by mail.",
                trigger=(
                    "Once delivery is confirmed the process is flagged as "
                    f"'{WorkflowFlag.COMPLETED.value}' and a final confirmation is generated."
                ),
                flag=WorkflowFlag.COMPLETED,
                notifications=[
                    WorkflowNotification(
                        recipient_role="Registry Administrators",
                        message="Form delivered. Registration process completed.",
                    )
                ],
                details=[
                    "Physical delivery or postal dispatch completes the workflow.",
                    "Final confirmation is recorded for audit purposes.",
                ],
            ),
        ]

        return {
            "registration": regn,
            "monkName": monk_name,
            "currentFlag": WorkflowFlag.PENDING_VERIFICATION.value,
            "availableFlags": [flag.value for flag in WorkflowFlag],
            "steps": [step.to_dict() for step in steps],
        }


bhikku_workflow_service = BhikkuWorkflowService()
