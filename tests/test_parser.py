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


class TestOffsetsPastTheBasicPlane:
    """An entity counts in UTF-16 units, so anything above the BMP counts twice.

    parse works that out by encoding, except for a run that is entirely ASCII,
    where the count is the length and encoding it would be a copy made to learn
    nothing. These pin the two halves of that against each other.
    """

    @pytest.mark.parametrize(
        ("written", "expected"),
        [
            ("a **bold** b", ["bold"]),
            # One emoji ahead of the run is two units, not one.
            ("🎉 **bold** 🚀", ["bold"]),
            ("🎉🎉🎉 **after six units**",
             ["after six units"]),
            ("**🎉 inside 🚀**", ["🎉 inside 🚀"]),
            # Cyrillic is not ASCII but is still one unit each.
            ("Привет **bold** x", ["bold"]),
            ("a **b** c __i__ d `k` e", ["b", "i", "k"]),
            ("𝔘𝔫 **x**", ["x"]),
        ],
    )
    def test_an_entity_points_at_what_was_marked(self, written, expected):
        plain, entities = parse(written)
        assert [styled(plain, entity) for entity in entities] == expected

    def test_a_run_of_emoji_round_trips(self):
        written = "🎉 **bold** and __italic__ 🚀"
        plain, entities = parse(written)
        assert unparse(plain, entities) == written


class TestQuotesComingBack:
    """A blockquote is a line-level run, and > is only special where a line starts.

    Both halves of that were wrong in unparse: the marker was written in
    whatever order the entities happened to be in, so it could land inside a
    code span and stop being a marker; and a literal > was never escaped, so
    text that began with one came back as a quote with the character gone.
    """

    def test_a_quoted_code_span_keeps_its_marker_outside(self):
        plain, entities = parse(">`a`")
        assert unparse(plain, entities) == "> `a`"

    def test_a_quote_holding_styled_text_round_trips(self):
        written = "> **bold** and `code`"
        plain, entities = parse(written)
        assert unparse(plain, entities) == written

    @pytest.mark.parametrize(
        "written",
        [
            "\\> a quote that is not one",
            "\\>",
            "first line\n\\> second",
        ],
    )
    def test_a_literal_quote_marker_survives(self, written):
        plain, entities = parse(written)
        again = unparse(plain, entities)
        assert parse(again)[0] == plain

    def test_an_ordinary_greater_than_is_left_alone(self):
        # Escaping every > would put backslashes through ordinary prose.
        plain, entities = parse("a > b")
        assert unparse(plain, entities) == "a > b"

    def test_the_marker_is_escaped_inside_a_quote_too(self):
        plain, entities = parse("> \\> not nested")
        assert parse(unparse(plain, entities))[0] == plain


class TestTagsNestRatherThanCross:
    """Two runs starting on the same character have to open widest first.

    Telegram does not promise what order entities arrive in, and writing them
    out in whatever order they came produced crossed tags rather than nested
    ones, which is not HTML at all.
    """

    @pytest.mark.parametrize("order", [(0, 1), (1, 0)])
    def test_the_wider_run_wraps_the_narrower_one(self, order):
        pair = [
            types.MessageEntityItalic(offset=0, length=3),
            types.MessageEntityBold(offset=0, length=5),
        ]
        written = unparse("abcde", [pair[i] for i in order], mode="html")
        assert written == "<b><i>abc</i>de</b>"

    @pytest.mark.parametrize("order", [(0, 1), (1, 0)])
    def test_it_holds_for_markdown_too(self, order):
        pair = [
            types.MessageEntityItalic(offset=0, length=3),
            types.MessageEntityBold(offset=0, length=5),
        ]
        written = unparse("abcde", [pair[i] for i in order])
        assert written == "**__abc__de**"


class TestAQuoteIsLineLevel:
    """A blockquote can only begin where a line does and nothing inline is open.

    Without the second half a > inside a run took the rest of the line into a
    parse of its own while the run was still waiting to close, so both ended up
    covering the same characters and the same styling was reported twice.
    """

    def test_a_marker_inside_a_run_is_just_a_character(self):
        plain, entities = parse("__>__")
        assert plain == ">"
        assert kinds(entities) == [("MessageEntityItalic", 0, 1)]

    def test_no_run_is_reported_twice(self):
        plain, entities = parse("__>__d(>")
        assert plain == ">d(>"
        assert kinds(entities) == [("MessageEntityItalic", 0, 1)]

    def test_a_quote_still_begins_a_line(self):
        plain, entities = parse("> quoted")
        assert plain == "quoted"
        assert kinds(entities) == [("MessageEntityBlockquote", 0, 6)]

    def test_a_quote_after_a_closed_run_still_begins(self):
        plain, entities = parse("**b**\n> q")
        assert plain == "b\nq"
        assert ("MessageEntityBlockquote", 2, 1) in kinds(entities)

    def test_a_quote_still_holds_styled_text(self):
        plain, entities = parse("> **bold**")
        assert plain == "bold"
        assert sorted(kinds(entities)) == sorted(
            [("MessageEntityBold", 0, 4), ("MessageEntityBlockquote", 0, 4)]
        )

    @pytest.mark.parametrize(
        "written", ["__>__", "__>__d(>", "> quoted", "> **bold**"]
    )
    def test_each_of_them_round_trips(self, written):
        plain, entities = parse(written)
        again = unparse(plain, entities)
        assert parse(again)[0] == plain
        assert sorted(kinds(parse(again)[1])) == sorted(kinds(entities))
