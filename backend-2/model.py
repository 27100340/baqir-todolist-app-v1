from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

class User(BaseModel):
    """
    user in the system.
    """
    id: str
    username: str
    email: str
    password: str
    created_at: datetime

    def create_user(self, username: str, email: str, password: str) -> None:
        """
        create a new user.
        """
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password = password
        self.created_at = datetime.now()
    
    def update_user(self, username: Optional[str] = None, 
                    email: Optional[str] = None, 
                    password: Optional[str] = None) -> None:
        """
        update user information.
        """
        if username:
            self.username = username
        if email:
            self.email = email
        if password:
            self.password = password
    
    def delete_user(self) -> None:
        """
        delete user.
        """
        self.username = None
        self.email = None
        self.password = None
        self.created_at = None
        self.id = None


class TodoList(BaseModel):
    """
    to-do list in the system.
    """
    id: str
    user_id: str = Field(unique=True)
    created_at: datetime
    updated_at: Optional[datetime] = None

    def create_todolist(self, user_id: str) -> None:
        """
        create a new to-do list.
        """
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.created_at = datetime.now()
        self.updated_at = None

    def delete_todolist(self) -> None:
        """
        delete to-do list.
        """
        self.user_id = None
        self.created_at = None
        self.updated_at = None
        self.id = None

class Task(BaseModel):
    """
    task in the system.
    """
    id: str
    todolist_id: str
    title: str
    description: str
    completed: bool
    #priority can be <= 1 the higher the number the lower the priority
    priority: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    def create_task(self, todolist_id: str, title: str, description: str, 
                    completed: bool, priority: int) -> None:
        """
        create a new task.
        """
        self.id = str(uuid.uuid4())
        self.todolist_id = todolist_id
        self.title = title
        self.description = description
        self.completed = completed
        self.priority = priority
        self.created_at = datetime.now()
        self.updated_at = None

    def update_task(self, title: Optional[str] = None, 
                    description: Optional[str] = None,
                    completed: Optional[bool] = None, 
                    priority: Optional[int] = None) -> None:
        """
        update task information.
        """
        if title:
            self.title = title
        if description:
            self.description = description
        if completed is not None:
            self.completed = completed
        if priority:
            self.priority = priority
        self.updated_at = datetime.now()

    def delete_task(self) -> None:
        """
        delete task.
        """
        self.todolist_id = None
        self.title = None
        self.description = None
        self.completed = None
        self.priority = None
        self.created_at = None
        self.updated_at = None
        self.id = None

    def mark_as_completed(self) -> None:
        """
        mark task as completed.
        """
        self.completed = True
        self.updated_at = datetime.now()

    def mark_as_incompleted(self) -> None:
        """
        mark task as incompleted.
        """
        self.completed = False
        self.updated_at = datetime.now()
