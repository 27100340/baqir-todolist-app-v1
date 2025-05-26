
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta
from typing import Optional, List
from queries import Getter
from uow import UnitOfWork
from commands import Command
from view_model import TaskDTO, UserDTO, TodoListDTO, TodoListWithTasksDTO, LoginRequest
from auth import (
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router: APIRouter = APIRouter()
router = APIRouter()
query_service = Getter()
command_service = Command()

#query layer apis

# @router.get("/{todolist_id}")
# def get_todolist_name(todolist_id: str):
#     uow = UnitOfWork()
#     try:
#         result = query_service.get_todolist_name(todolist_id,uow)
#         return result
#     except ValueError as e:
#         uow.close()
#         raise HTTPException(status_code=404, detail=str(e))
#     except Exception as e:
#         uow.close()
#         raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    
@router.get("/todolists/{user_id}", response_model=List[TodoListDTO])
def get_todolists_for_a_user(user_id: str):
    uow = UnitOfWork()
    try:
        result = query_service.get_all_todolists_for_user(uow, user_id)
        uow.close()
        return result
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        uow.close()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/todolists/{user_id}/all", response_model=List[TodoListWithTasksDTO])
def get_todolists_with_tasks_for_user(user_id: str):
    uow = UnitOfWork()
    try:
        result = query_service.get_all_todolists_and_tasks_for_user(uow, user_id)
        uow.close()
        return result
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/todolists/{todolist_id}/tasks", response_model=List[TaskDTO])
def get_tasks_for_todolist(todolist_id: str):
    uow = UnitOfWork()
    try:
        result = query_service.get_all_tasks_for_todolist(uow, todolist_id)
        uow.close()
        return result
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/users", response_model=List[UserDTO])
def get_all_users():
    uow = UnitOfWork()
    try:
        users = query_service.get_all_users(uow)
        
        uow.close()
        return users
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/users/{username}", response_model=UserDTO)
def get_user_by_username(username: str):
    uow = UnitOfWork()
    try:
        result = query_service.get_user_by_username(uow, username)
        uow.close()
        return result
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/tasks/{task_id}", response_model=TaskDTO)
def get_task_by_id(task_id: str):
    uow = UnitOfWork()
    try:
        result = uow.tasks_repository.get_task(task_id,None)
        uow.close()
        return result
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/tasks/{user_id}/all", response_model=List[TaskDTO])
def get_all_tasks_for_user(user_id: str):
    uow = UnitOfWork()
    try:
        result = query_service.get_all_tasks_for_user(uow, user_id)
        uow.close()
        return result
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        uow.close()
        raise HTTPException(status_code=500, detail=str(e))

    
#apis for command layer
@router.post("/users", response_model=UserDTO)
def create_user(username: str, email: str, password: str):
    uow = UnitOfWork()
    try:
        result = command_service.create_user(username, email, password, uow)
        uow.commit_close()
        return result
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        uow.close()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/users/{user_id}", response_model=UserDTO)
def update_user(
    user_id: str,
    username: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None
):
    uow = UnitOfWork()
    try:
        result = command_service.update_user(
            uow=uow,
            user_id=user_id,
            username=username or "",
            email=email or "",
            password=password or ""
        )
        uow.commit_close()
        return result
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        uow.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
def delete_user(user_id: str):
    uow = UnitOfWork()
    try:
        command_service.delete_user(user_id=user_id, uow=uow)
        uow.commit_close()
        return {"message": f"User {user_id} and all associated data deleted successfully"}
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        uow.close()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/todolists", response_model=TodoListDTO)
def create_todolist(user_id: str):
    uow = UnitOfWork()
    try:
        result = command_service.create_todolist(user_id, uow)
        uow.commit_close()
        return result
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        uow.close()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    

# @router.delete("/todolists/{todolist_id}")
# def delete_todolist_by_id(todolist_id:str)

@router.delete("/todolists/{user_id}")
def delete_todolist(user_id: str, todolist_id: Optional[str] = None):
    uow = UnitOfWork()
    try:
        command_service.delete_todolist(user_id, todolist_id, uow)
        uow.commit_close()
        if todolist_id:
            return {"message": f"Todolist {todolist_id} deleted successfully"}
        return {"message": f"All todolists for user {user_id} deleted successfully"}
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        uow.close()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/todolists/{todolist_id}/tasks", response_model=TaskDTO)
def add_task_to_todolist(
    user_id: str,
    todolist_id: str,
    title: str,
    description: str,
    priority: int
):
    uow = UnitOfWork()
    try:
        result = command_service.add_task_to_todolist(
            user_id=user_id,
            todolist_id=todolist_id,
            title=title,
            description=description,
            priority=priority,
            uow=uow
        )
        uow.commit_close()
        return result
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        uow.close()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/tasks/{task_id}", response_model=TaskDTO)
def update_task(
    task_id: str,
    todolist_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None,
    priority: Optional[int] = None
):
    uow = UnitOfWork()
    try:
        result = command_service.update_task(
            task_id=task_id,
            todolist_id=todolist_id,
            title=title,
            description=description,
            completed=completed,
            priority=priority,
            uow=uow
        )
        uow.commit_close()
        return result  # Return the TaskDTO directly
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        uow.close()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/todolists/{todolist_id}/tasks/{task_id}", response_model=TaskDTO)
def update_todolist_task( 
    todolist_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None,
    priority: Optional[int] = None
):
    uow = UnitOfWork()
    try:
        result = command_service.update_task(
            task_id=task_id,
            todolist_id=todolist_id,
            title=title,
            description=description,
            completed=completed,
            priority=priority,
            uow=uow
        )
        uow.commit_close()
        return result  # Return the TaskDTO object instead of a message
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        uow.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, todolist_id: str):
    uow = UnitOfWork()
    try:
        command_service.delete_task(
            task_id=task_id,
            todolist_id=todolist_id,
            uow=uow
        )
        uow.commit_close()
        return {"message": f"Task {task_id} deleted successfully"}
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        uow.close()
        raise HTTPException(status_code=500, detail=str(e))
    
#api to add a task to a todolist of a specific username
@router.post("/users/{username}/todolists/{todolist_id}/tasks", response_model=TaskDTO)
def add_task_to_specific_todolist_for_user(username: str, todolist_id: str, title: str, description: str, priority: int):
    uow = UnitOfWork()
    try:
        command_service.add_task_to_specific_todolist_for_user(uow, username=username, todolist_id=todolist_id, title=title, description=description, priority=priority)
        uow.commit_close()
        return {"message": f"Task {title} added to todolist {todolist_id} for user {username} successfully"}
    except ValueError as e:
        uow.close()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(login_data: LoginRequest):
    uow = UnitOfWork()
    try:
        # 1) Look up user by username
        user = query_service.get_user_by_username(uow, login_data.username)
        # 2) If user doesn't exist or password is wrong, immediately raise 401
        if not user or not verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "username": user.username
        }

    except HTTPException:
        # Re-raise 401 so FastAPI returns it as-is
        raise

    except Exception as e:
        # Any other error becomes a 500
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Always try to close the UnitOfWork, even if an exception was raised
        try:
            uow.close()
        except Exception:
            pass



@router.post("/logout")
async def logout(current_user: str = Depends(get_current_user)):
    return {"message": f"User {current_user} successfully logged out"}
