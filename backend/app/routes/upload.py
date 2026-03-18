from pathlib import Path
from uuid import uuid4

from docx import Document
from fastapi import APIRouter, File, HTTPException, UploadFile
from PyPDF2 import PdfReader

from app.services.candidate_service import get_candidate, save_candidate
from app.services.gap_detector import detect_gaps
from app.services.jd_service import save_jd
from app.services.resume_parser import parse_jd, parse_resume

router = APIRouter(tags=["upload"])

BASE_DIR = Path(__file__).resolve().parents[3]
UPLOAD_DIR = BASE_DIR / "uploads"

ALLOWED_EXTENSIONS = {
    ".pdf": {"application/pdf"},
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    },
}


def _validate_upload(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    extension = Path(file.filename).suffix.lower()
    allowed_content_types = ALLOWED_EXTENSIONS.get(extension)
    if allowed_content_types is None:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")

    if file.content_type not in allowed_content_types:
        raise HTTPException(status_code=400, detail="Invalid content type for uploaded file")

    return extension


async def _save_upload(file: UploadFile) -> tuple[str, str]:
    _validate_upload(file)

    resource_id = str(uuid4())
    original_filename = Path(file.filename).name
    stored_filename = f"{resource_id}_{original_filename}"
    destination = UPLOAD_DIR / stored_filename

    content = await file.read()
    destination.write_bytes(content)

    return resource_id, stored_filename


def extract_text(file_path: str) -> str:
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)

    if extension == ".docx":
        document = Document(str(path))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    raise ValueError("Unsupported file format")


@router.post("/upload/resume")
async def upload_resume(file: UploadFile = File(...)):
    _, stored_filename = await _save_upload(file)
    file_path = UPLOAD_DIR / stored_filename

    raw_text = extract_text(str(file_path))
    parsed_data = parse_resume(raw_text)
    parsed_data["employment_gaps"] = detect_gaps(parsed_data.get("experience", []))

    candidate_id = await save_candidate(
        parsed_data=parsed_data,
        file_url=str(file_path),
        session_id=str(uuid4()),
    )
    return {
        "candidate_id": candidate_id,
        "filename": stored_filename,
        "status": "uploaded",
    }


@router.post("/upload/jd")
async def upload_job_description(file: UploadFile = File(...)):
    _, stored_filename = await _save_upload(file)
    file_path = UPLOAD_DIR / stored_filename

    raw_text = extract_text(str(file_path))
    parsed_data = parse_jd(raw_text)
    jd_id = await save_jd(parsed_data=parsed_data, file_url=str(file_path))

    return {
        "jd_id": jd_id,
        "filename": stored_filename,
        "status": "uploaded",
    }


@router.get("/parse/resume/{candidate_id}")
async def get_parsed_resume(candidate_id: str):
    try:
        return await get_candidate(candidate_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
