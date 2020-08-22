from spottools import sync_merge, reverse_block_chunks


def song(added_at, track_id):
    return dict(
        added_at=added_at,
        track=dict(id=track_id,
                   name=track_id)
    )


class TestMergeFull:
    """ A few test for the full merging algorithm """
    full = True

    def test_to_empty(self):
        likes = iter([
            song("2020-08-22", 'b'),
            song("2019-08-22", 'a'),
        ])
        current = iter([])
        to_add, to_del = sync_merge(likes, current, full=self.full)
        assert to_add == ['b', 'a']
        assert to_del == []

    def test_to_unrelated(self):
        likes = iter([
            song("2020-08-22", 'b'),
            song("2019-08-22", 'a'),
        ])
        current = iter([
            song("2020-08-22", 'c'),
        ])
        to_add, to_del = sync_merge(likes, current, full=self.full)
        assert to_add == ['b', 'a']
        assert to_del == ['c']

    def test_normal(self):
        likes = iter([
            song("2020-08-22", 'b'),
            song("2019-08-22", 'a'),
        ])
        current = iter([
            song("2020-01-22", 'a'),
        ])
        to_add, to_del = sync_merge(likes, current, full=self.full)
        assert to_add == ['b']
        assert to_del == []

    def test_i_hate_everything(self):
        likes = iter([])
        current = iter([
            song("2020-01-22", 'a'),
        ])
        to_add, to_del = sync_merge(likes, current, full=self.full)
        assert to_add == []
        assert to_del == ['a']


class TestChunkSplitting:
    def test_chunk_inverted(self):
        l = [1, 2, 3, 4, 5, 6, 7, 8]
        chunks = list(reverse_block_chunks(l, 3))
        assert chunks == [
            [6, 7, 8],
            [3, 4, 5],
            [1, 2],
        ]

    def test_empty(self):
        l = []
        chunks = list(reverse_block_chunks(l, 3))
        assert chunks == []
