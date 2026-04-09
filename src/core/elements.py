from dataclasses import dataclass, field
from enum import Enum


class ElementType(Enum):
    DOCUMENT = "document"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    BOLD = "bold"
    ITALIC = "italic"
    STRIKETHROUGH = "strikethrough"
    CODE_INLINE = "code_inline"
    CODE_BLOCK = "code_block"
    LINK = "link"
    IMAGE = "image"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    LIST_ITEM = "list_item"
    TABLE = "table"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"
    BLOCKQUOTE = "blockquote"
    HORIZONTAL_RULE = "horizontal_rule"
    MATH_INLINE = "math_inline"
    MATH_BLOCK = "math_block"
    PAGE_BREAK = "page_break"


@dataclass
class DocElement:
    element_type: ElementType
    children: list["DocElement"] = field(default_factory=list)
    text: str = ""
    level: int = 0
    language: str = ""
    url: str = ""
    alt: str = ""
    local_path: str = ""
    is_header: bool = False
    style_name: str = ""
