from fastapi import APIRouter

router = APIRouter()


@router.post("/")
def submit_feedback():
    return {"status": "not implemented"}
