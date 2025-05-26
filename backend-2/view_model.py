from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import uuid
class UserDTO(BaseModel):
    """
    user DTO
    """
    id: str
    username: str
    email: str
    password: str
    created_at: datetime

    def clear_pw(self):
        self.password = ""
    

class TodoListDTO(BaseModel):
    """
    to-do list DTO
    """
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    def ___init__(self, user_id: str):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.created_at = datetime.now()
        self.updated_at = None

class TaskDTO(BaseModel):
    """
    task DTO
    """
    id: str
    todolist_id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    priority: Optional[int] = None
    #priority can be <= 1 the higher the number the lower the priority

    

class TodoListWithTasksDTO(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    tasks: list[TaskDTO]

class LoginRequest(BaseModel):
    username: str
    password: str

