from pyquery import PyQuery

from src.util.md_util import md_to_html
from .elements import DocElement, ElementType


def parse_md_to_elements(md_content: str) -> list[DocElement]:
    html = md_to_html(md_content)
    doc = PyQuery(f"<div>{html}</div>")
    return [_parse_node(PyQuery(child)) for child in doc.children().items()]


def _parse_node(node: PyQuery) -> DocElement:
    tag = node[0].tag

    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        return DocElement(
            element_type=ElementType.HEADING,
            text=node.text(),
            level=int(tag[1]),
        )

    if tag == "p":
        children = _parse_inline_children(node)
        if len(children) == 1 and children[0].element_type == ElementType.PARAGRAPH:
            return children[0]
        return DocElement(element_type=ElementType.PARAGRAPH, children=children)

    if tag == "pre":
        code_el = node("code")
        language = ""
        if code_el:
            cls = code_el.attr("class") or ""
            if cls.startswith("language-"):
                language = cls[9:]
            text = code_el.text()
        else:
            text = node.text()
        return DocElement(element_type=ElementType.CODE_BLOCK, text=text, language=language)

    if tag in ("ul", "ol"):
        element_type = ElementType.UNORDERED_LIST if tag == "ul" else ElementType.ORDERED_LIST
        items = [
            DocElement(element_type=ElementType.LIST_ITEM, text=PyQuery(li).text())
            for li in node.children("li").items()
        ]
        return DocElement(element_type=element_type, children=items)

    if tag == "blockquote":
        inner_html = node.html()
        if inner_html:
            inner_elements = parse_md_to_elements(inner_html) if '<' in inner_html else []
            if inner_elements:
                return DocElement(element_type=ElementType.BLOCKQUOTE, children=inner_elements)
        return DocElement(element_type=ElementType.BLOCKQUOTE, text=node.text())

    if tag == "table":
        return _parse_table(node)

    if tag == "hr":
        return DocElement(element_type=ElementType.HORIZONTAL_RULE)

    if tag == "img":
        return DocElement(
            element_type=ElementType.IMAGE,
            alt=node.attr("alt") or "",
            url=node.attr("src") or "",
        )

    if tag == "div":
        children = [_parse_node(PyQuery(c)) for c in node.children().items()]
        if len(children) == 1:
            return children[0]
        return DocElement(element_type=ElementType.DOCUMENT, children=children)

    return DocElement(element_type=ElementType.PARAGRAPH, text=node.text())


def _parse_inline_children(node: PyQuery) -> list[DocElement]:
    children = []
    for child in node.children().items():
        tag = child[0].tag
        if tag in ("strong", "b"):
            children.append(DocElement(element_type=ElementType.BOLD, text=child.text()))
        elif tag in ("em", "i"):
            children.append(DocElement(element_type=ElementType.ITALIC, text=child.text()))
        elif tag == "code":
            children.append(DocElement(element_type=ElementType.CODE_INLINE, text=child.text()))
        elif tag == "a":
            children.append(DocElement(
                element_type=ElementType.LINK, text=child.text(), url=child.attr("href") or ""
            ))
        elif tag == "del":
            children.append(DocElement(element_type=ElementType.STRIKETHROUGH, text=child.text()))
        elif tag == "img":
            children.append(DocElement(
                element_type=ElementType.IMAGE,
                alt=child.attr("alt") or "",
                url=child.attr("src") or "",
            ))
        else:
            text = child.text()
            if text:
                children.append(DocElement(element_type=ElementType.PARAGRAPH, text=text))
    if not children:
        text = node.text()
        if text:
            children.append(DocElement(element_type=ElementType.PARAGRAPH, text=text))
    return children


def _parse_table(node: PyQuery) -> DocElement:
    rows = []
    for tr in node("tr").items():
        cells = []
        for cell in tr("th, td").items():
            cells.append(DocElement(
                element_type=ElementType.TABLE_CELL,
                text=cell.text(),
                is_header=cell[0].tag == "th",
            ))
        rows.append(DocElement(element_type=ElementType.TABLE_ROW, children=cells))
    return DocElement(element_type=ElementType.TABLE, children=rows)
