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
# UTILITATS BÀSIQUES
############
def _normalize_role(role_name):
	if role_name is None:
		return ''
	return str(role_name).strip().lower()


def _clean_text(value):
	if value is None:
		return ''
	return str(value).strip()


def _mask_generic(value, visible_start=2, visible_end=2, mask_char='*'):
	text = _clean_text(value)

	if not text:
		return value

	if len(text) <= visible_start + visible_end:
		return mask_char * len(text)

	masked_middle = mask_char * (len(text) - visible_start - visible_end)
	return text[:visible_start] + masked_middle + text[-visible_end:]


############
# MASKING PER CAMP
############
def mask_dni(value):
	return _mask_generic(value, visible_start=2, visible_end=2)


def mask_phone(value):
	return _mask_generic(value, visible_start=3, visible_end=2)


def mask_email(value):
	text = _clean_text(value)

	if not text:
		return value

	if '@' not in text:
		return _mask_generic(text, visible_start=2, visible_end=2)

	local_part, domain_part = text.split('@', 1)
	if not local_part:
		return '*' + '@' + domain_part

	if len(local_part) == 1:
		return local_part[0] + '***@' + domain_part

	return local_part[0] + '***@' + domain_part


def mask_date(value):
	if value is None:
		return value

	if isinstance(value, (date, datetime)):
		return '****-**-**'

	text = _clean_text(value)
	if not text:
		return value

	return '****-**-**'


def mask_value(field_name, value):
	field = _clean_text(field_name).lower()

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
# CONTROL D'ACCÉS
############
def can_view_full_data(role_name):
	return _normalize_role(role_name) in FULL_ACCESS_ROLES


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

