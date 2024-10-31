from pydantic import BaseModel


class BaseTaskSchema(BaseModel):
    title: str
    description: str
    status: str
    user_id: int


class TaskSchema(BaseTaskSchema):
    id: int
