from model import Task, TodoList, User
from uow import UnitOfWork
from view_model import TaskDTO, UserDTO, TodoListDTO, TodoListWithTasksDTO
from typing import Optional
from datetime import datetime
import uuid
from auth import get_password_hash

class Command:
    def __init__(self) -> None:
        pass

    def create_user(self, username: str, email: str, password: str, 
                   uow: Optional[UnitOfWork] = None) -> UserDTO:
        try:
            hashed_password = get_password_hash(password)
            
            user = User(
                id=str(uuid.uuid4()),
                username=username,
                email=email,
                password=hashed_password,
                created_at=datetime.now()
            )
            
            user_dto = UserDTO(
                id=user.id,
                username=user.username,
                email=user.email,
                password=hashed_password,
                created_at=user.created_at
            )
            
            uow.user_repository.save(user_dto)
            return user_dto
        except Exception as e:
            raise ValueError(f"Error creating user: {e}")

    def update_user(self, uow: UnitOfWork, user_id: str, 
                   username: str = "", email: str = "", 
                   password: str = "") -> UserDTO:
        try:
            user_dto = uow.user_repository.get_user(user_id)
            hashed_password = get_password_hash(password)
            if not user_dto:
                raise ValueError(f"User with id {user_id} not found")
            
            if username:
                user_dto.username = username
            if email:
                user_dto.email = email
            if password:
                user_dto.password = hashed_password
                
            uow.user_repository.update(user_dto)
            return user_dto
            
        except Exception as e:
            raise ValueError(f"Error updating user: {e}")

    def delete_user(self, user_id: str, uow: UnitOfWork) -> None:
        try:

            user_dto = uow.user_repository.get_user(user_id)
            if not user_dto:
                raise ValueError(f"User with id {user_id} not found")
            
            uow.todolist_repository.delete(None, user_id)
            
            uow.user_repository.delete(user_id)
            
        except Exception as e:
            raise ValueError(f"Error deleting user: {e}")

    def create_todolist(self, user_id: str, uow: UnitOfWork) -> TodoListDTO:
        try:
            user_dto = uow.user_repository.get_user(user_id)
            if not user_dto:
                raise ValueError(f"User with id {user_id} not found")
            
            todolist_dto = TodoListDTO(
                id=str(uuid.uuid4()),
                user_id=user_id,
                created_at=datetime.now(),
                updated_at=None
            )
            
            uow.todolist_repository.save(todolist_dto)
            return todolist_dto
        except Exception as e:
            raise ValueError(f"Error creating todolist: {e}")
        
    def delete_todolist(self, user_id: str, todolist_id: Optional[str] = None, uow: Optional[UnitOfWork] = None) -> None:
        try:
            user_dto = uow.user_repository.get_user(user_id)
            if not user_dto:
                raise ValueError(f"User with id {user_id} not found")

            if todolist_id:
                todolist_dto = uow.todolist_repository.get_todolist(todolist_id, user_id)
                if not todolist_dto:
                    raise ValueError(f"Todolist with id {todolist_id} not found")
                
                uow.todolist_repository.delete(todolist_id, user_id)
            else:
                response = uow.todolist_repository.delete(None, user_id)
                print(response)
            self.delete_tasks_for_todolist(todolist_id,uow)

        except Exception as e:
            raise ValueError(f"Error deleting todolist(s): {e}")

    def add_task_to_todolist(self,user_id : str, todolist_id: str, title: str, description: str, priority: int, uow: Optional[UnitOfWork] = None) -> TaskDTO:
        try:
            todolist = uow.todolist_repository.get_todolist(todolist_id=todolist_id, user_id=user_id)
            if not todolist:
                raise ValueError(f"Todolist with id {todolist_id} not found")
                
            task_dto = TaskDTO(
                id=str(uuid.uuid4()),
                todolist_id=todolist_id,
                title=title,
                description=description,
                priority=priority,
                completed=False,
                created_at=datetime.now(),
                updated_at=None
            )
            
            uow.tasks_repository.save(task_dto)
            return task_dto
        except Exception as e:
            raise ValueError(f"Error adding task to todolist: {e}")
        
    def update_task(self, task_id: str, todolist_id: str, title: Optional[str] = None, 
                    description: Optional[str] = None, completed: Optional[bool] = None, 
                    priority: Optional[int] = None, uow: Optional[UnitOfWork] = None) -> TaskDTO:
        try:
            task = uow.tasks_repository.get_task(task_id, todolist_id)
            if not task:
                raise ValueError(f"Task with id {task_id} not found")
            
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if completed is not None:
                task.completed = completed
            if priority is not None:
                task.priority = priority
                
            task.updated_at = datetime.now()
            
            uow.tasks_repository.update(task)

            return TaskDTO(
                id=task.id,
                todolist_id=task.todolist_id,
                title=task.title,
                description=task.description,
                completed=task.completed,
                priority=task.priority,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            
        except Exception as e:
            raise ValueError(f"Error updating task: {e}")

    def delete_task(self, task_id: str, todolist_id: str, uow: Optional[UnitOfWork] = None) -> None:
        try:
            task = uow.tasks_repository.get_task(task_id, todolist_id)
            if not task:
                raise ValueError(f"Task with id {task_id} not found")
                
            uow.tasks_repository.delete(task_id)
            
        except Exception as e:
            raise ValueError(f"Error deleting task: {e}")
        
    def delete_tasks_for_todolist(self, todolist_id, uow: Optional[UnitOfWork] = None):
        try:
            if uow is None:
                raise ValueError("UnitOfWork must be provided")

            tasks_collection = uow.connection.db["tasks"]
            result = tasks_collection.delete_many({"todolist_id": todolist_id})
            return result.deleted_count

        except Exception as e:
            # Consider logging the exception here
            print(f"Error deleting tasks for todolist_id {todolist_id}: {e}")
            raise


    def add_task_to_specific_todolist_for_user(user_id: str, todolist_id: str, title: str, description: str, priority: int, uow: UnitOfWork = None):
        try:
            user = uow.user_repository.get_user(user_id)
            if not user:
                raise ValueError(f"User with id {user_id} not found")
            
            todolist = uow.todolist_repository.get_todolist(todolist_id, user.id)
            if not todolist:
                raise ValueError(f"Todolist with id {todolist_id} not found")
            
            task = Task(todolist_id=todolist_id, title=title, description=description, priority=priority)
            uow.task_repository.save(task)
        except Exception as e:
            raise ValueError(f"Error adding task to specific todolist for user: {e}")