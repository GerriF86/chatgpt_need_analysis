import io
from pathlib import Path
from typing import Union

from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_pdf(file_path_or_bytes: Union[str, bytes]) -> str:
    """
    Extract text from a PDF file given a file path or bytes.
    """
    try:
        if isinstance(file_path_or_bytes, (str, Path)):
            # If a file path is provided
            reader = PdfReader(str(file_path_or_bytes))
        else:
            # If bytes content is provided
            reader = PdfReader(io.BytesIO(file_path_or_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        raise RuntimeError(f"Failed to read PDF file: {e}")
    return text

def extract_text_from_docx(file_path_or_bytes: Union[str, bytes]) -> str:
    """
    Extract text from a DOCX file given a file path or bytes.
    """
    try:
        if isinstance(file_path_or_bytes, (str, Path)):
            doc = Document(file_path_or_bytes)
        else:
            doc = Document(io.BytesIO(file_path_or_bytes))
        text = "\n".join(para.text for para in doc.paragraphs)
    except Exception as e:
        raise RuntimeError(f"Failed to read DOCX file: {e}")
    return text

def extract_text_from_txt(file_path_or_bytes: Union[str, bytes], encoding: str = "utf-8") -> str:
    """
    Read text from a plain text file given a file path or bytes.
    """
    try:
        if isinstance(file_path_or_bytes, (str, Path)):
            with open(file_path_or_bytes, 'r', encoding=encoding) as f:
                text = f.read()
        else:
            text = file_path_or_bytes.decode(encoding, errors='ignore')
    except Exception as e:
        raise RuntimeError(f"Failed to read text file: {e}")
    return text

def parse_file(file: Union[str, bytes, io.IOBase], file_name: str = None) -> str:
    """
    Determine file type and extract text accordingly.
    :param file: File path, bytes, or a file-like object (e.g., an uploaded file).
    :param file_name: Optional file name to help determine file type if file is not a path.
    :return: Extracted text content as a string.
    """
    # If a file-like object is provided, read its content first
    if hasattr(file, 'read') and not isinstance(file, (str, Path, bytes, bytearray)):
        try:
            content = file.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read file-like object: {e}")
        if file_name is None and hasattr(file, 'name'):
            file_name = file.name
        return parse_file(content, file_name)
    # Determine file extension
    ext = None
    if file_name:
        ext = Path(file_name).suffix.lower()
    elif isinstance(file, (str, Path)):
        ext = Path(file).suffix.lower()
    # If no extension is found and we have bytes, attempt to detect PDF signature
    if not ext:
        head_bytes = b''
        if isinstance(file, (bytes, bytearray)):
            head_bytes = file[:5]
        elif hasattr(file, '__iter__') and not isinstance(file, (str, Path)):
            try:
                iterator = iter(file)
                head_bytes = bytes([next(iterator) for _ in range(5)])
            except Exception:
                head_bytes = b''
        if head_bytes.startswith(b'%PDF'):
            ext = '.pdf'
        else:
            ext = '.txt'
    # Dispatch to appropriate extractor based on extension
    if ext == '.pdf':
        return extract_text_from_pdf(file)
    elif ext == '.docx':
        return extract_text_from_docx(file)
    elif ext == '.txt':
        return extract_text_from_txt(file)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
