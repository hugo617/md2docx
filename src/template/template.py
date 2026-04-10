import os
import yaml


def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_md_for_template(md_content: str) -> tuple[dict, str]:
    """解析含 YAML front matter 的 Markdown

    Returns:
        (front_matter_data, body_content)
    """
    if not md_content.startswith("---"):
        return {}, md_content

    parts = md_content.split("---", 2)
    if len(parts) < 3:
        return {}, md_content

    front_matter = yaml.safe_load(parts[1])
    body = parts[2].strip()
    return front_matter or {}, body


def extract_sections(body: str) -> dict[str, str]:
    """按 ## 二级标题分节提取正文内容

    Returns:
        {heading_text: section_content}
    """
    sections = {}
    current_heading = None
    current_lines = []

    for line in body.split("\n"):
        if line.startswith("## "):
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_heading is not None:
        sections[current_heading] = "\n".join(current_lines).strip()

    return sections


def resolve_section_data(
    config: dict, front_matter: dict, sections: dict[str, str]
) -> dict[str, str]:
    """合并 front matter 和 section 数据为统一 data dict

    Args:
        config: 模板配置 (fields 定义)
        front_matter: YAML front matter 键值对
        sections: {heading: content} 分节内容

    Returns:
        {field_name: text} 统一数据映射
    """
    data = dict(front_matter)

    content_mapping = config.get("content_mapping", {})
    headings_map = content_mapping.get("headings", {})

    for heading_text, field_name in headings_map.items():
        if heading_text in sections:
            data[field_name] = sections[heading_text]

    return data


def find_template_dir(template_name: str, search_paths: list[str] | None = None) -> str | None:
    """查找模板目录"""
    paths = search_paths or ["templates", os.path.join(os.path.dirname(__file__), "..", "templates")]
    for base in paths:
        tpl_dir = os.path.join(base, template_name)
        if os.path.isdir(tpl_dir):
            return tpl_dir
    return None
