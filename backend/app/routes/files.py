from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter()

MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_TEXT_CHARS = 120_000
ALLOWED = {
    "text/plain",
    "text/markdown",
    "text/csv",
    "application/json",
    "application/pdf",
}


def _extract_pdf(data: bytes) -> str:
    try:
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(data))
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not read PDF: {exc}") from exc


@router.post("/files/upload")
async def upload_file(file: Annotated[UploadFile, File()]) -> dict[str, str | int]:
    if file.content_type not in ALLOWED:
        raise HTTPException(status_code=415, detail="Supported files: PDF, TXT, MD, CSV, JSON")
    data = await file.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="File is larger than 8 MB")

    if file.content_type == "application/pdf" or Path(file.filename or "").suffix.lower() == ".pdf":
        text = _extract_pdf(data)
    else:
        text = data.decode("utf-8", errors="replace")

    text = text[:MAX_TEXT_CHARS].strip()
    return {
        "filename": file.filename or "uploaded-file",
        "content_type": file.content_type or "application/octet-stream",
        "characters": len(text),
        "text": text,
    }
