from pydantic import BaseModel, EmailStr, constr, root_validator
from datetime import datetime
from decimal import Decimal

class WalletSchema(BaseModel):
    user_id: str | None = None
    opening_balance: str | None = "0.00"
    balance: str | None = "0.00"
    qnt_expense: int | None = 0
    financial_institution: str
    qnt_transfer: int | None = 0
    description: str | None = None
    qnt_income: int | None = 0
    active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True
    
    # @root_validator
    # def set_scale(cls, values):
    #     values["opening_balance"] = values["opening_balance"].quantize(Decimal("0.00"))
    #     values["balance"] = values["balance"].quantize(Decimal("0.00"))
    #     return values