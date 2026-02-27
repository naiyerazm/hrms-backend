from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from utils.constants import *
from utils.security import *

router = APIRouter()

@router.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != API_USERNAME or form_data.password != API_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials",
        )

    token = create_access_token({"sub": API_USERNAME})
    return {"access_token": token, "token_type": "bearer"}
