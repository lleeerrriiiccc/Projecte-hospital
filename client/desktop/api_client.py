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


def _download(path, params=None):
    url = API_BASE_URL.rstrip('/') + path
    response = _session.request(
        method='GET',
        url=url,
        params=params or {},
        timeout=20,
        verify=API_VERIFY_TLS,
    )

    payload = {}
    content_type = response.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        try:
            payload = response.json()
        except ValueError:
            payload = {}

    if not response.ok:
        message = payload.get('error') if isinstance(payload, dict) else response.text
        raise Exception(message or f'HTTP {response.status_code}')

    if isinstance(payload, dict) and payload.get('ok') is False:
        raise Exception(payload.get('error') or 'API error')

    return response.content


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


def generate_dummy_data():
    return _request('POST', '/api/admin/dummy-data/generate')


def delete_dummy_data():
    return _request('POST', '/api/admin/dummy-data/delete')


def get_dummy_data_status():
    payload = _request('GET', '/api/admin/dummy-data/status')
    if isinstance(payload, dict):
        return payload.get('status', {})
    return {}


def validate_dummy_data():
    payload = _request('GET', '/api/admin/dummy-data/validate')
    if isinstance(payload, dict):
        return payload.get('validation', {})
    return {}


def get_metges():
    return _request('GET', '/api/metges')


def get_pacients():
    return _request('GET', '/api/pacients')


def get_habitacions():
    return _request('GET', '/api/habitacions')


def get_visites(date_value=None, end_date=None):
    params = {}
    if date_value and end_date:
        params = {'start_date': date_value, 'end_date': end_date}
    elif date_value:
        params = {'date': date_value}
    return _request('GET', '/api/informes/visites', params=params)


def get_planta_report():
    return _request('GET', '/api/informes/planta')


def get_personal_report():
    return _request('GET', '/api/informes/personal')


def get_malalties_report():
    return _request('GET', '/api/informes/malalties')


def get_ranking_metges_report():
    return _request('GET', '/api/informes/ranking_metges')


def get_visites_dia(date_value=None):
    params = {}
    if date_value:
        params = {'date': date_value}
    return _request('GET', '/api/informes/visites_dia', params=params)


def get_report(report_name, params=None):
    return _request('GET', f'/api/informes/{report_name}', params=params or {})


def download_visites_export(export_format, start_date=None, end_date=None):
    params = {}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    return _download(f'/api/exportacions/visites/{export_format}', params=params)


def download_visites_schema(schema_format):
    return _download(f'/api/exportacions/visites/schema/{schema_format}')
