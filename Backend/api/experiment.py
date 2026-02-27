from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db import get_db
from service.experiment_service import ExperimentService

router = APIRouter(prefix="/experiment", tags=["物理实验模块"])


@router.get("/api/content-path")
def get_content_path(
    category: str = Query(...),
    title: str = Query(...),
    db: Session = Depends(get_db),
):
    try:
        if not category or not title:
            raise HTTPException(status_code=400, detail="参数缺失")
        data = ExperimentService.get_content_path_by_category_title(db, category, title)
        if not data:
            raise HTTPException(status_code=404, detail="实验不存在")
        return {"code": 200, "data": data}
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 500, "detail": str(e)},
        )


@router.get("/api/titles")
def get_titles(
    category: str = Query(...),
    db: Session = Depends(get_db),
):
    try:
        if not category:
            raise HTTPException(status_code=400, detail="参数缺失")
        titles = ExperimentService.list_titles_by_category(db, category)
        return {"code": 200, "data": titles}
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 500, "detail": str(e)},
        )
