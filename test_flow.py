import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'server'))

from tools import db_driver
from main import app
from flask import session

def test():
    db = db_driver.DB()
    
    # 1. Query admin and nil1
    admins = db.query(\"SELECT username FROM personal WHERE tipus_feina = 'administrador' LIMIT 1\")
    nil_info = db.query(\"SELECT tipus_feina FROM personal WHERE username = 'nil1'\")
    
    admin_user = admins[0][0] if admins else None
    nil_tipus = nil_info[0][0] if nil_info else None
    
    print(f\"Admin chosen: {admin_user}\")
    print(f\"Nil1 tipus_feina: {nil_tipus}\")
    
    client = app.test_client()
    
    # 2. Call GET /api/admin/dummy-data/status as admin
    if admin_user:
        with client.session_transaction() as sess:
            sess['username'] = admin_user
            sess['role'] = 'administrador'
        
        resp_admin = client.get('/api/admin/dummy-data/status')
        print(f\"Admin Request Status: {resp_admin.status_code}\")
        print(f\"Admin Request JSON: {resp_admin.get_data(as_text=True)}\")
    else:
        print(\"No admin user found\")

    # 3. Call GET /api/admin/dummy-data/status as nil1
    with client.session_transaction() as sess:
        sess['username'] = 'nil1'
        sess['role'] = 'metge'
    
    resp_nil = client.get('/api/admin/dummy-data/status')
    print(f\"Nil1 Request Status: {resp_nil.status_code}\")
    print(f\"Nil1 Request JSON: {resp_nil.get_data(as_text=True)}\")

if __name__ == '__main__':
    test()
