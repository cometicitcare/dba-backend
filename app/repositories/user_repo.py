from app.repositories.base import BaseRepository
from app.models.user_accounts import UserAccount


class UserRepository(BaseRepository[UserAccount]):
    def __init__(self):
        super().__init__(UserAccount)