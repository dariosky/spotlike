import atexit
import datetime

import peewee
from playhouse.sqlite_ext import JSONField

db = peewee.SqliteDatabase('spotlike.db')


class BaseModel(peewee.Model):
    class Meta:
        database = db

    def insert_or_update(self):
        if self.dirty_fields:
            saved = self.save()
            if not saved:
                self.save(force_insert=True)


class User(BaseModel):
    id = peewee.CharField(primary_key=True)
    name = peewee.CharField()
    email = peewee.CharField(unique=True, index=True)
    picture = peewee.CharField()
    tokens = JSONField()
    join_date = peewee.DateTimeField(default=datetime.datetime.utcnow)
    is_admin = peewee.BooleanField(default=False)

    def as_json(self):
        return {
            k: getattr(self, k)
            for k in ('id', 'name',
                      'email', 'picture')
        }


class Artist(BaseModel):
    id = peewee.CharField(primary_key=True)
    name = peewee.CharField()


class Track(BaseModel):
    id = peewee.CharField(primary_key=True)
    title = peewee.CharField()
    duration = peewee.IntegerField()


class TrackArtist(BaseModel):
    # a many to many relation table
    track = peewee.ForeignKeyField(Track)
    artist = peewee.ForeignKeyField(Artist)


class Play(BaseModel):
    user = peewee.ForeignKeyField(User, backref='played')
    track = peewee.ForeignKeyField(Track)
    date = peewee.DateTimeField()


class Liked(BaseModel):
    # a many to many relation table
    user = peewee.ForeignKeyField(User)
    track = peewee.ForeignKeyField(Track)
    date = peewee.DateTimeField()


class Message(BaseModel):
    user = peewee.ForeignKeyField(User)
    message = peewee.CharField()
    date = peewee.DateTimeField(default=datetime.datetime.utcnow)


def closedb():
    db.close()


def initdb():
    db.connect(reuse_if_open=True)
    db.create_tables((User,
                      Artist, Track, TrackArtist,
                      Play, Liked,
                      Message,
                      ))
    atexit.register(closedb)


if __name__ == '__main__':
    initdb()
