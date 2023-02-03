
from fastapi import APIRouter, Depends, Request, HTTPException, status, Response
from ..schemas.walletSchemas import WalletSchema
# from ..serializers.walletSerializer import userEntity, userListEntity, logginUserResponseEntity, embeddedUserResponse
from oauth2 import require_user, admin_role
from enumConfig import Role
from datetime import datetime, timedelta
from config import settings
from bson.objectid import ObjectId
from ..crud.walletCRUD import create_wallet_func
router = APIRouter()



@router.post("/", status_code=status.HTTP_201_CREATED, tags=["POST"])
def create_wallet(
    wallet: WalletSchema,
    user_id: str = Depends(require_user)
    ):
    print("aqui chegou")
    wallet.user_id = user_id
    wallet.created_at = datetime.utcnow()
    sucess = create_wallet_func(wallet)    
    
    return {"sucess":"true"}

