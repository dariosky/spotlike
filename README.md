![Spotlike](src/assets/spotlike.svg)

#### a bot to ameliorate your Spotify experience

----
Note:

If the description seems too generic, it's because it is - we are still defining the features :)

But trust me - it is going to be awesome!

----

## Use the hosted one for free
You can just sign up here for free and enjoy its benefits.
It's free, and it will always be the latest stable version.

https://spotlike.dariosky.it/

You can always run it on your box, but if  I host it for you,
you don't have to create a SpotifyApp and keep your computer
on checking your account to do its magic.

We are going to add more social features soon - for that you'll need
other users in the same server, so this is the only mode that works :)

## CLI interface

The way it started, you log in with your Spotify account, and you'll have a few
commands to manage it.

If you install it via pip - you'll get a `spotlike` command.

#### Sync your likes to a playlist
The first feature: creating a playlist with all
your liked songs (and keep it in sync) so you can share it with others.

```shell script
spotlike sync
```

The fist time you'll lunch it it will open a browser kindly asking
 for permissions to access your Spotify account, and you're set.
Like for the other commands, you can check the options with 

```shell script
spotlike sync --help
```

You can change the playlist with the likes name and choose between
a full but slow sync (default) - or a fast one that just check for recent
additions.

#### Remove duplicates in you likes

It happends to all of us: you REALLY love that song - so if you see it without the heart,
you can't resist. In Spotify however the same song in different albums has different ids,
and so you end up with duplicates your carefully crafted list of likes.

Spotlike is here to help you, it will remove all the duplicate likes
(it checks for songs with same title and same duration, as the list of artists may differ).

It will keep the latest one of your likes... cause you want to show the world you like it since
you were young! 

```shell script
spotlike remove-duplicates
```


## Roadmap

If you find yourself doing repetitive chores in Spotify, or you have an
idea that will save the humanity tons of hours, so we can all move to a beach
sipping Mojitos, [write me](mailto://dariosky+spotlike@gmail.com?subject=I have this great idea for Spotlike)!

Here a few things I'll be working on (in this order):

* Automatically like (or add to a playlist) the songs you are listening to the most
* A web interface to access your stats, artist, track views related with your tastes
* More social features:
  * Recommendations based on your friends likes and listen habits
  * What about a thread of comments with your friends around a track you
    like. I'd like to have messaging in Spotify.
  
 ##### Done (see the [changelog](CHANGELOG.md))

* Remove duplicates whenever you like two songs with the same name and duration
  (it happens often to me: I like a song in the original album, and again in a collection)
* Multi-user support - the webserver joins various users sequentially 
* Add a web-interface to this bot
