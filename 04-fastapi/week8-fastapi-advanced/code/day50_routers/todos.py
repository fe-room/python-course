from fastapi import APIRouter

router = APIRouter(prefix="/todos", tags=["todos"])

@router.get("/")
def list_todos():
    return [{"id": 1, "title": "示例"}]

@router.post("/")
def create_todo():
    return {"id": 2, "title": "新建"}
