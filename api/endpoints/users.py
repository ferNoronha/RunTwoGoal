
from fastapi import APIRouter, Depends, Request, HTTPException, status, Response
from ..schemas.userSchemas import UserSchema, CreateUserSchema, UserLoginSchemma
from ..schemas.walletSchemas import WalletSchema
from ..serializers.userSerializer import userEntity, userListEntity, logginUserResponseEntity, embeddedUserResponse
from core.database.db import User_db as us
from oauth2 import require_user, AuthJWT, admin_role
from utils import hash_password, verify_password
from enumConfig import Role
from datetime import datetime, timedelta
from config import settings
from bson.objectid import ObjectId
from ..crud.walletCRUD import create_wallet_func

router = APIRouter()
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN

@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_role)], tags=["POST"])
def create_user(
    user: CreateUserSchema, 
    user_id:str = Depends(require_user)
    ):
    #verifica se existe
    exist = us.find_one({"email":user.email.lower()})
    if exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already exist")
    
    if user.password != user.password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong passwords")
    
    user.password = hash_password(user.password)
    del user.password_confirm
    try:
        if user.role is None:
            user.role = Role.admin
        else:
            # user.role = Role(user.role.lower()) pega pelo value
            user.role = str(Role[user.role.lower()].value) #pega o value pela key
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong Role")
    user.email = user.email.lower()
    user.created_at = datetime.utcnow()
    user.created_at = user.updated_at

    user.verified = False
    
    result = us.insert_one(user.dict())
    exist = us.find_one({"_id":result.inserted_id})
    if exist:
        new_wallet = WalletSchema(user_id=str(result.inserted_id),
        opening_balance = "0.00",
        balance = "0.00",
        qnt_expense = 0,
        financial_institution= "Carteira",
        qnt_transfer = 0,
        description = "Carteira",
        qnt_income= 0,
        active = True,
        created_at= datetime.utcnow(),
        updated_at= datetime.utcnow()
        )
        sucess = create_wallet_func(new_wallet)
        return {"status": "success", "message": "Adicionado"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error user creating")

@router.get("/", status_code=status.HTTP_202_ACCEPTED, tags=["GET"])
def get_users(
    limit: int = 10, 
    page: int=1, 
    search: str = '', 
    user_id:str = Depends(require_user)
    ):
    #retorna lista de usuarios
    skip = (page-1)*limit
    users = userListEntity(us.find({}).skip(skip).limit(limit))
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not found")
    return {'status': 'success', 'results': len(users), 'users': users}

@router.get("/{user_id}", tags=["GET"])
def read_user(user_id:str, user: str = Depends(require_user)):
    # if user_role == "admin":.....
    #retorna um usuario
    if not user_id:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User must be have a value")
    
    user_mg = us.find_one({"_id":ObjectId(user_id)})
    if not user_mg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not found")

    user_embed = embeddedUserResponse(user_mg)
    return {"status":"sucess", "user":user_embed}

@router.put("/{user_id}", tags=["PUT"], dependencies=[Depends(admin_role)])
def update_user(user_id:str, user:CreateUserSchema, userLogged: str = Depends(require_user)):
    #update usuario
    print(user)
    result = us.update_one({"_id":ObjectId(user_id)},{"$set",user})
    print(result)
    return {"message":"updated user"}

@router.post("/login", tags=["POST"])
def login(
    user: UserLoginSchemma,
    response: Response,
    Authorize: AuthJWT = Depends()
    ):

    exist = us.find_one({"email":user.email})
    if not exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong e-mail or password")
    
    user_entity = userEntity(exist)
    if not user_entity["active"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not active")
    
    if not verify_password(user.password,user_entity["password"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong password")
    
    #str(user_entity["id"])
    # str(logginUserResponseEntity(exist)
    access_token = Authorize.create_access_token(subject=str(user_entity["id"]),expires_time=timedelta(ACCESS_TOKEN_EXPIRES_IN))
    refresh_token = Authorize.create_refresh_token(subject=str(user_entity["id"]),expires_time=timedelta(REFRESH_TOKEN_EXPIRES_IN))

    response.set_cookie('access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('refresh_token', refresh_token, REFRESH_TOKEN_EXPIRES_IN * 60, REFRESH_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('logged_in', 'True', ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')
    

    return {'status': 'success', 'access_token': access_token, 'user':logginUserResponseEntity(exist)}

@router.get("/logout/", status_code=status.HTTP_200_OK, dependencies=[Depends(require_user)], tags=["GET"])
def logout(
    response: Response,
    Authorize: AuthJWT = Depends()
    ):

    Authorize.unset_jwt_cookies()
    response.set_cookie('logged_in','',-1)
    
    return {"status":"success"}

@router.get("/refresh/", tags=["GET"])
def refresh_token(
    response: Response,
    Authorize: AuthJWT = Depends()
    ):

    try:
        Authorize.jwt_refresh_token_required()
        user_id = Authorize.get_jwt_subject()
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not refreshed")
        
        user = userEntity(us.find_one({"_id":ObjectId(str(user_id))}))
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        access_token = Authorize.create_access_token(subject=str(user["id"]),expires_time=timedelta(ACCESS_TOKEN_EXPIRES_IN))
        
        response.set_cookie('access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
        response.set_cookie('logged_in', 'True', ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')
    
    except Exception as e:
        error = e.__class__.__name__
        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Please provide refresh token')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return {'access_token': access_token}