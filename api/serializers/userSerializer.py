def userEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["nome"],
        "email": user["email"],
        "role": user["role"],
        "photo": user["photo"],
        "full_name": user["full_name"],
        "verified": user["verified"],
        "active":user["active"],
        "password": user["password"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"]
    }


def userResponseEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "photo": user["photo"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"]
    }


def embeddedUserResponse(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["nome"],
        "email": user["email"],
        "photo": user["photo"],
        "active": user["active"]
        
    }

def logginUserResponseEntity(user) -> dict:
    return {
        "name": user["nome"],
        "email": user["email"],
        "photo": user["photo"],
        "role": user["role"]
    }
def userRoleEntity(user) -> dict:
    return {
        "role":user["role"]
    }

def userListEntity(users) -> list:
    return [embeddedUserResponse(user) for user in users]