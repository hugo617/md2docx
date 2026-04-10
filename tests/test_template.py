import pytest
from src.template.template import parse_md_for_template, extract_sections, resolve_section_data


class TestTemplate:
    """Test template parsing and section extraction functionality"""

    def test_parse_front_matter(self):
        """Test parsing YAML front matter"""
        md = """---
key: val
name: test
---

## Section
content"""
        fm, body = parse_md_for_template(md)
        assert fm == {"key": "val", "name": "test"}
        assert "Section" in body
        assert "content" in body

    def test_parse_front_matter_with_numbers(self):
        """Test parsing front matter with various data types"""
        md = """---
string: text
number: 42
float: 3.14
bool: true
list:
  - a
  - b
---

Content here"""
        fm, body = parse_md_for_template(md)
        assert fm["string"] == "text"
        assert fm["number"] == 42
        assert fm["float"] == 3.14
        assert fm["bool"] is True
        assert fm["list"] == ["a", "b"]
        assert "Content here" in body

    def test_no_front_matter(self):
        """Test handling content without front matter"""
        md = "Just text without front matter"
        fm, body = parse_md_for_template(md)
        assert fm == {}
        assert body == "Just text without front matter"

    def test_empty_front_matter(self):
        """Test handling empty front matter"""
        md = """---

## Section
content"""
        fm, body = parse_md_for_template(md)
        assert fm == {}
        assert "Section" in body

    def test_incomplete_front_matter_delimiters(self):
        """Test handling incomplete front matter delimiters"""
        md = """---
key: val
## Section"""
        fm, body = parse_md_for_template(md)
        # Should treat as no front matter
        assert fm == {}
        assert "key: val" in body

    def test_extract_sections(self):
        """Test extracting sections by level 2 headings"""
        body = """## Sec1

content1

## Sec2

content2"""
        sections = extract_sections(body)
        assert "Sec1" in sections
        assert "Sec2" in sections
        assert sections["Sec1"] == "content1"
        assert sections["Sec2"] == "content2"

    def test_extract_sections_with_multiline_content(self):
        """Test extracting sections with multiline content"""
        body = """## Introduction

This is the introduction.

It has multiple paragraphs.

## Details

More details here."""
        sections = extract_sections(body)
        assert "Introduction" in sections
        assert "Details" in sections
        assert "This is the introduction." in sections["Introduction"]
        assert "It has multiple paragraphs." in sections["Introduction"]
        assert "More details here." in sections["Details"]

    def test_extract_sections_no_sections(self):
        """Test extracting sections when no level 2 headings exist"""
        body = "Just some text\n\nWithout level 2 headings"
        sections = extract_sections(body)
        assert len(sections) == 0

    def test_extract_sections_with_level1_headings(self):
        """Test that level 1 headings are included in section content"""
        body = """## Section

# Inside Section

Content"""
        sections = extract_sections(body)
        assert "Section" in sections
        assert "# Inside Section" in sections["Section"]

    def test_extract_sections_empty_content(self):
        """Test extracting sections with empty content after heading"""
        body = """## Empty Section

## Next Section
Content"""
        sections = extract_sections(body)
        assert "Empty Section" in sections
        assert sections["Empty Section"] == ""
        assert "Next Section" in sections
        assert sections["Next Section"] == "Content"

    def test_extract_sections_preserves_formatting(self):
        """Test that section content preserves formatting"""
        body = """## Code Section

```python
print("hello")
```

## List Section

- item1
- item2"""
        sections = extract_sections(body)
        assert "Code Section" in sections
        assert "List Section" in sections
        assert '```python' in sections["Code Section"]
        assert "- item1" in sections["List Section"]

    def test_resolve_section_data_basic(self):
        """Test resolving section data with basic config"""
        config = {
            "content_mapping": {
                "headings": {
                    "Introduction": "intro",
                    "Details": "details"
                }
            }
        }
        front_matter = {"title": "Test Doc", "author": "John"}
        sections = {
            "Introduction": "Intro content",
            "Details": "Details content"
        }
        data = resolve_section_data(config, front_matter, sections)
        assert data["title"] == "Test Doc"
        assert data["author"] == "John"
        assert data["intro"] == "Intro content"
        assert data["details"] == "Details content"

    def test_resolve_section_data_no_mapping(self):
        """Test resolving data when no content mapping exists"""
        config = {}
        front_matter = {"key": "value"}
        sections = {"Section": "Content"}
        data = resolve_section_data(config, front_matter, sections)
        assert data["key"] == "value"
        assert "Section" not in data  # No mapping, so not included

    def test_resolve_section_data_missing_section(self):
        """Test resolving data when mapped section doesn't exist"""
        config = {
            "content_mapping": {
                "headings": {
                    "Existing": "field1",
                    "Missing": "field2"
                }
            }
        }
        front_matter = {}
        sections = {"Existing": "Content"}
        data = resolve_section_data(config, front_matter, sections)
        assert data["field1"] == "Content"
        assert "field2" not in data  # Section doesn't exist

    def test_resolve_section_data_front_matter_override(self):
        """Test that sections override front matter values"""
        # DESIGN DECISION: Sections take precedence over front matter
        # The code starts with front_matter dict, then overwrites with section values
        config = {
            "content_mapping": {
                "headings": {
                    "Section": "content_field"
                }
            }
        }
        front_matter = {"content_field": "From front matter"}
        sections = {"Section": "From section"}
        data = resolve_section_data(config, front_matter, sections)
        # Section value overrides front matter value
        assert data["content_field"] == "From section"

    def test_resolve_section_data_empty_inputs(self):
        """Test resolving data with empty inputs"""
        config = {}
        front_matter = {}
        sections = {}
        data = resolve_section_data(config, front_matter, sections)
        assert data == {}

    def test_complete_template_workflow(self):
        """Test complete template parsing workflow"""
        md = """---
title: My Document
author: Jane Doe
---

## Abstract

This is the abstract.

## Introduction

This is the introduction.

## Conclusion

Final thoughts."""
        fm, body = parse_md_for_template(md)
        assert fm["title"] == "My Document"
        assert fm["author"] == "Jane Doe"

        sections = extract_sections(body)
        assert "Abstract" in sections
        assert "Introduction" in sections
        assert "Conclusion" in sections

        config = {
            "content_mapping": {
                "headings": {
                    "Abstract": "abstract",
                    "Introduction": "intro",
                    "Conclusion": "conclusion"
                }
            }
        }
        data = resolve_section_data(config, fm, sections)
        assert data["title"] == "My Document"
        assert data["abstract"] == "This is the abstract."
        assert data["intro"] == "This is the introduction."
        assert data["conclusion"] == "Final thoughts."
