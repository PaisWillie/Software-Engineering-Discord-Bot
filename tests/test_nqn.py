from unittest import TestCase, mock
import unittest
from Miscellaneous import nqn


class TestNQN(TestCase):

    def setUp(self):
        def fake_get_emoji_repr(cog_ins, emoji_name : str):
            return {key.lower(): value for key, value in {
                    'sadge': '<:sadge:1234567890>',
                    'drake': '<a:drake:1234543210>',
                    'omegalul': '<:omegalul:4159075138>',
                    'pepeLaugh': '<:pepeLaugh:1234543210>',
                    'pepe_laugh': '<:pepe_laugh:9876543210>',
                }.items()}.get(emoji_name.lower())
        
        self.cog_ins = nqn.NQN(bot=None)
        self.patch = mock.patch.object(nqn.NQN, 'get_emoji_repr', fake_get_emoji_repr)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def _test_parse_message(self, original_message, expected_message):
        parsed_message = self.cog_ins.parse_message(original_message)
        self.assertEqual(parsed_message, expected_message)


    def test_normal_no_emoji(self):
        self._test_parse_message("just a normal message", None)

    def test_normal_emoji_animated(self):
        self._test_parse_message(":drake:", "<a:drake:1234543210>")

    def test_normal_emoji(self):
        self._test_parse_message(":sadge:", "<:sadge:1234567890>")

    def test_with_message(self):
        self._test_parse_message("w :omegalul: w", "w <:omegalul:4159075138> w")

    def test_emoji_case(self):
        self._test_parse_message(":pepeLaugh: :pepe_laugh:", "<:pepeLaugh:1234543210> <:pepe_laugh:9876543210>")

    def test_emoji_case_insens(self):
        self._test_parse_message(":pepelaugh:", "<:pepeLaugh:1234543210>")

    def test_global_emoji(self): # assumes no server emote with same name
        self._test_parse_message("wow :flushed:", None)

    def test_emoji_in_markdown(self):
        self._test_parse_message("try typing `:drake:`", None)

    def test_emoji_in_markdown_multi(self):
        self._test_parse_message("try typing ```:drake:```", None)

    def test_server_emote(self):
        self._test_parse_message("<:sadge:1234567890>", None)

    def test_server_emote_animated(self):
        self._test_parse_message("<a:drake:1234543210>", None)

    def test_incomplete_begin(self):
        self._test_parse_message(":sadge:1>", "<:sadge:1234567890>1>")

    def test_incomplete_end(self):
        self._test_parse_message("<:sadge:1", "<<:sadge:1234567890>1")

    def test_incomplete_end_animated(self):
        self._test_parse_message("<a:drake:1", "<a<a:drake:1234543210>1")

    def test_no_spacing(self):
        self._test_parse_message(":drake::drake::drake:", "<a:drake:1234543210><a:drake:1234543210><a:drake:1234543210>")

    def test_mixed_scope(self):
        self._test_parse_message(":flushed::omegalul:", ":flushed:<:omegalul:4159075138>")

    def test_gauntlet(self):
        self._test_parse_message(
            """:drake:a:test:omegalul:sadge:`a`:sadge:``a``:omegalul:`asd:drake>:sadge:```
:sadge::sadge:``````:drak```e:omegalul:""",
            """<a:drake:1234543210>a:test:omegalul<:sadge:1234567890>`a`<:sadge:1234567890>``a``<:omegalul:4159075138>`asd:drake><:sadge:1234567890>```
:sadge::sadge:``````:drak```e<:omegalul:4159075138>""")


# run test suite via
# python3 -m unittest tests/test_nqn.py -v
if __name__ == '__main__':
    unittest.main()