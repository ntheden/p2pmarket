from sqlmodel import SQLModel, Field, Relationship
from typing import Union, Optional


class Media(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Union[str, None]
    size: Union[int, None] # TODO
    thumb_size: Union[int, None] # TODO
    type: Union[str, None]
    path: str = Union[str, None]
    # owned by either a message or a user, but not both
    message_id: Optional[int] = Field(default=None, foreign_key="message.id")
    message: Optional["Message"] = Relationship(back_populates="media")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="media")


class Reaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    emoji: Union[str, None]
    count: int
    message_id: Optional[int] = Field(index=True, default=None, foreign_key="message.id")
    message: Optional["Message"] = Relationship(back_populates="reactions")


class HashtagMessageLink(SQLModel, table=True):
    hashtag_id: Optional[int] = Field(
        default=None, foreign_key="message.id", primary_key=True
    )
    message_id: Optional[int] = Field(
        default=None, foreign_key="hashtag.id", primary_key=True
    )


class Hashtag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True) # lower case #hashtag
    messages: Optional[list["Message"]] = Relationship(
        back_populates="hashtags",
        link_model=HashtagMessageLink
    )


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    first_name: Union[str, None]
    last_name: Union[str, None]
    username: Union[str, None]
    is_deleted: bool = False
    status: Union[str, None] # will not remain optional
    last_online_date: Union[str, None] # will not remain optional, is this str
    thumb_name: Union[str, None] # using telegram's thumb for now
    media: Optional[list["Media"]] = Relationship(back_populates="user")
    messages: Optional[list["Message"]] = Relationship(back_populates="user")


class Message(SQLModel, table=True):
    id: int = Field(primary_key=True)
    caption: str = "" # caption or text
    date: Union[str, None] # is this str
    edit_date: Union[str, None] # is this str
    is_deleted: bool = False
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="messages")
    media: Optional[list["Media"]] = Relationship(back_populates="message")
    reactions: Optional[list["Reaction"]] = Relationship(back_populates="message")
    hashtags: Optional[list[Hashtag]] = Relationship(
        back_populates="messages",
        link_model=HashtagMessageLink
    )



