import atexit
import datetime

import peewee
from playhouse.sqlite_ext import JSONField

db = peewee.SqliteDatabase("spotlike.db")


class BaseModel(peewee.Model):
    class Meta:
        database = db

    def get_by_any_id(self, **kwargs):
        Model = self._meta.model
        if isinstance(self._pk, tuple):
            key = {k.name: kwargs[k.name] for k in self._meta.get_primary_keys()}
            return Model.get(**key)
        else:
            return Model.get_by_id(self._pk)

    def insert_or_update(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)
        passed_fields = {field for field in kwargs}

        if self.dirty_fields:
            Model = self._meta.model
            try:
                existing = self.get_by_any_id(**kwargs)
                changed_fields = []
                for field in self.dirty_fields:
                    if (
                        getattr(existing, field.name) != getattr(self, field.name)
                        and field.name in passed_fields
                    ):
                        changed_fields.append(field)
                if changed_fields:
                    self.save(only=changed_fields)  # change only the changed fields
            except Model.DoesNotExist:
                self.save(force_insert=True)
                self._new = True
        return self


class User(BaseModel):
    id = peewee.CharField(primary_key=True)
    name = peewee.CharField()
    email = peewee.CharField(unique=True, index=True)
    picture = peewee.CharField(null=True)
    tokens = JSONField()
    join_date = peewee.DateTimeField(default=datetime.datetime.utcnow)
    is_admin = peewee.BooleanField(default=False)

    def as_json(self):
        return {k: getattr(self, k) for k in ("id", "name", "email", "picture")}

    def __str__(self):
        return f"{self.email}"


class Artist(BaseModel):
    id = peewee.CharField(primary_key=True)
    name = peewee.CharField()
    picture = peewee.CharField(null=True)


class Album(BaseModel):
    id = peewee.CharField(primary_key=True)
    name = peewee.CharField()
    picture = peewee.CharField(null=True)
    release_date = peewee.DateField(null=True)
    release_date_precision = peewee.CharField(null=True)


class Track(BaseModel):
    id = peewee.CharField(primary_key=True)
    title = peewee.CharField()
    duration = peewee.IntegerField()
    album = peewee.ForeignKeyField(Album, null=True)


class TrackArtist(BaseModel):
    # a many to many relation table
    track = peewee.ForeignKeyField(Track)
    artist = peewee.ForeignKeyField(Artist)

    class Meta:
        primary_key = peewee.CompositeKey("track", "artist")


class AlbumArtist(BaseModel):
    # a many to many relation table
    album = peewee.ForeignKeyField(Album)
    artist = peewee.ForeignKeyField(Artist)

    class Meta:
        primary_key = peewee.CompositeKey("album", "artist")


class Play(BaseModel):
    user = peewee.ForeignKeyField(User, backref="played")
    track = peewee.ForeignKeyField(Track)
    date = peewee.DateTimeField()

    class Meta:
        primary_key = peewee.CompositeKey("user", "track", "date")


class Liked(BaseModel):
    # a many to many relation table
    user = peewee.ForeignKeyField(User, backref="liked")
    track = peewee.ForeignKeyField(Track)
    date = peewee.DateTimeField()

    class Meta:
        primary_key = peewee.CompositeKey("user", "track", "date")


class Message(BaseModel):
    user = peewee.ForeignKeyField(User, backref="messages")
    message = peewee.CharField()
    date = peewee.DateTimeField(default=datetime.datetime.utcnow)
    msg_type = peewee.CharField(null=True)


def closedb():
    db.close()


def initdb():
    db.connect(reuse_if_open=True)
    db.create_tables(
        (
            User,
            Track,
            Artist,
            TrackArtist,
            Album,
            AlbumArtist,
            Play,
            Liked,
            Message,
        )
    )
    atexit.register(closedb)


if __name__ == "__main__":
    initdb()
