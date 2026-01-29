from __future__ import annotations  # used to defer the evaluation of type annotations until runtime, allowing you to use type hints for classes or functions that are defined later in the code or in a module that would otherwise cause an error
from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel, Text


class SnippetCollaboratorLink(SQLModel, table=True):  # 6 (importance order -- reordered for type primacy)
    snippet_id: Optional[int] = Field(default=None, foreign_key="snippet.id", primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    role: str = Field(default="editor")  # Role


class SnippetTagLink(SQLModel, table=True):  # 7
    snippet_id: Optional[int] = Field(default=None, foreign_key="snippet.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)


class User(SQLModel, table=True):  # 2
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: Optional[str] = None
    hashed_password: str
    # TODO: avatar_url: Optional[str] = None

    # snippets_created: List["Snippet"] = Relationship(back_populates="created_by")
    ## snippets_created: List["Snippet"] = Relationship(
    ##     sa_relationship_kwargs={"primaryjoin": "Snippet.created_by_id==User.id"} )

    # assigned_tasks: List["Task"] = Relationship(back_populates="assignee")
    # collaborations: List["Snippet"] = Relationship(back_populates="collaborators", 
    #    link_model=SnippetCollaboratorLink)
    ## TODO: maybe add:: custom_date_stamp: str = r'%d/%m/%Y'  # // '%Y-%m-%d' etc
    ## custom_body_preview: float = 4.0


class Tag(SQLModel, table=True):  # 4
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    value: Optional[str] = None
    is_number: Optional[bool] = False
    # snippets: List["Snippet"] = Relationship(back_populates="tags", link_model=SnippetTagLink)


class Task(SQLModel, table=True):  # 3
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    is_done: bool = False

    parent_id: Optional[int] = Field(default=None, foreign_key="task.id")  # for sub-tasks recursiveness
    #sub_tasks: List["Task"] = Relationship(back_populates="parent_task")
    #parent_task: Optional["Task"] = Relationship(back_populates="sub_tasks", 
    #    sa_relationship_kwargs={"remote_side": "Task.id"} )

    #snippet_id: Optional[int] = Field(default=None, foreign_key="snippet.id")
    #snippet: Optional["Snippet"] = Relationship(back_populates="tasks")
    #assignee_id: Optional[int] = Field(default=None, foreign_key="user.id")
    #assignee: Optional[User] = Relationship()
    #assignee: Optional[User] = Relationship(back_populates="assigned_tasks")


class Snippet(SQLModel, table=True):  # 1
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    body: str

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    created_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    # created_by: Optional[User] = Relationship(back_populates="snippets_created")
    #created_by: Optional[User] = Relationship(
    #    sa_relationship_kwargs={"primaryjoin": "Snippet.created_by_id==User.id", "lazy": "joined"} )
    
    updated_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    #updated_by: Optional[User] = Relationship(
    #    sa_relationship_kwargs={"primaryjoin": "Snippet.updated_by_id==User.id"} )

    #tasks: List[Task] = Relationship(back_populates="snippet", 
    #    sa_relationship_kwargs={"cascade": "all, delete-orphan"} )
    #tags: List[Tag] = Relationship(link_model=SnippetTagLink)
    #collaborators: List[User] = Relationship(link_model=SnippetCollaboratorLink)
    #tags: List[Tag] = Relationship(back_populates="snippets", link_model=SnippetTagLink)
    #collaborators: List[User] = Relationship(back_populates="collaborations", link_model=SnippetCollaboratorLink)
    #history: List["SnippetHistory"] = Relationship(back_populates="snippet")


# class SnippetHistory(SQLModel, table=True):  # 5
#     """
#     Full (with all metadata) Snippet Markdown Version.
#     Immutable. Each new different save is kept here.
#     """
#     id: Optional[int] = Field(default=None, primary_key=True)
#     full_markdown: str = Field(sa_type=Text)  # full_markdown: str = Field(sa_column_kwargs={"type_": Text})
#     diff_summary: Optional[str] = None  # Optional: "+2 lines, 1 task done"
#     captured_at: datetime = Field(default_factory=datetime.utcnow)
#     changed_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
#     snippet_id: int = Field(foreign_key="snippet.id")
#     snippet: Snippet = Relationship(back_populates="history")
