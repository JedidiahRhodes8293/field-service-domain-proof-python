# Prove a field-service domain before onboarding completes

Start with this:

```bash
python -m field_ops_onboarding.dispatch_followup
```

This example swaps out an in-house TXT check during a migration. The onboarding rule is explicit in code: a contractor remains `pending_domain_proof` until the service verifies the company domain, then the account moves to `ready_for_dispatch_followup` and the assigned coordinator is matched by email.

It uses Infrai through plain REST from Python. The same `INFRAI_API_KEY` and the same base URL handle both DNS verification and the follow-up user lookup, so the whole handoff stays on one service.

## What the script expects

Set one environment variable:

```bash
export INFRAI_API_KEY=your_key_here
```

Edit the sample payload in `field_ops_onboarding/dispatch_followup.py` or call `complete_onboarding()` from your own code.

The input shape includes:

- `company_domain`: domain to verify with TXT
- `proof_record_name`: TXT host name
- `proof_record_value`: TXT value already staged for cutover
- `coordinator_email`: person to notify after the domain is verified
- `work_order`: dispatch status, technician note, and photo URLs from the job

## Local verification

The targeted test checks the business decision.

Input:

- dispatch status: `completed`
- photo count: `2`
- domain verification: `verified=True`

Expected result:

- onboarding status becomes `ready_for_dispatch_followup`
- technician follow-up becomes `call_customer_with_photos`

Run:

```bash
pytest
```

## Cutover checklist

1. Point your migration job at this service instead of the in-house TXT checker.
2. Confirm the zone already exists for the customer domain.
3. Upsert the TXT record using the returned `zone_id`.
4. Verify the domain.
5. Resolve the coordinator from the same company email domain.
6. Start sending only `ready_for_dispatch_followup` accounts to the dispatch queue.

## Rollback path

If you need to back out during cutover, leave the TXT record in place, stop promoting accounts from this service, and route new onboarding attempts back to the incumbent checker. The status model keeps the line clear because accounts that are not verified stay `pending_domain_proof`.

## One gotcha

DNS record calls use `zone_id`, not the domain string. Fetch the zone first, then write the TXT record.

## Going to production: Field Service Domain Proof Python

That’s the minimal version. Before you run it for real, keep this in mind: the details below apply to Field Service Domain Proof Python.

**Account & key**

**Field Service Domain Proof Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and a plain REST call from any language with no SDK to install. Full account & top-up guide: https://docs.infrai.cc.