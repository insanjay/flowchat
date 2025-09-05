from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def search_test():
    return {"message": "Search endpoint working"}
