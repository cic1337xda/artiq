from pydantic import BaseModel


class SessionStartRequest(BaseModel):
    name: str
    age: int


class SessionStopRequest(BaseModel):
    session_id: int
    reps: int


class MacRequest(BaseModel):
    mac: str
