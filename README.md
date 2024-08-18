![Spotlike](src/assets/spotlike.svg)

#### Giving some 🫶 to Spotify

----
Note:

If the description seems too generic, it's because it is
- we are still defining the features :)

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

### Revamp

I am taking this side-project back after a few years from it's incubation
(during 2020 lockdown) to add the features I want and get it back to a
dev-friendly project.

Historically it started as a command-line with a few commands
then I added a VUE interface and a Flask backend - but then lockdown was over
and I didn't do much more of it (but it still work, on its hosted way).

So I want to revamp it using the tools I most love and to try something new.
I get rid of the CLI and rewrite the UI from scratch...  Stay tuned.

#### Sync your likes to a playlist
The first feature: creating a playlist with all
your liked songs (and keep it in sync) so you can share it with others.

#### Remove duplicates in you likes

It happens to all of us: you REALLY love that song - so if you see it without the heart,
you can't resist. In Spotify however the same song in different albums has different ids,
and so you end up with duplicates your carefully crafted list of likes.

Spotlike is here to help you, it will remove all the duplicate likes
(it checks for songs with same title and same duration, as the list of artists may differ).

It will keep the latest one of your likes... because you want to show the world
you like it since you were young!

## Roadmap

If you find yourself doing repetitive chores in Spotify, or you have an
idea that will save the humanity tons of hours, so we can all move to a beach
sipping Mojitos, [write me](mailto://dariosky+spotlike@gmail.com?subject=I have this great idea for Spotlike)!

Here a few things I'll be working on (in this order):

* Automatically like (or add to a playlist) the songs you are listening to the most
* More social features:
  * Recommendations based on your friends likes and listen habits
  * What about a thread of comments with your friends around a track you
    like. I'd like to have messaging in Spotify.
  
 ##### Done (see the [changelog](CHANGELOG.md))

* Remove duplicates whenever you like two songs with the same name and duration
  (it happens often to me: I like a song in the original album, and again in a collection)
* Multi-user support - the webserver joins various users sequentially
