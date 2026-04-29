from datetime import date, datetime


############
# CAMPS SENSIBLES
############
SENSITIVE_FIELDS = (
	'dni',
	'telefon',
	'telefon2',
	'email',
	'email_intern',
	'data_naixement',
)


############
# ROLS AMB ACCÉS COMPLET
############
FULL_ACCESS_ROLES = {
	'hosp_admin',
	'administrador',
	'rol_administrador',
}


############
# CONTROL D'ACCÉS
############
def can_view_full_data(role_name):
	if role_name is None:
		return False
	return str(role_name).strip().lower() in FULL_ACCESS_ROLES


############
# MASKING PER CAMP
############
def mask_dni(value):
	text = str(value or '').strip()
	if not text or len(text) <= 4:
		return '*' * len(text) if text else value
	return text[:2] + '*' * (len(text) - 4) + text[-2:]


def mask_phone(value):
	text = str(value or '').strip()
	if not text or len(text) <= 5:
		return '*' * len(text) if text else value
	return text[:3] + '*' * (len(text) - 5) + text[-2:]


def mask_email(value):
	text = str(value or '').strip()
	if not text:
		return value
	if '@' not in text:
		return text[:2] + '***' if len(text) > 2 else '***'
	local_part, domain_part = text.split('@', 1)
	if not local_part:
		return '*@' + domain_part
	return local_part[0] + '***@' + domain_part


def mask_date(value):
	if value is None:
		return value
	return '****-**-**'


def mask_value(field_name, value):
	field = str(field_name or '').strip().lower()

	if field == 'dni':
		return mask_dni(value)

	if field in ('telefon', 'telefon2'):
		return mask_phone(value)

	if field in ('email', 'email_intern'):
		return mask_email(value)

	if field == 'data_naixement':
		return mask_date(value)

	return value


############
# MASKING DE REGISTRES
############
def mask_personal_data(data, role_name=None, fields=None):
	if data is None:
		return data

	if can_view_full_data(role_name):
		return dict(data) if isinstance(data, dict) else data

	fields_to_mask = fields or SENSITIVE_FIELDS
	masked_data = dict(data) if isinstance(data, dict) else data

	if not isinstance(masked_data, dict):
		return masked_data

	for field in fields_to_mask:
		if field in masked_data:
			masked_data[field] = mask_value(field, masked_data[field])

	return masked_data


def mask_personal_list(rows, role_name=None, fields=None):
	if rows is None:
		return rows

	if can_view_full_data(role_name):
		return list(rows)

	return [mask_personal_data(row, role_name=role_name, fields=fields) for row in rows]


############
# MASKING RECURSIU DE PAYLOAD
############
def mask_payload(payload, role_name):
	if can_view_full_data(role_name):
		return payload

	if isinstance(payload, dict):
		result = {}
		for key, value in payload.items():
			if isinstance(value, (dict, list)):
				result[key] = mask_payload(value, role_name)
			else:
				result[key] = mask_value(key, value)
		return result

	if isinstance(payload, list):
		return [mask_payload(item, role_name) for item in payload]

	return payload

