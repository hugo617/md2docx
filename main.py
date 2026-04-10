import argparse
import os
import sys


def cmd_convert(args):
    from src.util.file_util import read
    from src.core.parser import parse_md_to_elements
    from src.core.renderer import render_to_docx

    md_content = read(args.filepath)

    output = args.output
    if not output:
        base = os.path.splitext(args.filepath)[0]
        output = base + ".docx"

    elements = parse_md_to_elements(md_content)
    render_to_docx(elements, output)
    print(f"Generated: {output}")


def cmd_fill(args):
    from src.util.file_util import read
    from src.template.template import load_config, parse_md_for_template, extract_sections, resolve_section_data
    from src.template.table_filler import fill_table_template

    md_content = read(args.filepath)
    front_matter, body = parse_md_for_template(md_content)
    sections = extract_sections(body)

    config_path = args.config
    if not config_path:
        tpl_dir = os.path.dirname(args.template)
        config_path = os.path.join(tpl_dir, "config.yaml")

    config = load_config(config_path)
    data = resolve_section_data(config, front_matter, sections)

    output = args.output
    if not output:
        base = os.path.splitext(args.filepath)[0]
        output = base + "_filled.docx"

    fill_table_template(args.template, config, data, output)
    print(f"Generated: {output}")


def cmd_extract(args):
    from src.core.extractor import extract_docx_to_elements
    from src.core.md_writer import elements_to_md
    from src.util.file_util import write

    elements, images = extract_docx_to_elements(args.filepath)
    md_content = elements_to_md(elements)

    output = args.output
    if not output:
        base = os.path.splitext(args.filepath)[0]
        output = base + "_extracted.md"

    write(output, md_content)
    print(f"Generated: {output}")
    if images:
        print(f"Extracted {len(images)} images")


def cmd_template(args):
    import shutil
    import yaml
    from docx import Document

    if args.tpl_command == "list":
        tpl_dir = "templates"
        if os.path.isdir(tpl_dir):
            for name in os.listdir(tpl_dir):
                path = os.path.join(tpl_dir, name)
                if os.path.isdir(path):
                    has_config = os.path.exists(os.path.join(path, "config.yaml"))
                    print(f"  {name} {'(configured)' if has_config else '(no config)'}")
        else:
            print("No templates directory found.")
    elif args.tpl_command == "init":
        name = args.name
        filepath = args.filepath
        tpl_dir = os.path.join("templates", name)
        os.makedirs(tpl_dir, exist_ok=True)
        shutil.copy(filepath, os.path.join(tpl_dir, "template.docx"))

        doc = Document(filepath)
        fields = []
        for ti, table in enumerate(doc.tables):
            for ri, row in enumerate(table.rows):
                seen = set()
                for ci, cell in enumerate(row.cells):
                    tc_id = id(cell._tc)
                    if tc_id in seen:
                        continue
                    seen.add(tc_id)
                    text = cell.text.strip()
                    if text:
                        fields.append({
                            "name": f"field_{ti}_{ri}_{ci}",
                            "table": ti, "row": ri, "col": ci,
                            "label": text,
                        })

        config = {
            "name": name,
            "mode": "table_fill",
            "template": "template.docx",
            "fields": fields,
        }
        config_path = os.path.join(tpl_dir, "config.yaml")
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        print(f"Template initialized: {tpl_dir}")
        print(f"Config generated: {config_path}")
        print(f"Found {len(fields)} fields - edit config.yaml to customize")
    else:
        print("Usage: md2docx template {list|init}")


def cmd_web(args):
    print("web command - TODO (Phase 5)")


def main():
    parser = argparse.ArgumentParser(
        prog="md2docx",
        description="Markdown <-> Word (.docx) 双向转换工具",
    )
    subparsers = parser.add_subparsers(dest="command")

    p_convert = subparsers.add_parser("convert", help="Markdown 转 Word")
    p_convert.add_argument("filepath", help="Markdown 文件路径")
    p_convert.add_argument("-o", "--output", help="输出 .docx 路径")
    p_convert.add_argument("-s", "--style", default="default", help="样式配置名")

    p_fill = subparsers.add_parser("fill", help="模板填充")
    p_fill.add_argument("filepath", help="Markdown 文件路径")
    p_fill.add_argument("-t", "--template", required=True, help=".docx 模板路径")
    p_fill.add_argument("-c", "--config", help="字段映射 config.yaml")
    p_fill.add_argument("-o", "--output", help="输出 .docx 路径")

    p_extract = subparsers.add_parser("extract", help="Word 转 Markdown")
    p_extract.add_argument("filepath", help=".docx 文件路径")
    p_extract.add_argument("-o", "--output", help="输出 .md 路径")
    p_extract.add_argument("--img-dir", help="图片提取目录")

    p_tpl = subparsers.add_parser("template", help="模板管理")
    p_tpl_sub = p_tpl.add_subparsers(dest="tpl_command")
    p_tpl_sub.add_parser("list", help="列出可用模板")
    p_tpl_init = p_tpl_sub.add_parser("init", help="从 .docx 生成配置")
    p_tpl_init.add_argument("name", help="模板名称")
    p_tpl_init.add_argument("filepath", help=".docx 模板文件")

    p_web = subparsers.add_parser("web", help="启动 Web UI")
    p_web.add_argument("--host", default="127.0.0.1")
    p_web.add_argument("--port", type=int, default=8080)

    args = parser.parse_args()

    if args.command == "convert":
        cmd_convert(args)
    elif args.command == "fill":
        cmd_fill(args)
    elif args.command == "extract":
        cmd_extract(args)
    elif args.command == "template":
        cmd_template(args)
    elif args.command == "web":
        cmd_web(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
