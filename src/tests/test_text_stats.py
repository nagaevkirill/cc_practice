import pytest
from src.utils.text_stats import analyze, TextStats


# ---------------------------------------------------------------------------
# Базовое поведение
# ---------------------------------------------------------------------------

class TestAnalyzeBasic:
    def test_returns_text_stats_instance(self):
        assert isinstance(analyze("hello"), TextStats)

    def test_empty_string(self):
        result = analyze("")
        assert result.char_count == 0
        assert result.char_count_no_spaces == 0
        assert result.word_count == 0
        assert result.line_count == 0

    def test_single_word(self):
        result = analyze("hello")
        assert result.char_count == 5
        assert result.char_count_no_spaces == 5
        assert result.word_count == 1
        assert result.line_count == 1

    def test_multiple_words(self):
        result = analyze("hello world foo")
        assert result.word_count == 3

    def test_extra_spaces_between_words(self):
        result = analyze("hello   world")
        assert result.word_count == 2


# ---------------------------------------------------------------------------
# Подсчёт символов
# ---------------------------------------------------------------------------

class TestCharCount:
    def test_char_count_includes_spaces(self):
        result = analyze("a b")
        assert result.char_count == 3

    def test_char_count_no_spaces_excludes_spaces(self):
        result = analyze("a b")
        assert result.char_count_no_spaces == 2

    def test_char_count_no_spaces_excludes_tabs_and_newlines(self):
        result = analyze("a\tb\nc")
        assert result.char_count_no_spaces == 3

    def test_only_spaces(self):
        result = analyze("   ")
        assert result.char_count == 3
        assert result.char_count_no_spaces == 0
        assert result.word_count == 0


# ---------------------------------------------------------------------------
# Подсчёт строк
# ---------------------------------------------------------------------------

class TestLineCount:
    def test_single_line(self):
        assert analyze("one line").line_count == 1

    def test_two_lines(self):
        assert analyze("line one\nline two").line_count == 2

    def test_three_lines(self):
        assert analyze("a\nb\nc").line_count == 3

    def test_trailing_newline_not_counted_as_extra_line(self):
        # splitlines() не добавляет пустую строку в конце
        assert analyze("hello\n").line_count == 1

    def test_windows_line_endings(self):
        assert analyze("a\r\nb\r\nc").line_count == 3


# ---------------------------------------------------------------------------
# Кириллица и юникод
# ---------------------------------------------------------------------------

class TestUnicode:
    def test_cyrillic_word_count(self):
        result = analyze("Привет мир")
        assert result.word_count == 2

    def test_cyrillic_char_count(self):
        result = analyze("Привет")
        assert result.char_count == 6
        assert result.char_count_no_spaces == 6

    def test_emoji_counted_as_chars(self):
        result = analyze("hi 🎉")
        assert result.word_count == 2
        assert result.char_count == 4
