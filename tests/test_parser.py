"""Styled text, in both flavours and both directions.

The offsets are the point. Telegram counts in UTF-16 code units, Python counts
in code points, and the two agree until somebody sends an emoji, so most of what
is checked here is checked twice: once with plain text and once with the same
text after something outside the Basic Multilingual Plane. A library that only
tests the first is a library that works until its first 👍.
"""

from __future__ import annotations

import pytest

from sunnygram.parser import parse, unparse, utf16_length
from sunnygram.parser.entities import Span, spans_to_entities
from sunnygram.raw import types

WAVE = "\U0001f44b"  # two UTF-16 units, one Python character


def kinds(entities):
    return [(type(e).__name__, e.offset, e.length) for e in entities]


def styled(text: str, entity) -> str:
    """The exact run an entity points at, sliced the way Telegram means it."""
    units = text.encode("utf-16-le")
    start, end = entity.offset * 2, (entity.offset + entity.length) * 2
    return units[start:end].decode("utf-16-le")


class TestCounting:
    def test_ordinary_text_counts_as_itself(self):
        assert utf16_length("hello") == 5

    def test_an_emoji_counts_twice(self):
        assert utf16_length(WAVE) == 2
        assert len(WAVE) == 1

    def test_the_basic_plane_counts_once(self):
        assert utf16_length("è") == 1
        assert utf16_length("日本語") == 3


class TestMarkdown:
    @pytest.mark.parametrize(
        ("written", "plain", "entity"),
        [
            ("**bold**", "bold", "MessageEntityBold"),
            ("__italic__", "italic", "MessageEntityItalic"),
            ("~~struck~~", "struck", "MessageEntityStrike"),
            ("||secret||", "secret", "MessageEntitySpoiler"),
            ("`code`", "code", "MessageEntityCode"),
        ],
    )
    def test_each_delimiter(self, written, plain, entity):
        text, entities = parse(written)
        assert text == plain
        assert kinds(entities) == [(entity, 0, len(plain))]

    def test_a_run_after_an_emoji_is_offset_by_two(self):
        text, entities = parse(f"{WAVE} **bold**")
        assert text == f"{WAVE} bold"
        assert entities[0].offset == 3
        assert styled(text, entities[0]) == "bold"

    def test_an_emoji_inside_a_run_lengthens_it(self):
        text, entities = parse(f"**a{WAVE}b**")
        assert entities[0].length == 4
        assert styled(text, entities[0]) == f"a{WAVE}b"

    def test_runs_nest(self):
        text, entities = parse("**bold and __both__**")
        assert text == "bold and both"
        assert ("MessageEntityBold", 0, 13) in kinds(entities)
        assert ("MessageEntityItalic", 9, 4) in kinds(entities)

    def test_a_code_block_keeps_its_language(self):
        text, entities = parse("```python\nprint(1)\n```")
        assert text == "print(1)"
        assert entities[0].language == "python"

    def test_nothing_inside_code_is_read_as_markup(self):
        text, entities = parse("`**not bold**`")
        assert text == "**not bold**"
        assert kinds(entities) == [("MessageEntityCode", 0, 12)]

    def test_a_link_becomes_a_url_entity(self):
        text, entities = parse("[label](https://example.com/a_b)")
        assert text == "label"
        assert entities[0].url == "https://example.com/a_b"

    def test_a_tg_link_becomes_a_mention(self):
        text, entities = parse("[me](tg://user?id=777000)")
        assert text == "me"
        assert isinstance(entities[0], types.MessageEntityMentionName)
        assert entities[0].user_id == 777000

    def test_a_tg_emoji_link_becomes_a_custom_emoji(self):
        text, entities = parse(f"[{WAVE}](tg://emoji?id=5368324170671202286)")
        assert isinstance(entities[0], types.MessageEntityCustomEmoji)
        assert entities[0].document_id == 5368324170671202286

    def test_a_quote_runs_to_the_end_of_its_line(self):
        text, entities = parse("> quoted\nafter")
        assert text == "quoted\nafter"
        assert kinds(entities) == [("MessageEntityBlockquote", 0, 6)]

    def test_a_lone_delimiter_is_just_text(self):
        # People write about a * b without meaning anything by it, and a parser
        # that raises at them is a parser that eats messages.
        text, entities = parse("2 * 3 = 6")
        assert text == "2 * 3 = 6"
        assert entities == []

    def test_an_escape_keeps_the_character(self):
        text, entities = parse(r"\*\*not bold\*\*")
        assert text == "**not bold**"
        assert entities == []

    def test_an_unclosed_run_still_ends_somewhere(self):
        text, entities = parse("**never closed")
        assert text == "never closed"
        assert kinds(entities) == [("MessageEntityBold", 0, 12)]

    def test_trailing_space_is_not_part_of_a_run(self):
        # The API asks for this: a run that swallowed the space before the next
        # word should not carry it.
        text, entities = parse("**bold ** rest")
        assert entities[0].length == 4


class TestHtml:
    @pytest.mark.parametrize(
        ("written", "entity"),
        [
            ("<b>x</b>", "MessageEntityBold"),
            ("<strong>x</strong>", "MessageEntityBold"),
            ("<i>x</i>", "MessageEntityItalic"),
            ("<em>x</em>", "MessageEntityItalic"),
            ("<u>x</u>", "MessageEntityUnderline"),
            ("<s>x</s>", "MessageEntityStrike"),
            ("<del>x</del>", "MessageEntityStrike"),
            ("<code>x</code>", "MessageEntityCode"),
            ("<tg-spoiler>x</tg-spoiler>", "MessageEntitySpoiler"),
        ],
    )
    def test_each_tag(self, written, entity):
        text, entities = parse(written, "html")
        assert text == "x"
        assert kinds(entities) == [(entity, 0, 1)]

    def test_a_link(self):
        text, entities = parse('<a href="https://x.com">link</a>', "html")
        assert text == "link"
        assert entities[0].url == "https://x.com"

    def test_a_code_block_with_a_language(self):
        text, entities = parse(
            '<pre><code class="language-py">x=1</code></pre>', "html"
        )
        assert text == "x=1"
        assert entities[0].language == "py"

    def test_an_expandable_quote(self):
        _, entities = parse("<blockquote expandable>x</blockquote>", "html")
        assert entities[0].collapsed is True

    def test_a_custom_emoji(self):
        text, entities = parse(f'<tg-emoji emoji-id="5">{WAVE}</tg-emoji>', "html")
        assert text == WAVE
        assert entities[0].document_id == 5
        assert entities[0].length == 2

    def test_character_references_come_out_as_characters(self):
        text, entities = parse("<b>a &amp; b</b>", "html")
        assert text == "a & b"
        assert entities[0].length == 5

    def test_a_tag_nobody_knows_is_ignored_and_its_text_kept(self):
        text, entities = parse("<div>plain <b>bold</b></div>", "html")
        assert text == "plain bold"
        assert kinds(entities) == [("MessageEntityBold", 6, 4)]

    def test_offsets_survive_an_emoji(self):
        text, entities = parse(f"<b>{WAVE}</b> after <i>x</i>", "html")
        assert entities[0].length == 2
        assert styled(text, entities[1]) == "x"


class TestGoingBack:
    @pytest.mark.parametrize(
        "written",
        [
            "**bold** and __italic__",
            "plain text",
            "`code` here",
            "[label](https://example.com)",
            f"{WAVE} then **bold**",
            "**outer __inner__**",
        ],
    )
    def test_markdown_round_trips(self, written):
        text, entities = parse(written)
        again, again_entities = parse(unparse(text, entities))
        assert again == text
        assert kinds(again_entities) == kinds(entities)

    @pytest.mark.parametrize(
        "written",
        [
            "<b>bold</b> and <i>italic</i>",
            'a <a href="https://x.com">link</a>',
            f"<b>{WAVE}</b>",
        ],
    )
    def test_html_round_trips(self, written):
        text, entities = parse(written, "html")
        again, again_entities = parse(unparse(text, entities, "html"), "html")
        assert again == text
        assert kinds(again_entities) == kinds(entities)

    def test_code_is_not_escaped_on_the_way_out(self):
        # Backslashes in somebody's source listing are the one place they are
        # certain to be noticed.
        text, entities = parse("`a_b*c`")
        assert unparse(text, entities) == "`a_b*c`"

    def test_special_characters_outside_code_are_escaped(self):
        assert unparse("a_b", []) == r"a\_b"

    def test_html_escapes_what_it_must(self):
        assert unparse("a < b & c", None, "html") == "a &lt; b &amp; c"


class TestModes:
    def test_no_mode_means_no_parsing(self):
        assert parse("**as written**", None) == ("**as written**", [])

    def test_the_names_are_forgiving(self):
        for name in ("md", "Markdown", "MARKDOWN", " html "):
            assert parse("plain", name)[0] == "plain"

    def test_a_mode_nobody_has_says_which_there_are(self):
        with pytest.raises(Exception, match="markdown"):
            parse("x", "rst")


class TestTheSmallPrint:
    def test_an_empty_run_is_dropped(self):
        assert spans_to_entities([Span("bold", 0, 0)], "") == []

    def test_a_run_of_only_spaces_is_dropped(self):
        assert spans_to_entities([Span("bold", 0, 3)], "   ") == []

    def test_the_entities_come_out_in_order(self):
        spans = [Span("italic", 5, 9), Span("bold", 0, 4)]
        entities = spans_to_entities(spans, "some text here")
        assert [e.offset for e in entities] == [0, 5]
