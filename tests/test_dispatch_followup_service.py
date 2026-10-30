from field_ops_onboarding.dispatch_followup_service import FieldOpsService
from field_ops_onboarding.field_models import DomainProofRequest, WorkOrder, WorkOrderPhoto


class StubInfraiClient:
    def __init__(self):
        self.upsert_calls = []

    def dns_domain_get(self, domain: str):
        return {"zone_id": "zone_123", "domain": domain}

    def dns_record_upsert(self, zone_id: str, record_type: str, name: str, content: str, ttl: int = 300):
        self.upsert_calls.append(
            {
                "zone_id": zone_id,
                "record_type": record_type,
                "name": name,
                "content": content,
                "ttl": ttl,
            }
        )
        return {"record_id": "rec_123"}

    def dns_domain_verify(self, domain: str):
        return {"verified": True, "domain": domain}

    def auth_user_get_by_email(self, email: str):
        return {"user_id": "user_55", "email": email}


def test_completed_work_order_with_photos_becomes_ready_for_dispatch_followup():
    service = FieldOpsService(StubInfraiClient())
    request = DomainProofRequest(
        company_domain="ops.example.com",
        proof_record_name="_cutover-proof",
        proof_record_value="txt-ownership-123",
        coordinator_email="dispatch@ops.example.com",
        work_order=WorkOrder(
            work_order_id="WO-9",
            dispatch_status="completed",
            technician_name="Sam",
            technician_note="Photos attached.",
            photos=[
                WorkOrderPhoto(photo_url="https://img.example.com/1.jpg"),
                WorkOrderPhoto(photo_url="https://img.example.com/2.jpg"),
            ],
        ),
    )

    result = service.complete_onboarding(request)

    assert result.domain_verified is True
    assert result.onboarding_status == "ready_for_dispatch_followup"
    assert result.technician_follow_up == "call_customer_with_photos"
    assert result.coordinator_user_id == "user_55"
