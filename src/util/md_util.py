import re
from typing import List, Union, Callable, Tuple

from markdown import markdown
from markdown import Extension
from markdown.blockprocessors import BlockProcessor
import xml.etree.ElementTree as etree


def process_images(content: str, func: Callable[[str], Tuple[str, bool]]) -> str:
    def modify(match):
        tar = match.group()
        if tar[-1] == ")":
            pre = tar[: tar.index("(") + 1]
            mid = tar[tar.index("(") + 1 : -1]
            suf = tar[-1]
        else:
            mid = re.search(r'src="([^"]*)"', tar).group(1)
            pre, suf = tar.split(mid)
        new_name, err = func(mid)
        return pre + (new_name if not err else mid) + suf

    pattern = r"!\[.*?\]\((.*?)\)|<img.*?src=[\'\"](.*?)[\'\"].*?>"
    return re.sub(pattern, modify, content)


def md_to_html(md: str) -> str:
    class BoxBlockProcessor(BlockProcessor):
        first = True

        def run(self, parent, blocks):
            if self.first:
                self.first = False
                e = etree.SubElement(parent, "div")
                self.parser.parseBlocks(e, blocks)
                for _ in range(len(blocks)):
                    blocks.pop(0)
                return True
            return False

    class BoxExtension(Extension):
        def extendMarkdown(self, md):
            md.parser.blockprocessors.register(
                BoxBlockProcessor(md.parser), "box", 175
            )

    extensions: List[Union[str, BoxExtension]] = [
        BoxExtension(),
        "meta",
        "fenced_code",
        "codehilite",
        "extra",
        "attr_list",
        "tables",
        "toc",
    ]
    return markdown(md, extensions=extensions)
