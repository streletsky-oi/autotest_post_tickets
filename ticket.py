# models/ticket.py
from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import re


class TicketCreate(BaseModel):
    pid: Optional[str] = "0"
    title: str
    description: str
    sla_date: Optional[str] = None
    status_id: Optional[Union[str, int]] = "open"
    priority_id: Optional[int] = 2
    type_id: Optional[int] = 0
    department_id: Optional[int] = 1
    ticket_lock: Optional[bool] = False
    owner_id: Optional[int] = 0
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    followers: Optional[List[int]] = None
    create_from_user: Optional[int] = None
    custom_fields: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

    @field_validator('pid')
    @classmethod
    def validate_pid(cls, v):
        if v is not None and v != "0":
            try:
                pid_int = int(v)
                if pid_int < 0:
                    raise ValueError('pid должен быть положительным числом')
            except ValueError:
                raise ValueError('pid должен быть числом')
        return v

    @field_validator('sla_date')
    @classmethod
    def validate_sla_date(cls, v):
        if v is not None and v != "":
            try:
                # API ожидает формат DD.MM.YYYY HH:MM
                datetime.strptime(v, '%d.%m.%Y %H:%M')
            except ValueError:
                raise ValueError('sla_date должен быть в формате DD.MM.YYYY HH:MM')
        return v

    @field_validator('priority_id', 'type_id', 'department_id', 'owner_id')
    @classmethod
    def validate_positive_numbers(cls, v):
        if v is not None and v < 0:
            raise ValueError('Значение должно быть положительным числом')
        return v

    @field_validator('title', 'description')
    @classmethod
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Поле является обязательным')
        return v.strip()