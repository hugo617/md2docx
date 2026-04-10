from .elements import DocElement, ElementType


def elements_to_md(elements: list[DocElement]) -> str:
    lines = []
    for element in elements:
        md = _element_to_md(element)
        if md:
            lines.append(md)
    return "\n\n".join(lines) + "\n"


def _element_to_md(element: DocElement) -> str:
    match element.element_type:
        case ElementType.HEADING:
            return f"{'#' * element.level} {element.text}"
        case ElementType.PARAGRAPH:
            if element.children:
                return _render_inline_md(element.children)
            return element.text
        case ElementType.BOLD:
            return f"**{element.text}**"
        case ElementType.ITALIC:
            return f"*{element.text}*"
        case ElementType.STRIKETHROUGH:
            return f"~~{element.text}~~"
        case ElementType.CODE_INLINE:
            return f"`{element.text}`"
        case ElementType.CODE_BLOCK:
            return f"```{element.language}\n{element.text}\n```"
        case ElementType.UNORDERED_LIST:
            items = [f"- {item.text}" for item in element.children]
            return "\n".join(items)
        case ElementType.ORDERED_LIST:
            items = [f"1. {item.text}" for item in element.children]
            return "\n".join(items)
        case ElementType.LIST_ITEM:
            prefix = "1." if element.style_name == "ordered_list" else "-"
            return f"{prefix} {element.text}"
        case ElementType.BLOCKQUOTE:
            return f"> {element.text}"
        case ElementType.TABLE:
            return _render_table_md(element)
        case ElementType.IMAGE:
            return f"![{element.alt}]({element.url})"
        case ElementType.HORIZONTAL_RULE:
            return "---"
        case _:
            return element.text


def _render_inline_md(children: list[DocElement]) -> str:
    parts = []
    for child in children:
        parts.append(_element_to_md(child))
    return "".join(parts)


def _render_table_md(element: DocElement) -> str:
    rows = []
    for i, row in enumerate(element.children):
        cells = [cell.text for cell in row.children]
        rows.append("| " + " | ".join(cells) + " |")
        if i == 0:
            rows.append("| " + " | ".join(["---"] * len(cells)) + " |")
    return "\n".join(rows)
