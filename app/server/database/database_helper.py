def client_helper(client) -> dict:
    return {
        "id": str(client['_id']),
        "name": client['name'],
        "email": client['email'],
        "signup_date": client['signup'],
        "active_token": client['active_token'],
        "token_history_count": len(client['token_history'])
    }

def admin_helper(admin) -> dict:
    return {
        "id": str(admin['_id']),
        "name": admin['name'],
    }

def token_helper(token) -> dict:
    return {
        "id": str(token['_id']),
        "client": str(token['client']),
        "token": str(token['token']),
        "creation": str(token['creation_date']),
        "toss": str(token['toss_date']),
        "expiry": token['expiry'],
        "active": token['active']
    }

