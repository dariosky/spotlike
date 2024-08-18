import logging

logger = logging.getLogger("spotlike.multispot")


def reverse_block_chunks(haystack: list, size):
    """iterate through the list with a given size so the blocks keep their inner order,
    but we get them from the latest"""
    start, end = len(haystack) - size, len(haystack)
    while end > 0:
        yield haystack[start:end]
        start, end = max(0, start - size), start


def sync_merge_full(likes, playlist_tracks):
    """A full-sync, iterating all likes and all the playlist_tracks
    There's no way around to avoid a full-iteration sync from now and then
    Because it's possible to unlike old songs - and that leaves no traces
    """
    likes_ids = [t["track"]["id"] for t in likes]  # here we care about the order
    playlist_ids = set(
        [t["track"]["id"] for t in playlist_tracks]
    )  # we don't care about the order

    to_add = [t for t in likes_ids if t not in playlist_ids]
    to_del = list(playlist_ids - set(likes_ids))
    return to_add, to_del


def sync_merge_fast(likes, playlist_tracks):
    """A fast-sync - that copies every new likes in the playlist"""
    to_add = []
    to_del = []

    in_playlist = next(playlist_tracks, None)
    liked = next(likes, None)

    # so let's do merge-magic
    while True:
        # let's add songs until we find something already synced or we find something sinced before the current like
        if (
            liked
            and in_playlist
            and (
                liked["track"]["id"] != in_playlist["track"]["id"]
                and in_playlist["added_at"] <= liked["added_at"]
            )
        ):
            to_add.append(liked["track"]["id"])
            liked = next(likes, None)
            continue

        if liked and (
            not in_playlist or liked["track"]["id"] != in_playlist["track"]["id"]
        ):
            # if what we have
            logger.info(f"Adding the non-liked {liked['track']['name']}")
            to_add.append(liked["track"]["id"])
            liked = next(likes, None)
            continue
        break

    return to_add, to_del


def sync_merge(likes, playlist_tracks, full=True):
    # ... and in the end that's what we want to know
    if full:
        return sync_merge_full(likes, playlist_tracks)
    else:
        return sync_merge_fast(likes, playlist_tracks)


def store_track(track):
    artists = []
    for artist in track.get("artists", []):
        a = Artist().insert_or_update(
            id=artist["id"],
            name=artist["name"],
        )
        artists.append(a)

    if track.get("album"):
        album = Album().insert_or_update(
            id=track["album"]["id"],
            name=track["album"]["name"],
            release_date=parse_date(track["album"]["release_date"]),
            release_date_precision=track["album"]["release_date_precision"],
            picture=track["album"]["images"][0]["url"]
            if track["album"]["images"]
            else None,
        )
        for artist in track["album"].get("artists", []):
            a = Artist().insert_or_update(
                id=artist["id"],
                name=artist["name"],
            )
            AlbumArtist().insert_or_update(album=album, artist=a)
    else:
        album = None

    t = Track().insert_or_update(
        id=track["id"],
        duration=track["duration_ms"],
        title=track["name"],
        album=album,
    )
    for a in artists:
        TrackArtist().insert_or_update(track=t, artist=a)
    return t
