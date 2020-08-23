# Changelog

## v0.0.1 - still a CLI sprout

### Added

* First version - using [Click](https://click.palletsprojects.com/) to have a CLI and [Spotipy](https://github.com/plamere/spotipy/) to access [Spotify](https://developer.spotify.com/) APIs
* the `sync` command to sync your likes to a playlist (it can be either `fast` or `full`, 
  where the full version sync the unlikes and check older tracks, but takes a little longer)
* the `remove-duplicates` command to unlike the duplicate versions of
  the same songs
