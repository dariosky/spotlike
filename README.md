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
