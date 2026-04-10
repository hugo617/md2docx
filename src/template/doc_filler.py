from docxtpl import DocxTemplate


def fill_doc_template(
    template_path: str,
    data: dict,
    output_path: str,
) -> str:
    """用 docxtpl (Jinja2) 填充 .docx 模板

    模板中使用 {{ variable }} 占位符。

    Args:
        template_path: .docx 模板 (含 Jinja2 占位符)
        data: {variable_name: value} 数据字典
        output_path: 输出路径

    Returns:
        生成的文件路径
    """
    tpl = DocxTemplate(template_path)
    tpl.render(data)
    tpl.save(output_path)
    return output_path
