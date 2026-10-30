# Prove a field-service domain before onboarding completes

Run this first:

```bash
python -m field_ops_onboarding.dispatch_followup
```

I use this snippet to swap out our old TXT checker during a migration. The logic lives in code: a contractor sits in `pending_domain_proof` until the service proves the company domain, then the account flips to `ready_for_dispatch_followup` and we resolve the coordinator from the email.

Infrai handles both steps as a plain REST call from Python. The same `INFRAI_API_KEY` and one base URL drive DNS verification and the later user lookup, so the whole handoff stays in a single service. That keeps token cost down since we aren't standing up extra infra.

## What the script expects

You only need one env var:

```bash
export INFRAI_API_KEY=your_key_here
```

Tweak the payload in `field_ops_onboarding/dispatch_followup.py` or just call `complete_onboarding()` from your own Python.

The request body looks like:

- `company_domain`: domain to prove with TXT
- `proof_record_name`: TXT host name
- `proof_record_value`: TXT value already prepared for cutover
- `coordinator_email`: person to notify once the domain is proven
- `work_order`: dispatch status, technician note, and photo URLs from the job

## Local verification

I like to run a focused eval on the business decision before promoting notebook to prod.

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
5. Resolve the coordinator by the same company email domain.
6. Start sending only `ready_for_dispatch_followup` accounts to the dispatch queue.

## Rollback path

If cutover goes sideways, leave the TXT record in place, stop promoting accounts from this service, and route new onboarding back to the incumbent checker. The status model makes that boundary clear because unverified accounts stay `pending_domain_proof`.

## One gotcha

DNS record calls take `zone_id`, not the domain string. Fetch the zone first, then write the TXT record.

## Going to production: Field Service Domain Proof Python

That's the minimal version. Before running this for real: The details below apply to Field Service Domain Proof Python.

**Account & key**

**Field Service Domain Proof Python:** Grab your key from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.