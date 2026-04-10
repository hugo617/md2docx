import os
import uuid
from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse

from src.util.file_util import read, write
from src.core.parser import parse_md_to_elements
from src.core.renderer import render_to_docx
from src.core.extractor import extract_docx_to_elements
from src.core.md_writer import elements_to_md
from src.template.template import load_config, parse_md_for_template, extract_sections, resolve_section_data
from src.template.table_filler import fill_table_template

router = APIRouter()

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

tasks: dict[str, str] = {}


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    from . import templates
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/api/convert")
async def api_convert(file: UploadFile = File(...)):
    task_id = uuid.uuid4().hex[:8]
    md_path = os.path.join(OUTPUT_DIR, f"{task_id}.md")
    docx_path = os.path.join(OUTPUT_DIR, f"{task_id}.docx")

    content = await file.read()
    write(md_path, content.decode("utf-8"))

    md_content = content.decode("utf-8")
    elements = parse_md_to_elements(md_content)
    render_to_docx(elements, docx_path)

    tasks[task_id] = docx_path
    return {"task_id": task_id, "filename": os.path.basename(docx_path)}


@router.post("/api/extract")
async def api_extract(file: UploadFile = File(...)):
    task_id = uuid.uuid4().hex[:8]
    docx_path = os.path.join(OUTPUT_DIR, f"{task_id}_input.docx")
    md_path = os.path.join(OUTPUT_DIR, f"{task_id}.md")

    content = await file.read()
    with open(docx_path, "wb") as f:
        f.write(content)

    elements, images = extract_docx_to_elements(docx_path)
    md_content = elements_to_md(elements)
    write(md_path, md_content)

    tasks[task_id] = md_path
    return {"task_id": task_id, "filename": os.path.basename(md_path)}


@router.get("/api/download/{task_id}")
async def api_download(task_id: str):
    filepath = tasks.get(task_id)
    if not filepath or not os.path.exists(filepath):
        return {"error": "File not found"}
    return FileResponse(filepath, filename=os.path.basename(filepath))


@router.get("/api/templates")
async def api_templates():
    tpl_dir = "templates"
    result = []
    if os.path.isdir(tpl_dir):
        for name in os.listdir(tpl_dir):
            path = os.path.join(tpl_dir, name)
            if os.path.isdir(path):
                has_config = os.path.exists(os.path.join(path, "config.yaml"))
                result.append({"name": name, "configured": has_config})
    return result
