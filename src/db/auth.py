import datetime
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel, JSON, Column

from db.common import CamelModel


class User(SQLModel, CamelModel, table=True):
    __tablename__ = "user"

    id: str = Field(primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    picture: str
    tokens: dict = Field(default_factory=dict, sa_column=Column(JSON))
    join_date: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    is_admin: bool = False

    def can_be_seen_by(self, user: "User") -> bool:
        if user.is_admin:
            return True
        # try:
        #     self.friends.where(
        #         Friendship.star == u,
        #         Friendship.fan == self,
        #         Friendship.pending is False,
        #     ).get()
        #     return True
        # except Friendship.DoesNotExist:
        #     return False

    def __str__(self):
        return f"{self.email}"


class Artist(SQLModel, CamelModel, table=True):
    __tablename__ = "artist"

    id: str = Field(primary_key=True)
    name: str
    picture: str | None


class DatePrecision(str, Enum):
    day = "day"
    month = "month"
    year = "year"


class Album(SQLModel, CamelModel, table=True):
    __tablename__ = "album"

    id: str = Field(primary_key=True)
    name: str
    picture: str | None
    release_date: datetime.date | None
    release_date_precision: DatePrecision | None

    tracks: list["Track"] = Relationship(back_populates="album")


class TrackArtist(SQLModel, CamelModel, table=True):
    __tablename__ = "trackartist"

    track_id: int | None = Field(
        default=None,
        primary_key=True,
        foreign_key="track.id",
    )
    artist_id: int | None = Field(
        default=None,
        primary_key=True,
        foreign_key="artist.id",
    )


class Track(SQLModel, CamelModel, table=True):
    __tablename__ = "track"

    id: str | None = Field(default=None, primary_key=True)
    title: str
    duration: int
    album_id: int | None = Field(default=None, foreign_key="album.id")

    album: Album | None = Relationship(back_populates="tracks")
    artists: list["Artist"] = Relationship(
        back_populates="tracks", link_model=TrackArtist
    )


class AlbumArtist(SQLModel, CamelModel, table=True):
    __tablename__ = "albumartist"

    album_id: int | None = Field(
        default=None,
        primary_key=True,
        foreign_key="album.id",
    )
    artist_id: int | None = Field(
        default=None,
        primary_key=True,
        foreign_key="artist.id",
    )


class Play(SQLModel, CamelModel, table=True):
    __tablename__ = "play"

    user_id: int | None = Field(default=None, primary_key=True, foreign_key="user.id")
    track_id: int | None = Field(default=None, primary_key=True, foreign_key="track.id")
    date: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, primary_key=True
    )


class Liked(SQLModel, CamelModel, table=True):
    __tablename__ = "liked"

    user_id: int | None = Field(default=None, primary_key=True, foreign_key="user.id")
    track_id: int | None = Field(default=None, primary_key=True, foreign_key="track.id")
    date: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, primary_key=True
    )


class Message(SQLModel, CamelModel, table=True):
    __tablename__ = "message"

    user: int | None = Field(default=None, primary_key=True, foreign_key="user.id")
    message: str
    date: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, primary_key=True
    )
    msg_type: str | None = Field(default=None)


class Friendship(SQLModel, CamelModel, table=True):
    """The friendship model is like:
    I can see just a limited profile of you
    I ask you for friendship (I become a fan)
    When you grant me the friendship - it's mutual - we both see each-other info
    """

    fan: int | None = Field(
        default=None, primary_key=True, foreign_key="user.id"
    )  # the one asking for the request
    star: int | None = Field(
        default=None, primary_key=True, foreign_key="user.id"
    )  # the one receiving the request
    pending: bool = True
