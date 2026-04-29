import os
import requests

from .config import API_BASE_URL, API_VERIFY_TLS


# Sessió compartida que manté les cookies entre peticions (necessari per a la sessió de Flask)
_session = requests.Session()


def _request(method, path, **kwargs):
    url = API_BASE_URL.rstrip('/') + path
    kwargs.setdefault('timeout', 20)
    kwargs['verify'] = API_VERIFY_TLS
    response = _session.request(method=method, url=url, **kwargs)

    content_type = response.headers.get('Content-Type', '')
    payload = {}
    if 'application/json' in content_type:
        payload = response.json()

    if not response.ok:
        message = payload.get('error') if isinstance(payload, dict) else response.text
        raise Exception(message or f'HTTP {response.status_code}')

    if isinstance(payload, dict) and payload.get('ok') is False:
        raise Exception(payload.get('error') or 'API error')

    return payload


def login(username, password):
    return _request('POST', '/api/login', json={'username': username, 'password': password})


def logout():
    _request('POST', '/api/logout')


def register(username, password, confirm_password, id_intern):
    return _request('POST', '/api/register', json={
        'username': username,
        'password': password,
        'confirm_password': confirm_password,
        'id_intern': id_intern,
    })


def me():
    return _request('GET', '/me')


def create_patient(nom, cognom, cognom2, data_naixement, identificador):
    return _request('POST', '/api/pacients', json={
        'nom': nom,
        'cognom': cognom,
        'cognom2': cognom2,
        'data_naixement': data_naixement,
        'identificador': identificador,
    })


def create_personal(payload):
    return _request('POST', '/api/personal', json=payload)


def get_metges():
    return _request('GET', '/api/metges')


def get_pacients():
    return _request('GET', '/api/pacients')


def get_habitacions():
    return _request('GET', '/api/habitacions')


def get_visites(date_value):
    return _request('GET', '/api/informes/visites', params={'date': date_value})


def get_report(report_name, params=None):
    return _request('GET', f'/api/informes/{report_name}', params=params or {})
