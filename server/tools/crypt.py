import bcrypt


############
# ENCRIPT PASSWORD
############
def encrypt_password(password):
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password

    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')



############
# CHECK PASSWORD
############
def check_password(password, hashed):
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password

    if isinstance(hashed, bytes):
        hashed_text = hashed.decode('utf-8', errors='ignore').strip()
    else:
        hashed_text = str(hashed).strip()

    if hashed_text.startswith('\\x'):
        hex_part = hashed_text[2:]
        try:
            hashed_bytes = bytes.fromhex(hex_part)
        except ValueError:
            return False
    elif hashed_text.startswith("b'") and hashed_text.endswith("'"):
        hashed_bytes = hashed_text[2:-1].encode('utf-8')
    elif hashed_text.startswith('b"') and hashed_text.endswith('"'):
        hashed_bytes = hashed_text[2:-1].encode('utf-8')
    else:
        hashed_bytes = hashed_text.encode('utf-8')

    try:
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except ValueError:
        return False
    

