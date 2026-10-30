from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


DispatchStatus = Literal["scheduled", "en_route", "completed"]
OnboardingState = Literal["pending_domain_proof", "ready_for_dispatch_followup"]
FollowUpAction = Literal["wait_for_completion", "request_job_photos", "call_customer_with_photos"]


class WorkOrderPhoto(BaseModel):
    photo_url: str
    caption: Optional[str] = None


class WorkOrder(BaseModel):
    work_order_id: str
    dispatch_status: DispatchStatus
    technician_name: str
    technician_note: str
    photos: List[WorkOrderPhoto] = Field(default_factory=list)


class DomainProofRequest(BaseModel):
    company_domain: str
    proof_record_name: str
    proof_record_value: str
    coordinator_email: EmailStr
    work_order: WorkOrder


class OnboardingResult(BaseModel):
    company_domain: str
    zone_id: str
    verification_record_name: str
    verification_record_value: str
    domain_verified: bool
    onboarding_status: OnboardingState
    dispatch_status: DispatchStatus
    technician_follow_up: FollowUpAction
    coordinator_user_id: Optional[str] = None
    coordinator_email: EmailStr
