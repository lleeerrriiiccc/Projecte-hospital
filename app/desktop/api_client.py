from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from .config import API_BASE_URL, API_VERIFY_TLS


class ApiError(Exception):
    pass


class ApiClient:
    def __init__(self, base_url: str = API_BASE_URL, verify_tls: bool = API_VERIFY_TLS):
        self.base_url = base_url.rstrip("/")
        self.verify_tls = verify_tls
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        timeout = kwargs.pop("timeout", 20)
        response = self.session.request(
            method=method,
            url=self._url(path),
            timeout=timeout,
            verify=self.verify_tls,
            **kwargs,
        )

        content_type = response.headers.get("Content-Type", "")
        payload: Dict[str, Any] = {}
        if "application/json" in content_type:
            payload = response.json()

        if not response.ok:
            message = payload.get("error") if isinstance(payload, dict) else response.text
            raise ApiError(message or f"HTTP {response.status_code}")

        if isinstance(payload, dict) and payload.get("ok") is False:
            raise ApiError(payload.get("error") or "API error")

        return payload

    def login(self, username: str, password: str) -> Dict[str, Any]:
        return self._request("POST", "/api/login", json={"username": username, "password": password})

    def register(self, username: str, password: str, confirm_password: str, id_intern: int) -> Dict[str, Any]:
        return self._request(
            "POST",
            "/api/register",
            json={
                "username": username,
                "password": password,
                "confirm_password": confirm_password,
                "id_intern": id_intern,
            },
        )

    def logout(self) -> None:
        self._request("POST", "/api/logout")

    def me(self) -> Dict[str, Any]:
        return self._request("GET", "/me")

    def create_patient(
        self,
        nom: str,
        cognom: str,
        cognom2: str,
        data_naixement: str,
        identificador: str,
    ) -> Dict[str, Any]:
        return self._request(
            "POST",
            "/api/pacients",
            json={
                "nom": nom,
                "cognom": cognom,
                "cognom2": cognom2,
                "data_naixement": data_naixement,
                "identificador": identificador,
            },
        )

    def create_personal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/api/personal", json=payload)

    def get_visites(self, date_value: str) -> Dict[str, Any]:
        return self._request("GET", "/api/informes/visites", params={"date": date_value})

    def get_metges(self) -> Dict[str, Any]:
        return self._request("GET", "/api/metges")

    def get_pacients(self) -> Dict[str, Any]:
        return self._request("GET", "/api/pacients")

    def get_habitacions(self) -> Dict[str, Any]:
        return self._request("GET", "/api/habitacions")

    def get_report(self, report_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("GET", f"/api/informes/{report_name}", params=params or {})
