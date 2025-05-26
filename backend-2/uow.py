import pymongo
from dotenv import load_dotenv
import os
import certifi
import logging
from repository import TasksRepository, UserRepository, TodoListRepository
from pymongo.mongo_client import MongoClient
from pymongo.database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Connection:
    client: MongoClient
    db: Database

    def __init__(self, client: MongoClient, db: Database) -> None:
        self.client = client
        self.db = db

class UnitOfWork:
    connection: Connection
    tasks_repository: TasksRepository
    user_repository: UserRepository
    todolist_repository: TodoListRepository

    def __init__(self) -> None:
        try:
            load_dotenv()
            mongodb_uri = os.getenv("MONGO_URI")
            db_name = os.getenv("DB_NAME", "todolist")
            
            logger.info(f"Connecting to DataBase")
            self.client = MongoClient(mongodb_uri)
            self.db = self.client[db_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to DataBase")
            
            self.connection = Connection(self.client, self.db)
            
            # Initialize repositories
            self.tasks_repository = TasksRepository(self.connection)
            self.user_repository = UserRepository(self.connection)
            self.todolist_repository = TodoListRepository(self.connection)
            
        except Exception as e:
            logger.error(f"Failed to connect to Database: {e}")
            raise

    def close(self) -> None:
        self.client.close()

    def commit_close(self) -> None:
        # For MongoDB, there's no explicit commit needed
        self.close()


