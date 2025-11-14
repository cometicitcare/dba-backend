# app/repositories/bhikku_workflow_flag_repo.py
from app.models.bhikku_workflow_flag import BhikkuWorkflowFlag
from app.repositories.base import BaseRepository


class BhikkuWorkflowFlagRepository(BaseRepository):
    """Repository for BhikkuWorkflowFlag model"""
    
    def __init__(self):
        super().__init__(BhikkuWorkflowFlag)


# Global instance
bhikku_workflow_flag_repo = BhikkuWorkflowFlagRepository()
