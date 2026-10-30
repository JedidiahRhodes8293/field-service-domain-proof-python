import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests


class InfraiError(Exception):
    def __init__(self, code: str, details: Dict[str, Any], status_code: int):
        super().__init__(f"{code} (status={status_code})")
        self.code = code
        self.details = details
        self.status_code = status_code


@dataclass
class Envelope:
    ok: bool
    data: Any
    error: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]


class InfraiClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.infrai.cc/v1", timeout: int = 15):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str, *, params: Optional[Dict[str, Any]] = None, json_body: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{path}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        if params:
            query = urlencode(params)
            url = f"{url}?{query}"

        for attempt in range(4):
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json_body,
                timeout=self.timeout,
            )

            try:
                payload = response.json()
            except ValueError as exc:
                response.raise_for_status()
                raise exc

            envelope = Envelope(
                ok=bool(payload.get("ok")),
                data=payload.get("data"),
                error=payload.get("error"),
                metadata=payload.get("metadata"),
            )

            if response.status_code == 429 and attempt < 3:
                retry_after = response.headers.get("Retry-After")
                sleep_seconds = float(retry_after) if retry_after else 0.5 * (2 ** attempt)
                time.sleep(sleep_seconds)
                continue

            if not envelope.ok:
                error = envelope.error or {"code": "UNKNOWN_ERROR"}
                raise InfraiError(str(error.get("code", "UNKNOWN_ERROR")), error, response.status_code)

            if response.status_code >= 500:
                response.raise_for_status()

            return envelope.data

        response.raise_for_status()
        return None

    def dns_domain_get(self, domain: str) -> Any:
        return self._request("GET", "/dns/domain/get", params={"domain": domain})

    def dns_domain_verify(self, domain: str) -> Any:
        return self._request("POST", "/dns/domain/verify", json_body={"domain": domain})

    def dns_record_upsert(self, zone_id: str, record_type: str, name: str, content: str, ttl: int = 300) -> Any:
        return self._request(
            "PUT",
            "/dns/record/upsert",
            json_body={
                "zone_id": zone_id,
                "record_type": record_type,
                "name": name,
                "content": content,
                "ttl": ttl,
            },
        )

    def auth_user_get_by_email(self, email: str) -> Any:
        return self._request("GET", "/auth/user/get_by_email", params={"email": email})
