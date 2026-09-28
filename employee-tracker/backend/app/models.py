"""Pydantic request/response schemas. Storage documents are plain dicts
built in app/repo.py; these models validate what crosses the API boundary."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field

Role = Literal["SystemAdmin", "Admin", "HR", "Manager"]
AttendanceStatus = Literal["on_time", "late", "reason", "absent", "off"]


class SignupRequest(BaseModel):
    organization_name: str
    admin_name: str
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class DeleteAccountRequest(BaseModel):
    password: str


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    role: Literal["Admin", "HR", "Manager"]


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[Literal["Admin", "HR", "Manager"]] = None
    disabled: Optional[bool] = None


class LocationCreate(BaseModel):
    name: str
    address: Optional[str] = None
    latitude: float
    longitude: float
    radius_m: float = Field(gt=0)
    start_time: str
    grace_minutes: int = 0
    max_accuracy_m: float = 100.0


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_m: Optional[float] = None
    start_time: Optional[str] = None
    grace_minutes: Optional[int] = None
    max_accuracy_m: Optional[float] = None
    is_active: Optional[bool] = None


class ShiftTemplateCreate(BaseModel):
    name: str
    start_time: str
    end_time: str
    grace_minutes: int = 0
    work_days: list[int] = Field(default_factory=lambda: [1, 2, 3, 4, 5])
    color: str = "#243b8f"
    assigned_departments: list[str] = Field(default_factory=list)
    assigned_location_ids: list[str] = Field(default_factory=list)


class ShiftTemplateUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    grace_minutes: Optional[int] = None
    work_days: Optional[list[int]] = None
    color: Optional[str] = None
    assigned_departments: Optional[list[str]] = None
    assigned_location_ids: Optional[list[str]] = None


class EmployeeCreate(BaseModel):
    full_name: str
    position: Optional[str] = None
    department: Optional[str] = None
    location_id: str
    phone: Optional[str] = None
    shift_template_id: Optional[str] = None
    work_days: Optional[list[int]] = None


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    location_id: Optional[str] = None
    phone: Optional[str] = None
    shift_template_id: Optional[str] = None
    work_days: Optional[list[int]] = None
    is_active: Optional[bool] = None


class HolidayCreate(BaseModel):
    date: str
    name: str


class CheckInRequest(BaseModel):
    latitude: float
    longitude: float
    accuracy_m: float
    captured_at: datetime
    device_fingerprint: str
    mock_location_flag: bool = False


class ConsentRequest(BaseModel):
    acknowledged: bool
    full_name: str
    device_fingerprint: str


class OrganizationProvisionRequest(BaseModel):
    name: str
    admin_name: str
    admin_email: EmailStr
    admin_password: str = Field(min_length=8)
