![Spotlike](assets/spotlike.svg)

#### a bot to ameliorate your Spotify experience

----
Note:

If the description seems too generic, is just because at the moment
I don't know what the bot is going to do :)

Trust me - it's going to be awesome

----

At the moment this is a CLI interface, it will launch a bot that does
magic with your Spotify account.

If you install it via pip - you'll get a `spotlite` command.

Let's start with the first feature: creating a playlist with all
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
a full but slow sync - or a fast one that just check for recent additions. 

...

That's it - it will show you a few of your songs, but stay tuned:
the magic still has to come.

### Roadmap

If you find yourself doing repetitive chores in Spotify, or you have an
idea that will save the humanity tons of hour so we can all move to a beach
sipping Mojitos, write me [in the suggestion box](mailto://dariosky@gmail.com)!

Here a few things I'll be working on (in this order):

* Automatically like (or add to a playlist) the songs you're listening to the most
* Multi-user support - ATM it links with a Spotify account, and it will be
  bonded to it for the rest of it's life
* Add a web-interface to this bot: you can always run it on your box, but if
  I host it for you, you don't have to create a SpotifyApp and keep your computer
  on checking your account to do its magic
* Warn whenever you like two songs with the same name and duration (to me it happens often
  I like a song in the original album, and again in a collection)
