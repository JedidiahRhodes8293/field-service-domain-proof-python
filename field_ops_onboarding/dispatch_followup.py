from pprint import pprint

from .dispatch_followup_service import complete_onboarding
from .field_models import DomainProofRequest, WorkOrder, WorkOrderPhoto


if __name__ == "__main__":
    request = DomainProofRequest(
        company_domain="example-fieldservice.com",
        proof_record_name="_onboarding-proof",
        proof_record_value="field-service-cutover-2026-10",
        coordinator_email="dispatch@example-fieldservice.com",
        work_order=WorkOrder(
            work_order_id="WO-1842",
            dispatch_status="completed",
            technician_name="Riley Chen",
            technician_note="Replaced compressor and uploaded finish photos.",
            photos=[
                WorkOrderPhoto(photo_url="https://photos.example.com/jobs/WO-1842/1.jpg", caption="Unit before restart"),
                WorkOrderPhoto(photo_url="https://photos.example.com/jobs/WO-1842/2.jpg", caption="Unit running"),
            ],
        ),
    )

    result = complete_onboarding(request)
    pprint(result.model_dump())
