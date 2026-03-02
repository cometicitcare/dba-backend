"""
Background Task Service for Async Email and OTP Operations

Features:
- Async task queue for email sending
- Task retry with exponential backoff
- Task status tracking
- Graceful shutdown
- In-memory queue (can be upgraded to Celery/RQ for production)
"""

import asyncio
import logging
from typing import Callable, Any, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import deque
from threading import Thread, Lock
import time

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class BackgroundTask:
    """Background task data structure."""
    task_id: str
    task_name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class BackgroundTaskService:
    """
    Background task service for async operations.
    
    For production, consider using:
    - Celery with Redis/RabbitMQ
    - Python-RQ with Redis
    - FastAPI BackgroundTasks
    """
    
    def __init__(self, num_workers: int = 5):
        self.num_workers = num_workers
        self.task_queue = deque()
        self.tasks: Dict[str, BackgroundTask] = {}
        self._lock = Lock()
        self._running = False
        self._workers = []
        
        # Metrics
        self.metrics = {
            "tasks_submitted": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_retried": 0
        }
    
    def start(self):
        """Start the background task workers."""
        if self._running:
            logger.warning("Background task service already running")
            return
        
        self._running = True
        
        # Start worker threads
        for i in range(self.num_workers):
            worker = Thread(target=self._worker, args=(i,), daemon=True)
            worker.start()
            self._workers.append(worker)
        
        logger.info(f"Background task service started with {self.num_workers} workers")
    
    def stop(self):
        """Stop the background task workers."""
        self._running = False
        
        # Wait for workers to finish
        for worker in self._workers:
            worker.join(timeout=5)
        
        logger.info("Background task service stopped")
    
    def submit_task(
        self,
        task_name: str,
        func: Callable,
        *args,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """
        Submit a background task for execution.
        
        Args:
            task_name: Name of the task
            func: Function to execute
            args: Positional arguments
            max_retries: Maximum retry attempts
            kwargs: Keyword arguments
        
        Returns:
            str: Task ID
        """
        task_id = str(uuid.uuid4())
        
        task = BackgroundTask(
            task_id=task_id,
            task_name=task_name,
            func=func,
            args=args,
            kwargs=kwargs,
            max_retries=max_retries
        )
        
        with self._lock:
            self.task_queue.append(task)
            self.tasks[task_id] = task
            self.metrics["tasks_submitted"] += 1
        
        logger.info(f"Task submitted: {task_name} (ID: {task_id})")
        return task_id
    
    def _worker(self, worker_id: int):
        """Worker thread for processing tasks."""
        logger.info(f"Worker {worker_id} started")
        
        while self._running:
            task = None
            
            # Get task from queue
            with self._lock:
                if self.task_queue:
                    task = self.task_queue.popleft()
            
            if task:
                self._execute_task(task, worker_id)
            else:
                # No tasks, sleep briefly
                time.sleep(0.1)
        
        logger.info(f"Worker {worker_id} stopped")
    
    def _execute_task(self, task: BackgroundTask, worker_id: int):
        """Execute a background task."""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            
            logger.info(
                f"Worker {worker_id} executing task: {task.task_name} "
                f"(ID: {task.task_id}, attempt: {task.retry_count + 1})"
            )
            
            # Execute the task
            result = task.func(*task.args, **task.kwargs)
            
            # Mark as completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            
            with self._lock:
                self.metrics["tasks_completed"] += 1
            
            logger.info(f"Task completed: {task.task_name} (ID: {task.task_id})")
            
        except Exception as e:
            logger.error(
                f"Task failed: {task.task_name} (ID: {task.task_id}): {e}",
                exc_info=True
            )
            
            task.error = str(e)
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                
                # Exponential backoff
                delay = 2 ** task.retry_count
                time.sleep(delay)
                
                with self._lock:
                    self.task_queue.append(task)
                    self.metrics["tasks_retried"] += 1
                
                logger.info(
                    f"Retrying task: {task.task_name} "
                    f"(attempt {task.retry_count + 1}/{task.max_retries + 1})"
                )
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
                
                with self._lock:
                    self.metrics["tasks_failed"] += 1
                
                logger.error(
                    f"Task permanently failed after {task.max_retries} retries: "
                    f"{task.task_name} (ID: {task.task_id})"
                )
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a task."""
        with self._lock:
            task = self.tasks.get(task_id)
            
            if not task:
                return None
            
            return {
                "task_id": task.task_id,
                "task_name": task.task_name,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "retry_count": task.retry_count,
                "error": task.error
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get task service metrics."""
        with self._lock:
            return {
                **self.metrics.copy(),
                "queue_size": len(self.task_queue),
                "total_tasks": len(self.tasks)
            }
    
    def cleanup_old_tasks(self, hours: int = 24):
        """Remove task records older than specified hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        with self._lock:
            task_ids_to_remove = [
                task_id for task_id, task in self.tasks.items()
                if task.completed_at and task.completed_at < cutoff
            ]
            
            for task_id in task_ids_to_remove:
                del self.tasks[task_id]
        
        if task_ids_to_remove:
            logger.info(f"Cleaned up {len(task_ids_to_remove)} old tasks")


# Create singleton instance
background_task_service = BackgroundTaskService(num_workers=5)

# Auto-start the service
background_task_service.start()


# Helper functions for common tasks

def send_email_async(to_email: str, subject: str, html_content: str, plain_text: Optional[str] = None) -> str:
    """
    Send email asynchronously using background task service.
    
    Returns:
        str: Task ID
    """
    from app.services.email_service_v2 import email_service_v2
    
    return background_task_service.submit_task(
        task_name=f"send_email_to_{to_email}",
        func=email_service_v2.send_email,
        to_email=to_email,
        subject=subject,
        html_content=html_content,
        plain_text=plain_text,
        max_retries=3
    )


def send_otp_email_async(
    user_id: str | int,
    user_email: str,
    user_name: str,
    otp: str,
    otp_expiry_minutes: int
) -> str:
    """
    Send OTP email asynchronously.
    
    Returns:
        str: Task ID
    """
    from app.services.email_service_v2 import email_service_v2
    
    # Load template
    html_content = email_service_v2.load_template(
        "password_reset",
        user_name=user_name,
        otp=otp,
        otp_expiry=otp_expiry_minutes,
        reset_password_url="https://your-app.com/reset-password",
        support_url="https://your-app.com/support",
        privacy_url="https://your-app.com/privacy",
        terms_url="https://your-app.com/terms",
    )
    
    plain_text = (
        f"Your OTP for password reset is: {otp}. "
        f"Valid for {otp_expiry_minutes} minutes."
    )
    
    return send_email_async(
        to_email=user_email,
        subject="Password Reset Request - DBA HRMS",
        html_content=html_content,
        plain_text=plain_text
    )
