import pytest
from src.utils.strip_empty_lines import strip_empty_lines


class TestStripEmptyLinesBasic:
    def test_empty_string(self):
        assert strip_empty_lines("") == ""

    def test_no_empty_lines(self):
        text = "line one\nline two\nline three\n"
        assert strip_empty_lines(text) == text

    def test_removes_empty_line_between(self):
        assert strip_empty_lines("a\n\nb\n") == "a\nb\n"

    def test_removes_multiple_empty_lines(self):
        assert strip_empty_lines("a\n\n\n\nb\n") == "a\nb\n"

    def test_removes_leading_empty_lines(self):
        assert strip_empty_lines("\n\na\n") == "a\n"

    def test_removes_trailing_empty_lines(self):
        assert strip_empty_lines("a\n\n\n") == "a\n"


class TestStripEmptyLinesWhitespace:
    def test_removes_lines_with_only_spaces(self):
        assert strip_empty_lines("a\n   \nb\n") == "a\nb\n"

    def test_removes_lines_with_only_tabs(self):
        assert strip_empty_lines("a\n\t\t\nb\n") == "a\nb\n"

    def test_keeps_lines_with_content_and_spaces(self):
        text = "  indented line  \n"
        assert strip_empty_lines(text) == text


class TestStripEmptyLinesLineEndings:
    def test_windows_line_endings(self):
        assert strip_empty_lines("a\r\n\r\nb\r\n") == "a\r\nb\r\n"

    def test_single_line_no_newline(self):
        assert strip_empty_lines("hello") == "hello"

    def test_only_empty_lines(self):
        assert strip_empty_lines("\n\n\n") == ""


class TestStripEmptyLinesUnicode:
    def test_cyrillic_text(self):
        assert strip_empty_lines("Привет\n\nМир\n") == "Привет\nМир\n"

    def test_emoji_lines_preserved(self):
        assert strip_empty_lines("hello\n\n🎉\n") == "hello\n🎉\n"
