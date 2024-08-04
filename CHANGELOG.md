# Changelog

## v2.0.0 - let's go back - 31 Jul 2024

It has been a long time. The server has been running for 4 years but feature-wise
there have been no juicy new feature. Getting my hands here again, I'd like to change
many things - other than the Spotipy integration, that is nice - I'd like to change
a few things, mostly because I'm more used to them:
* on the backend FastAPI rather than Flask
* sqlmodel rather than peewee
* NiceGUI rather than Vue (it was nice but that was still v2)
* Other than that: new standards, tests everything and easier dev-xp


## v0.0.1 - still a CLI sprout - 20 Aug 2020

### Added

* First version - using [Click](https://click.palletsprojects.com/) to have a CLI and [Spotipy](https://github.com/plamere/spotipy/) to access [Spotify](https://developer.spotify.com/) APIs
* the `sync` command to sync your likes to a playlist (it can be either `fast` or `full`, 
  where the full version sync the unlikes and check older tracks, but takes a little longer)
* the `remove-duplicates` command to unlike the duplicate versions of
  the same songs
