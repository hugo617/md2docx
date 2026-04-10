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
    print("fill command - TODO (Phase 3)")


def cmd_extract(args):
    print("extract command - TODO (Phase 2)")


def cmd_template(args):
    if args.tpl_command == "list":
        print("template list - TODO (Phase 3)")
    elif args.tpl_command == "init":
        print("template init - TODO (Phase 3)")
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
