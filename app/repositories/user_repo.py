from app.repositories.base import BaseRepository
from app.models.user import UserAccount  # Fixed: Import from correct location


class UserRepository(BaseRepository[UserAccount]):
    def __init__(self):
        super().__init__(UserAccount)