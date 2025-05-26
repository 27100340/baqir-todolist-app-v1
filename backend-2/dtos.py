from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TaskDTO(BaseModel):
    id: str
    todolist_id: str
    title: str
    description: str
    completed: bool
    priority: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserDTO(BaseModel):
    id: str
    username: str
    email: str
    password: str
    created_at: datetime

class TodoListDTO(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class TodoListWithTasksDTO(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    tasks: List[TaskDTO]

class CreateTaskDTO(BaseModel):
    todolist_id: str
    title: str
    description: str
    priority: int

class UpdateTaskDTO(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[int] = None

class CreateUserDTO(BaseModel):
    username: str
    email: str
    password: str

class UpdateUserDTO(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class CreateTodoListDTO(BaseModel):
    user_id: str

class TaskResponseDTO(BaseModel):
    message: str
    task: TaskDTO

class UserResponseDTO(BaseModel):
    message: str
    user: UserDTO

class TodoListResponseDTO(BaseModel):
    message: str
    todolist: TodoListDTO

class ErrorResponseDTO(BaseModel):
    detail: str
    status_code: int