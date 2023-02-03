from core.database.db import Wallet_db as w_db
from ..schemas.walletSchemas import WalletSchema
from fastapi import HTTPException, status


def  create_wallet_func(wallet: WalletSchema):
    result = w_db.insert_one(wallet.dict())
    exist = w_db.find_one({"_id":result.inserted_id})
    if exist:
        return True
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error wallet creating")
