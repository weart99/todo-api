from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .schemas import TaskCreate, TaskUpdate, TaskResponse
from .models import TaskStatus, Task
from .database import get_db, create_tables
from .auth_routes import auth_router
from .auth_utils import get_current_user
from .auth_models import User

app: FastAPI = FastAPI(title="Todo API", version="0.1.0")
app.include_router(auth_router)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="src/todo_api/static"), name="static")
templates: Jinja2Templates = Jinja2Templates(directory="src/todo_api/templates")

# Initialize the database and create tables
create_tables()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "To Do App"}
    )


@app.get("/tasks/", response_model=list[TaskResponse])
def get_tasks(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    db_tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return db_tasks


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .filter(Task.user_id == current_user.id)
        .first()
    )
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.post("/tasks/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        user_id=current_user.id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .filter(Task.user_id == current_user.id)
        .first()
    )
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_update.title is not None:
        db_task.title = task_update.title
    if task_update.description is not None:
        db_task.description = task_update.description
    if task_update.status is not None:
        db_task.status = task_update.status

    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}", response_model=dict)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .filter(Task.user_id == current_user.id)
        .first()
    )
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(db_task)
    db.commit()
    return {"detail": "Task deleted successfully"}
