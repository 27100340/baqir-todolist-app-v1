import pymongo
from dotenv import load_dotenv
# import os
# import certifi
# from pymongo.errors import ConnectionFailure, ConfigurationError
from model import Task, User, TodoList
from typing import Optional, Any
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from view_model import UserDTO, TaskDTO, TodoListDTO, TodoListWithTasksDTO


class TasksRepository:
    # connection
    db: Database
    collection: Collection
    client: MongoClient

    def __init__(self, connection) -> None:
        load_dotenv()
        self.connection = connection
        self.db = connection.db
        self.collection = self.db["tasks"]
        self.client = connection.client

    def get_task(self, task_id: str, todolist_id: Optional[str]) -> Task:
        """
        get a task by its id.
        """
        if not todolist_id:
            task_raw = self.collection.find_one({"_id": task_id})
        else:
            task_raw = self.collection.find_one({"_id": task_id, "todolist_id": todolist_id})
        if not task_raw:
            raise ValueError(f"Task with id {task_id}, Todolist id {todolist_id}, not found")
        task = Task(id=task_raw["_id"],
                    todolist_id=task_raw["todolist_id"],
                    title=task_raw["title"],
                    description=task_raw["description"],
                    completed=task_raw["completed"],
                    priority=task_raw["priority"],
                    created_at=task_raw["created_at"],
                    updated_at=task_raw.get("updated_at"))
        return task

    def save(self, task: Task) -> str:
        try:
            task_raw = {
                "_id": task.id,
                "todolist_id": task.todolist_id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "created_at": task.created_at,
                "updated_at": task.updated_at
            }
            result = self.collection.insert_one(task_raw)
            return result.inserted_id
        except pymongo.errors.DuplicateKeyError:
            raise ValueError(f"Task with id {task.id} already exists")
        except Exception as e:
            raise ValueError(f"Error saving task: {e}")

    def update(self, task: Task) -> bool:
        try:
            task_raw = {
                "todolist_id": task.todolist_id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "created_at": task.created_at,
                "updated_at": task.updated_at
            }
            result = self.collection.update_one(
                {"_id": task.id},
                {"$set": task_raw}
            )
            if result.matched_count == 0:
                raise ValueError(f"Task with id {task.id} not found")
            return result.modified_count > 0
        except Exception as e:
            raise ValueError(f"Error updating task: {e}")
        
    def delete(self, task_id: str):
        try:
            if not task_id:
                raise ValueError("Task id is required")
            result = self.collection.delete_one({"_id": task_id})
            if result.deleted_count == 0:
                raise ValueError(f"Task with id {task_id} not found")
            return True
        except Exception as e:
            raise ValueError(f"Error deleting task: {e}")


class UserRepository:
    db: Database
    collection: Collection
    client: MongoClient

    def __init__(self, connection: Any) -> None:
        load_dotenv()
        self.connection = connection
        self.db = connection.db
        self.collection = self.db["users"]
        self.client = connection.client

    def get_user(self, user_id: str) -> UserDTO:
        try:
            user_raw = self.collection.find_one({"_id": user_id})
            if not user_raw:
                raise ValueError(f"User with id {user_id} not found")
            return UserDTO(
                id=str(user_raw["_id"]),
                username=user_raw["username"],
                email=user_raw["email"],
                password=user_raw["password"],
                created_at=user_raw["created_at"]
            )
        except Exception as e:
            raise ValueError(f"Error getting user: {e}")

    def save(self, user_dto: UserDTO) -> str:
        try:
            # Check if user already exists by username or email
            existing_user = self.collection.find_one({
                "$or": [
                    {"username": user_dto.username},
                    {"email": user_dto.email}
                ]
            })
            if existing_user:
                raise ValueError("Username or email already exists")

            user_raw = {
                "_id": user_dto.id,
                "username": user_dto.username,
                "email": user_dto.email,
                "password": user_dto.password,
                "created_at": user_dto.created_at
            }
            result = self.collection.insert_one(user_raw)
            return str(result.inserted_id)
        except pymongo.errors.DuplicateKeyError:
            raise ValueError(f"User with id {user_dto.id} already exists")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Error saving user: {e}")
        
    def update(self, user: User):
        try:
            user_raw = {
                "username": user.username,
                "email": user.email,
                "password": user.password,
                "created_at": user.created_at
            }
            result = self.collection.update_one(
                {"_id": user.id},
                {"$set": user_raw}
            )
            if result.matched_count == 0:
                raise ValueError(f"User with id {user.id} not found")
            return result.modified_count > 0
        except Exception as e:
            raise ValueError(f"Error updating user: {e}")

    def delete(self, user_id: str) -> bool:
        try:
            result = self.collection.delete_one({"_id": user_id})
            if result.deleted_count == 0:
                raise ValueError(f"User with id {user_id} not found")
            return True
        except Exception as e:
            raise ValueError(f"Error deleting user: {e}")


class TodoListRepository:
    def __init__(self, connection):
        load_dotenv()
        self.connection = connection
        self.db = connection.db
        self.collection = self.db["todolists"]
        self.client = connection.client

    def get_todolist(self, todolist_id, user_id):
        """
        get a todolist by its id.
        """
        todolist_raw = self.collection.find_one({"_id": todolist_id, "user_id": user_id})
        if not todolist_raw:
            raise ValueError(f"Todolist with id {todolist_id}, User id {user_id}, not found")
        todolist = TodoList(id=todolist_raw["_id"],
                            user_id=todolist_raw["user_id"],
                            created_at=todolist_raw["created_at"],
                            updated_at=todolist_raw["updated_at"])
        return todolist

    def save(self, todolist):
        try:
            todolist_raw = {
                "_id": todolist.id,
                "user_id": todolist.user_id,
                "created_at": todolist.created_at,
                "updated_at": todolist.updated_at
            }
            result = self.collection.insert_one(todolist_raw)
            return result.inserted_id
        except pymongo.errors.DuplicateKeyError:
            raise ValueError(f"TodoList with id {todolist.id} already exists")
        except Exception as e:
            raise ValueError(f"Error saving todolist: {e}")

    def update(self, todolist):
        try:
            todolist_raw = {
                "user_id": todolist.user_id,
                "created_at": todolist.created_at,
                "updated_at": todolist.updated_at
            }
            result = self.collection.update_one(
                {"_id": todolist.id},
                {"$set": todolist_raw}
            )
            if result.matched_count == 0:
                raise ValueError(f"TodoList with id {todolist.id} not found")
            return result.modified_count > 0
        except Exception as e:
            raise ValueError(f"Error updating todolist: {e}")

    def delete(self, todolist_id, user_id):
        try:
            if not todolist_id:
                result = self.collection.delete_one({"user_id": user_id})
            else:
                result = self.collection.delete_one({"_id": todolist_id, "user_id": user_id})
            if result.deleted_count == 0:
                raise ValueError(f"Todolist with id {todolist_id} not found")
            return True
        except Exception as e:
            raise ValueError(f"Error deleting todolist: {e}")


