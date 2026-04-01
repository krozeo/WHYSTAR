from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from service.outfit_service import OutfitService

router = APIRouter(prefix="/shop", tags=["虚拟物品兑换"])


@router.get("/items")
def list_outfits(db: Session = Depends(get_db)):
    return {"success": True, "data": OutfitService.list_outfits(db)}


@router.get("/user-items")
def list_user_outfits(user_id: str = Query(...), db: Session = Depends(get_db)):
    data = OutfitService.list_user_outfits(user_id, db)
    return {"success": True, "data": data}


@router.get("/current-avatar")
def current_avatar(user_id: str = Query(...), db: Session = Depends(get_db)):
    data = OutfitService.get_current_outfit(user_id, db)
    return {"success": True, "data": data}


@router.post("/redeem")
def redeem_outfit(
    user_id: str = Body(...),
    outfit_id: int = Body(...),
    db: Session = Depends(get_db),
):
    result = OutfitService.redeem_outfit(user_id, outfit_id, db)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True, "data": result}


@router.post("/equip")
def equip_outfit(
    user_id: str = Body(...),
    outfit_id: int = Body(...),
    db: Session = Depends(get_db),
):
    result = OutfitService.equip_outfit(user_id, outfit_id, db)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True, "data": result}
