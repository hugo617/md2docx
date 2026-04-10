import pytest
from src.core.elements import DocElement, ElementType
from src.core.md_writer import elements_to_md


class TestMdWriter:
    """Test Markdown writer functionality"""

    def test_heading(self):
        """Test heading to Markdown conversion"""
        els = [DocElement(element_type=ElementType.HEADING, text="Title", level=2)]
        result = elements_to_md(els)
        assert "## Title" in result

    def test_heading_levels(self):
        """Test all heading levels"""
        for level in range(1, 7):
            els = [DocElement(element_type=ElementType.HEADING, text=f"H{level}", level=level)]
            result = elements_to_md(els)
            expected = f"{'#' * level} H{level}"
            assert expected in result

    def test_paragraph(self):
        """Test paragraph to Markdown conversion"""
        els = [DocElement(element_type=ElementType.PARAGRAPH, text="Simple paragraph")]
        result = elements_to_md(els)
        assert "Simple paragraph" in result

    def test_bold(self):
        """Test bold text to Markdown conversion"""
        els = [DocElement(element_type=ElementType.BOLD, text="bold")]
        result = elements_to_md(els)
        assert "**bold**" in result

    def test_italic(self):
        """Test italic text to Markdown conversion"""
        els = [DocElement(element_type=ElementType.ITALIC, text="italic")]
        result = elements_to_md(els)
        assert "*italic*" in result

    def test_strikethrough(self):
        """Test strikethrough to Markdown conversion"""
        els = [DocElement(element_type=ElementType.STRIKETHROUGH, text="deleted")]
        result = elements_to_md(els)
        assert "~~deleted~~" in result

    def test_code_inline(self):
        """Test inline code to Markdown conversion"""
        els = [DocElement(element_type=ElementType.CODE_INLINE, text="code")]
        result = elements_to_md(els)
        assert "`code`" in result

    def test_code_block(self):
        """Test code block to Markdown conversion"""
        els = [DocElement(element_type=ElementType.CODE_BLOCK, text="x=1", language="python")]
        result = elements_to_md(els)
        assert "```python" in result
        assert "x=1" in result
        assert "```" in result.split("x=1")[1]

    def test_code_block_no_language(self):
        """Test code block without language"""
        els = [DocElement(element_type=ElementType.CODE_BLOCK, text="code here")]
        result = elements_to_md(els)
        assert "```" in result
        assert "code here" in result

    def test_unordered_list(self):
        """Test unordered list to Markdown conversion"""
        els = [DocElement(
            element_type=ElementType.UNORDERED_LIST,
            children=[
                DocElement(element_type=ElementType.LIST_ITEM, text="a"),
                DocElement(element_type=ElementType.LIST_ITEM, text="b"),
                DocElement(element_type=ElementType.LIST_ITEM, text="c"),
            ]
        )]
        result = elements_to_md(els)
        assert "- a" in result
        assert "- b" in result
        assert "- c" in result

    def test_ordered_list(self):
        """Test ordered list to Markdown conversion"""
        els = [DocElement(
            element_type=ElementType.ORDERED_LIST,
            children=[
                DocElement(element_type=ElementType.LIST_ITEM, text="first"),
                DocElement(element_type=ElementType.LIST_ITEM, text="second"),
            ]
        )]
        result = elements_to_md(els)
        assert "1. first" in result
        assert "1. second" in result

    def test_list_item_unordered(self):
        """Test individual list item with unordered style"""
        els = [DocElement(element_type=ElementType.LIST_ITEM, text="item", style_name="unordered_list")]
        result = elements_to_md(els)
        assert "- item" in result

    def test_list_item_ordered(self):
        """Test individual list item with ordered style"""
        els = [DocElement(element_type=ElementType.LIST_ITEM, text="item", style_name="ordered_list")]
        result = elements_to_md(els)
        assert "1. item" in result

    def test_blockquote(self):
        """Test blockquote to Markdown conversion"""
        els = [DocElement(element_type=ElementType.BLOCKQUOTE, text="Quote text")]
        result = elements_to_md(els)
        assert "> Quote text" in result

    def test_table(self):
        """Test table to Markdown conversion"""
        els = [DocElement(
            element_type=ElementType.TABLE,
            children=[
                DocElement(element_type=ElementType.TABLE_ROW, children=[
                    DocElement(element_type=ElementType.TABLE_CELL, text="H1"),
                    DocElement(element_type=ElementType.TABLE_CELL, text="H2"),
                ]),
                DocElement(element_type=ElementType.TABLE_ROW, children=[
                    DocElement(element_type=ElementType.TABLE_CELL, text="D1"),
                    DocElement(element_type=ElementType.TABLE_CELL, text="D2"),
                ]),
            ]
        )]
        result = elements_to_md(els)
        assert "| H1 | H2 |" in result
        assert "| --- | --- |" in result
        assert "| D1 | D2 |" in result

    def test_table_single_column(self):
        """Test table with single column"""
        els = [DocElement(
            element_type=ElementType.TABLE,
            children=[
                DocElement(element_type=ElementType.TABLE_ROW, children=[
                    DocElement(element_type=ElementType.TABLE_CELL, text="Header"),
                ]),
                DocElement(element_type=ElementType.TABLE_ROW, children=[
                    DocElement(element_type=ElementType.TABLE_CELL, text="Data"),
                ]),
            ]
        )]
        result = elements_to_md(els)
        assert "| Header |" in result
        assert "| --- |" in result
        assert "| Data |" in result

    def test_horizontal_rule(self):
        """Test horizontal rule to Markdown conversion"""
        els = [DocElement(element_type=ElementType.HORIZONTAL_RULE)]
        result = elements_to_md(els)
        assert "---" in result

    def test_image(self):
        """Test image to Markdown conversion"""
        els = [DocElement(element_type=ElementType.IMAGE, alt="Alt text", url="image.jpg")]
        result = elements_to_md(els)
        assert "![Alt text](image.jpg)" in result

    def test_image_no_alt(self):
        """Test image without alt text"""
        els = [DocElement(element_type=ElementType.IMAGE, url="image.jpg")]
        result = elements_to_md(els)
        assert "![](image.jpg)" in result

    def test_paragraph_with_children(self):
        """Test paragraph with inline formatting children"""
        els = [DocElement(
            element_type=ElementType.PARAGRAPH,
            children=[
                DocElement(element_type=ElementType.BOLD, text="bold"),
                DocElement(element_type=ElementType.PARAGRAPH, text=" and "),
                DocElement(element_type=ElementType.ITALIC, text="italic"),
            ]
        )]
        result = elements_to_md(els)
        assert "**bold**" in result
        assert "*italic*" in result
        assert " and " in result

    def test_multiple_elements(self):
        """Test multiple elements conversion"""
        els = [
            DocElement(element_type=ElementType.HEADING, text="Title", level=1),
            DocElement(element_type=ElementType.PARAGRAPH, text="Paragraph"),
            DocElement(element_type=ElementType.HORIZONTAL_RULE),
        ]
        result = elements_to_md(els)
        assert "# Title" in result
        assert "Paragraph" in result
        assert "---" in result

    def test_empty_list(self):
        """Test empty elements list"""
        els = []
        result = elements_to_md(els)
        assert result == "\n"

    def test_complex_document(self):
        """Test complex document with multiple element types"""
        els = [
            DocElement(element_type=ElementType.HEADING, text="Title", level=1),
            DocElement(element_type=ElementType.PARAGRAPH, text="Introduction"),
            DocElement(
                element_type=ElementType.UNORDERED_LIST,
                children=[
                    DocElement(element_type=ElementType.LIST_ITEM, text="Point 1"),
                    DocElement(element_type=ElementType.LIST_ITEM, text="Point 2"),
                ]
            ),
            DocElement(element_type=ElementType.CODE_BLOCK, text="print('hello')", language="python"),
        ]
        result = elements_to_md(els)
        assert "# Title" in result
        assert "Introduction" in result
        assert "- Point 1" in result
        assert "```python" in result
        assert "print('hello')" in result

    def test_link(self):
        """Test link element (if supported)"""
        els = [DocElement(element_type=ElementType.LINK, text="Link", url="https://example.com")]
        result = elements_to_md(els)
        # Links may be rendered as plain text in current implementation
        assert "Link" in result
