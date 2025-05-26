from uow import UnitOfWork
# from model import Task, TodoList, User
from typing import List
from view_model import TaskDTO, TodoListDTO, UserDTO, TodoListWithTasksDTO


class Getter:
    def __init__(self) -> None:
        pass

    def get_all_tasks_for_user(self, uow: UnitOfWork, user_id: str) -> List[TaskDTO]:
        try:
            # First get all todolists for the user
            todolists = self.get_all_todolists_for_user(uow, user_id)
            
            # Then get all tasks for each todolist
            tasks = []
            tasks_collection = uow.connection.db["tasks"]
            
            for todolist in todolists:
                todolist_tasks = tasks_collection.find({"todolist_id": todolist.id})
                for task_raw in todolist_tasks:
                    task = TaskDTO(
                        id=str(task_raw["_id"]),
                        todolist_id=str(task_raw["todolist_id"]),
                        title=task_raw["title"],
                        description=task_raw["description"],
                        completed=task_raw["completed"],
                        priority=task_raw["priority"],
                        created_at=task_raw["created_at"],
                        updated_at=task_raw.get("updated_at")
                    )
                    tasks.append(task)
            
            if not tasks:
                return []
            
            return tasks
        except Exception as e:
            raise ValueError(f"Error getting tasks for user {user_id}: {e}")

    def get_all_tasks_for_todolist(self, uow: UnitOfWork, todolist_id: str) -> List[TaskDTO]:
        current_collection = uow.connection.db["tasks"]
        tasks_raw = current_collection.find({"todolist_id": todolist_id})

        tasks = []
        for task_raw in tasks_raw:
            task = TaskDTO(
                id=str(task_raw["_id"]),
                todolist_id=str(task_raw["todolist_id"]),
                title=task_raw["title"],
                description=task_raw["description"],
                completed=task_raw["completed"],
                priority=task_raw["priority"],
                created_at=task_raw["created_at"],
                updated_at=task_raw.get("updated_at")
            )
            tasks.append(task)

        if not tasks:
            raise ValueError(f"No tasks found for todolist id {todolist_id}")
        return tasks

    def get_all_users(self, uow: UnitOfWork) -> List[UserDTO]:
        current_collection = uow.connection.db["users"]
        users_raw = current_collection.find()

        users = []
        for user_raw in users_raw:
            user = UserDTO(
                id=str(user_raw["_id"]),
                username=user_raw["username"],
                email=user_raw["email"],
                password=user_raw["password"],
                created_at=user_raw["created_at"]
            )
            users.append(user)

        if not users:
            raise ValueError("No users found")
        return users

    def get_all_todolists_for_user(self, uow: UnitOfWork, user_id: str) -> List[TodoListDTO]:
        try:
            # Get collection
            current_collection = uow.connection.db["todolists"]
            collection_list =  uow.connection.db.list_collections()
            collection_list = [collection["name"] for collection in collection_list]
            print(collection_list)
            
            # Convert string ID to match MongoDB format if needed
            # user_id_query = str(user_id)
            print(f"User ID: {user_id}")
            # Find all todolists for user
            todolists_raw = current_collection.find({"user_id": user_id})
            # print(f"Raw todolists data: {todolists_raw}")
            # Convert cursor to list
            todolists_raw = list(todolists_raw)
            print(f"Converted todolists data: {todolists_raw}")
            
            # If no todolists found, return empty list instead of raising error
            if not todolists_raw:
                return []
            
            # Convert to DTOs
            todolists = []
            for todolist_raw in todolists_raw:
                try:
                    todolist = TodoListDTO(
                        id=str(todolist_raw["_id"]),
                        user_id=str(todolist_raw["user_id"]),
                        created_at=todolist_raw["created_at"],
                        updated_at=todolist_raw.get("updated_at")
                    )
                    todolists.append(todolist)
                except KeyError as e:
                    # Log malformed todolist but continue processing others
                    print(f"Malformed todolist data: {e}")
                    continue
                    
            return todolists
            
        except Exception as e:
            raise ValueError(f"Error fetching todolists: {e}")

    def get_all_todolists_and_tasks_for_user(self, uow: UnitOfWork, user_id: str) -> List[TodoListWithTasksDTO]:
        todolists = self.get_all_todolists_for_user(uow, user_id)
        response = []

        for todolist in todolists:
            try:
                tasks = self.get_all_tasks_for_todolist(uow, todolist.id)
            except ValueError:
                tasks = []

            todolist_with_tasks = TodoListWithTasksDTO(
                id=todolist.id,
                user_id=todolist.user_id,
                created_at=todolist.created_at,
                updated_at=todolist.updated_at,
                tasks=tasks
            )
            response.append(todolist_with_tasks)

        return response

    def get_task_by_title(self, uow: UnitOfWork, title: str) -> TaskDTO:
        try:
            current_collection = uow.connection.db["tasks"]
            print(f"Searching for task with title: {title}")
            
            # Get all tasks and check each one (case-insensitive)
            tasks_raw = current_collection.find({})
            matching_tasks = []
            
            for task in tasks_raw:
                if task.get("title", "").lower() == title.lower():
                    matching_tasks.append(task)
                    
            if not matching_tasks:
                raise ValueError(f"No task found with title '{title}'")
                
            # Return the first matching task
            task_raw = matching_tasks[0]
            
            return TaskDTO(
                id=str(task_raw["_id"]),
                todolist_id=str(task_raw["todolist_id"]),
                title=task_raw["title"],
                description=task_raw["description"],
                completed=task_raw["completed"],
                priority=task_raw["priority"],
                created_at=task_raw["created_at"],
                updated_at=task_raw.get("updated_at")
            )
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Error getting task by title: {e}")

    def get_user_by_username(self, uow: UnitOfWork, username: str) -> UserDTO:
        current_collection = uow.connection.db["users"]
        user_raw = current_collection.find_one({"username": username})
        if not user_raw:
            raise ValueError(f"No user found with username {username}")
        user = UserDTO(
            id=str(user_raw["_id"]),
            username=user_raw["username"],
            email=user_raw["email"],
            password=user_raw["password"],
            created_at=user_raw["created_at"]
        )
        return user

    def get_user_by_email(self, uow: UnitOfWork, email: str) -> UserDTO:
        current_collection = uow.connection.db["users"]
        user_raw = current_collection.find_one({"email": email})
        if not user_raw:
            raise ValueError(f"No user found with email {email}")
        user = UserDTO(
            id=str(user_raw["_id"]),
            username=user_raw["username"],
            email=user_raw["email"],
            password=user_raw["password"],
            created_at=user_raw["created_at"]
        )
        return user
    
    def get_todolist_name(self,todolist_id: str, uow:UnitOfWork):
        current_collection = uow.connection.db["todolists"]
        target_list = current_collection.find_one({"_id" : todolist_id})
        if not target_list:
            raise ValueError(f"No todolist exists with this ID")
        return target_list["name"]
