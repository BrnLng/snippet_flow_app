from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import json # Para lidar com JSON em SQLite


class Task(BaseModel):
    id: str
    text: str
    completed: bool = False

class Collaborator(BaseModel):
    id: str
    name: str
    avatarUrl: Optional[str] = None # Opcional, para simplificar

class Snippet(BaseModel):
    id: Optional[str] = None # auto ID
    title: str
    body: str
    authorId: str
    createdAt: Optional[datetime] = None # Definido no backend
    updatedAt: Optional[datetime] = None # Definido no backend
    tags: List[str] = Field(default_factory=list) # Padrão para lista vazia
    collaborators: List[Collaborator] = Field(default_factory=list)
    tasks: List[Task] = Field(default_factory=list)
