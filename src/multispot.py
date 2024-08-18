import logging
from collections import defaultdict, deque
from functools import partial
import spotipy
from spotipy import SpotifyException

scope = ",".join(
    (
        "playlist-modify-private",
        "playlist-modify-public",
        "playlist-read-private",
        "user-library-modify",
        "user-library-read",
        "user-read-email",
        "user-read-recently-played",
        "user-top-read",
    )
)

logger = logging.getLogger("spotlike.multispot")


class SpotifyConnectionException(Exception):
    pass


class StoredSpotifyOauth(spotipy.SpotifyOAuth):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.user = user
        self.token_info = None

    def get_cached_token(self):
        if not self.user:  # I have no tokens - we'll ask for them
            return self.token_info
        token_info = self.user.tokens  # get from DB
        # if scopes don't match, then bail
        if "scope" not in token_info or not self._is_scope_subset(
            self.scope, token_info["scope"]
        ):
            return None

        if self.is_token_expired(token_info):
            token_info = self.refresh_access_token(token_info["refresh_token"])
        self.token_info = token_info
        return token_info

    def _save_token_info(self, token_info):
        self.token_info = token_info
        if not self.user:
            # logger.warning("Skipping tokens save - without a user")
            return
        self.user.insert_or_update(tokens=token_info)


def get_auth_manager(user=None, redirect_uri="http://localhost:3000"):
    return StoredSpotifyOauth(
        scope=scope,
        user=user,
        redirect_uri=redirect_uri,
        # show_dialog=True,
    )


class SpotUserActions:
    def __init__(
        self,
        user=None,
        auth_manager=None,
        connect=True,
        redirect_uri="http://localhost:3000",
    ):
        initdb()
        # we use a custom client_credentials_manager that writes in the DB
        self.auth_manager = auth_manager or get_auth_manager(
            user, redirect_uri=redirect_uri
        )

        self.spotify = spotipy.Spotify(
            auth_manager=self.auth_manager, requests_timeout=30
        )

        if connect:
            try:
                spotify_user = self.spotify.current_user()
            except SpotifyException as e:
                raise SpotifyConnectionException(e.msg)

            # we are initialized - let's save the user
            self.user = User(id=spotify_user["id"]).insert_or_update(
                **dict(
                    name=spotify_user["display_name"],
                    email=spotify_user["email"],
                    picture=spotify_user["images"][0]["url"]
                    if spotify_user["images"]
                    else None,
                    tokens=self.auth_manager.token_info,
                )
            )

            if user is None:
                # we didn't have the user - so we save the tokens now
                self.auth_manager.user = self.user
            if getattr(self, "_new", False):
                self.msg("Sign up successful", msg_type="signup")

    def get_spotify_list(self, results):
        """A generic method to consume the Spotify API paginated results"""
        seen_next = deque(maxlen=10)
        while True:
            logger.debug(
                f"Got {results.get('offset',0)+len(results['items'])}/{results.get('total','unknown')} items"
            )
            for item in results["items"]:
                yield item
            next_page = results["next"]
            if next_page:
                if next_page in seen_next:
                    all_but_items = {k: v for k, v in results.items() if k != "items"}
                    raise RuntimeError(
                        f"Something is wrong - I got {next_page} that I already saw recently: {all_but_items}"
                    )
                seen_next.append(next_page)
                results = self.spotify.next(results)
            else:
                break

    # @ttl_cache(ttl=1 * 60)  # cached for a minute
    def get_all_playlists(self):
        """Return all the playlists of the user"""
        return [p for p in self.get_spotify_list(self.spotify.current_user_playlists())]

    def filter_own_playlists(self, playlists):
        for playlist in playlists:
            if (
                playlist["owner"]["id"] == self.user.id
            ):  # get only the one owned by the user
                yield playlist

    def get_or_create_playlist(self, name):
        playlists = self.filter_own_playlists(self.get_all_playlists())

        same_name_playlists = list(filter(lambda p: p["name"] == name, playlists))
        if not same_name_playlists:
            self.msg(f"Creating a new playlist: {name}", msg_type="playlist-create")
            playlist = self.spotify.user_playlist_create(
                self.spotify.current_user()["id"],
                description="All the songs you like - synced by Spotlike",
                name=name,
                public=False,
            )
        else:
            playlist = same_name_playlists[-1]  # getting the last
            if len(same_name_playlists) > 1:
                click.echo(
                    f"Warning: We have {len(same_name_playlists)}"
                    f" playlists with the name {name}",
                    color="green",
                )
                click.echo(
                    "Removing the others",
                    color="yellow",
                )
                for duplicated_playlist in same_name_playlists[:-1]:
                    logger.debug(f"Removing duplicated {duplicated_playlist['id']}")
                    self.spotify.current_user_unfollow_playlist(
                        duplicated_playlist["id"]
                    )

        return playlist

    def sync_liked_with_playlist(self, name, full=True):
        """Here we try to be smart to avoid having to go through all the likes or all the song in the playlist
        when it's not needed.
        """
        playlist = self.get_or_create_playlist(name)
        # we have these two iterators
        playlist_tracks = self.get_spotify_list(
            self.spotify.playlist_items(playlist["id"], additional_types=("track",))
        )
        likes = self.cached_likes()

        to_add, to_del = sync_merge(likes, playlist_tracks, full=full)

        if to_add or to_del:
            msg = filter(
                lambda x: x is not None,
                [
                    f"Added {len(to_add)}" if to_add else None,
                    f"Removed {len(to_del)}" if to_del else None,
                ],
            )
            self.msg(" / ".join(msg) + " songs", msg_type="synclike")

        # we add and remove all the needed tracks
        for all_tracks, method in (
            (to_add, partial(self.spotify.playlist_add_items, position=0)),
            (to_del, self.spotify.playlist_remove_all_occurrences_of_items),
        ):
            # we do our operations in chunks of 100 tracks
            for tracks in reverse_block_chunks(all_tracks, 100):
                method(
                    playlist["id"],
                    tracks,
                )

    def cached_likes(self):
        # TODO: This is enormous
        likes = list(self.liked_songs())
        self.cached_likes = lambda: likes  # replace the property
        return likes

    def liked_songs(self):
        logger.debug("Getting user likes")
        yield from self.get_spotify_list(
            self.spotify.current_user_saved_tracks(limit=50)
        )

    def remove_liked_duplicates(self):
        track_versions: Dict[str:list] = defaultdict(
            list
        )  # track key - list of (track_id, date)
        # we keep the date when a song was liked - so we can show it to the user
        for liked in self.cached_likes():
            track_id = liked["track"]["id"]
            track_duration = liked["track"]["duration_ms"]
            track_name = liked["track"]["name"]

            key = track_name, track_duration
            track_versions[key].append((track_id, liked["added_at"]))

        to_unlike = set()
        messages = []
        for key, versions in track_versions.items():
            if len(versions) > 1:
                duplicates = versions[:-1]  # all but the last
                messages.append(
                    f"Found a duplicate for {key} - removing {len(duplicates)}"
                    f" - liked on {[date for dup_id, date in versions]}"
                )
                to_unlike |= set(dup_id for dup_id, date in duplicates)
        if messages:
            self.msg("\n".join(messages), msg_type="duplicate")
        if to_unlike:
            self.unlike_tracks(to_unlike)

    def unlike_tracks(self, to_unlike):
        logger.debug(f"Unlike {len(to_unlike)} songs")

        for tracks in reverse_block_chunks(list(to_unlike), 100):
            self.spotify.current_user_saved_tracks_delete(
                tracks=tracks,
            )
        if isinstance(self.cached_likes, list):
            # filter the unliked_tracks
            self.cached_likes = [
                track for track in self.cached_likes if track not in to_unlike
            ]

    def recently_played(self, after=None):
        for played in self.get_spotify_list(
            self.spotify.current_user_recently_played()
        ):
            yield played

    def auto_like_recurrent(self, played_times=5, day_period=30, store=True):
        """Autolike songs played at least `played_times` times over the `day_period`"""
        check_history_from = datetime.datetime.utcnow() - datetime.timedelta(
            days=day_period
        )
        as_timestamp = int(check_history_from.timestamp() * 1000)  # in ms
        recently_played: Dict[str, Dict] = {}
        scanned = 0

        # we collect recent tracks in two ways - via the spotify top list - and via the recently played ones
        track_collecting_methods = (
            partial(self.spotify.current_user_top_tracks, time_range="short_term"),
            partial(self.spotify.current_user_recently_played, after=as_timestamp),
        )

        to_like = set()

        for track_collecting_method in track_collecting_methods:
            for played in self.get_spotify_list(track_collecting_method()):
                scanned += 1
                if played.get("type") == "track":  # this is a top-track we just add it
                    logger.debug(f"Track {played['name']} is a recent top")
                    to_like.add(played["id"])
                else:
                    track_id = played["track"]["id"]
                    played_at = played["played_at"]
                    if track_id not in recently_played:
                        recently_played[track_id] = dict(
                            name=played["track"]["name"], play_history=set()
                        )
                    recently_played[track_id]["play_history"].add(played_at)

        for track_id, desc in recently_played.items():
            if len(desc["play_history"]) >= played_times:
                logger.debug("Recently played several", desc)
                to_like.add(track_id)

        logger.debug(f"Scanned {scanned} songs - recurrent {len(to_like)}")

    def msg(self, message, msg_type=None):
        click.echo(message)
        message = Message(
            user=self.user,
            message=message,
            msg_type=msg_type,
        )
        message.save()

    def collect_likes(self):
        added = 0
        with db.atomic():
            for liked in self.cached_likes():
                track = store_track(liked["track"])
                try:
                    like = Liked(
                        track=track, user=self.user, date=parse_date(liked["added_at"])
                    )
                    like.save(force_insert=True)
                    added += 1
                except peewee.IntegrityError:
                    break
        if added:
            logger.debug(f"Added {added} likes")

    def collect_recent(self):
        added = 0
        with db.atomic():
            for played in self.recently_played():
                track = store_track(played["track"])

                try:
                    Play(
                        track=track,
                        user=self.user,
                        date=parse_date(played["played_at"]),
                    ).save(force_insert=True)
                    added += 1
                except peewee.IntegrityError:
                    break
        if added:
            logger.debug(f"Added {added} recent")
