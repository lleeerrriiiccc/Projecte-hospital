import requests

from .config import API_BASE_URL, API_VERIFY_TLS


class ApiError(Exception):
    pass


class ApiClient:
    def __init__(self, base_url=API_BASE_URL, verify_tls=API_VERIFY_TLS):
        self.base_url = base_url.rstrip("/")
        self.verify_tls = verify_tls
        self.session = requests.Session()

    def _url(self, path):
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def _request(self, method, path, **kwargs):
        timeout = kwargs.pop("timeout", 20)
        response = self.session.request(
            method=method,
            url=self._url(path),
            timeout=timeout,
            verify=self.verify_tls,
            **kwargs,
        )

        content_type = response.headers.get("Content-Type", "")
        payload = {}
        if "application/json" in content_type:
            payload = response.json()

        if not response.ok:
            message = payload.get("error") if isinstance(payload, dict) else response.text
            raise ApiError(message or f"HTTP {response.status_code}")

        if isinstance(payload, dict) and payload.get("ok") is False:
            raise ApiError(payload.get("error") or "API error")

        return payload

    def login(self, username, password):
        return self._request("POST", "/api/login", json={"username": username, "password": password})

    def register(self, username, password, confirm_password, id_intern):
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

    def logout(self):
        self._request("POST", "/api/logout")

    def me(self):
        return self._request("GET", "/me")

    def create_patient(
        self,
        nom,
        cognom,
        cognom2,
        data_naixement,
        identificador,
    ):
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

    def create_personal(self, payload):
        return self._request("POST", "/api/personal", json=payload)

    def get_visites(self, date_value):
        return self._request("GET", "/api/informes/visites", params={"date": date_value})

    def get_metges(self):
        return self._request("GET", "/api/metges")

    def get_pacients(self):
        return self._request("GET", "/api/pacients")

    def get_habitacions(self):
        return self._request("GET", "/api/habitacions")

    def get_report(self, report_name, params=None):
        return self._request("GET", f"/api/informes/{report_name}", params=params or {})
