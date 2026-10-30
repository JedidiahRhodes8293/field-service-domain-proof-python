from typing import Any, Dict

from .field_models import DomainProofRequest, OnboardingResult
from .infrai_client import InfraiClient


class FieldOpsService:
    def __init__(self, infrai: InfraiClient):
        self.infrai = infrai

    def complete_onboarding(self, request: DomainProofRequest) -> OnboardingResult:
        zone = self.infrai.dns_domain_get(request.company_domain)
        zone_id = self._extract_zone_id(zone)

        self.infrai.dns_record_upsert(
            zone_id=zone_id,
            record_type="TXT",
            name=request.proof_record_name,
            content=request.proof_record_value,
        )

        verification = self.infrai.dns_domain_verify(request.company_domain)
        verified = bool(verification.get("verified"))

        follow_up = self._follow_up_action(
            dispatch_status=request.work_order.dispatch_status,
            photo_count=len(request.work_order.photos),
        )
        onboarding_status = "ready_for_dispatch_followup" if verified else "pending_domain_proof"

        coordinator = self.infrai.auth_user_get_by_email(str(request.coordinator_email)) if verified else None
        coordinator_user_id = self._extract_user_id(coordinator) if coordinator else None

        return OnboardingResult(
            company_domain=request.company_domain,
            zone_id=zone_id,
            verification_record_name=request.proof_record_name,
            verification_record_value=request.proof_record_value,
            domain_verified=verified,
            onboarding_status=onboarding_status,
            dispatch_status=request.work_order.dispatch_status,
            technician_follow_up=follow_up if verified else "wait_for_completion",
            coordinator_user_id=coordinator_user_id,
            coordinator_email=request.coordinator_email,
        )

    @staticmethod
    def _follow_up_action(*, dispatch_status: str, photo_count: int) -> str:
        if dispatch_status != "completed":
            return "wait_for_completion"
        if photo_count == 0:
            return "request_job_photos"
        return "call_customer_with_photos"

    @staticmethod
    def _extract_zone_id(zone: Dict[str, Any]) -> str:
        zone_id = zone.get("zone_id") or zone.get("id")
        if not zone_id:
            raise ValueError("zone_id missing from domain lookup")
        return str(zone_id)

    @staticmethod
    def _extract_user_id(user: Dict[str, Any]) -> str:
        user_id = user.get("user_id") or user.get("id")
        if not user_id:
            raise ValueError("user id missing from user lookup")
        return str(user_id)


def complete_onboarding(request: DomainProofRequest) -> OnboardingResult:
    infrai = InfraiClient()
    service = FieldOpsService(infrai)
    return service.complete_onboarding(request)
