# Crypto Router - Encryption and Decryption
from fastapi import APIRouter, HTTPException, Depends
from app.schemas import CryptoEncryptRequest, CryptoDecryptRequest, CryptoResponse
from app.services.crypto_service import get_crypto_service
from app.config import get_settings
from app.database import get_session
from app.models import SimulationLog

router = APIRouter(prefix="/api/crypto", tags=["Cryptography"])


def get_crypto():
    settings = get_settings()
    return get_crypto_service(settings.CRYPTO_KEY)


@router.post("/encrypt", response_model=CryptoResponse)
async def encrypt_payload(
    request: CryptoEncryptRequest, crypto=Depends(get_crypto)
):
    """
    Encrypt a payload using Fernet symmetric encryption.
    All data in the Matrix must be secured.
    """
    try:
        encrypted = crypto.encrypt(request.payload)

        # Log to database
        session = next(get_session())
        log_entry = SimulationLog(
            module="crypto",
            action="encrypt",
            details={"key_name": request.key_name, "payload_length": len(request.payload)},
            status="success",
        )
        session.add(log_entry)
        session.commit()

        return CryptoResponse(result=encrypted, algorithm="Fernet")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")


@router.post("/decrypt", response_model=CryptoResponse)
async def decrypt_payload(
    request: CryptoDecryptRequest, crypto=Depends(get_crypto)
):
    """
    Decrypt an encrypted payload using Fernet.
    Access the true form of the data.
    """
    try:
        decrypted = crypto.decrypt(request.encrypted_data)

        # Log to database
        session = next(get_session())
        log_entry = SimulationLog(
            module="crypto",
            action="decrypt",
            details={"key_name": request.key_name},
            status="success",
        )
        session.add(log_entry)
        session.commit()

        return CryptoResponse(result=decrypted, algorithm="Fernet")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")


@router.get("/validate/{token}")
async def validate_token(token: str, crypto=Depends(get_crypto)):
    """Validate if a token is a valid Fernet token"""
    is_valid = crypto.validate_token(token)
    return {"valid": is_valid, "algorithm": "Fernet"}
