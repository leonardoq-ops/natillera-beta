from pydantic import BaseModel


class UploadProofResponse(BaseModel):
    success: bool
    member_code: str
    status: str
    proof_url: str
    ledger_hash: str


class VerifyProofRequest(BaseModel):
    member_code: str
    month: str
    action: str          # "VERIFICADO" | "RECHAZADO"
    admin_notes: str = ""
    ledger_hash: str      # hash of the original APORTE entry being reviewed


class VerifyProofResponse(BaseModel):
    success: bool
    member_code: str
    new_status: str
    ledger_hash: str
