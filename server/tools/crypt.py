import bcrypt


############
# ENCRIPT PASSWORD
############
def encrypt_password(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


############
# CHECK PASSWORD
############
def check_password(password, hashed):
    password_bytes = password.encode('utf-8')

    # Normalize the stored hash to bytes
    if isinstance(hashed, bytes):
        hashed_text = hashed.decode('utf-8', errors='ignore').strip()
    else:
        hashed_text = str(hashed).strip()

    # PostgreSQL bytea hex format: \x24326224...
    if hashed_text.startswith('\\x'):
        try:
            hashed_bytes = bytes.fromhex(hashed_text[2:])
        except ValueError:
            return False
    else:
        hashed_bytes = hashed_text.encode('utf-8')

    try:
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except ValueError:
        return False


