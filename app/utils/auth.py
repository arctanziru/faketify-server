from fastapi import HTTPException, status
from functools import wraps
from typing import Callable
import inspect
from app.db.models import UserModel


def role_required(*allowed_roles: str):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, current_user: UserModel, **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires role(s): {', '.join(allowed_roles)}",
                )
            if inspect.iscoroutinefunction(func):
                return await func(*args, current_user=current_user, **kwargs)
            else:
                return func(*args, current_user=current_user, **kwargs)

        return wrapper

    return decorator
