import pytesseract
from PIL import Image
import io
import asyncio
import PyPDF2
from docx import Document
from typing import Optional, Union
from ..utils.config import SUPPORTED_IMAGE_TYPES, SUPPORTED_DOCUMENT_TYPES, MAX_FILE_SIZE_MB

class OCRService:
    def __init__(self):
        # Настройка Tesseract для русского языка
        self.tesseract_config = '--oem 3 --psm 6 -l rus+eng'
        
    async def extract_text_from_image(self, image_bytes: bytes) -> Optional[str]:
        """Извлечь текст из изображения"""
        try:
            # Запускаем OCR в отдельном потоке
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                None, 
                self._extract_text_sync, 
                image_bytes
            )
            return text
        except Exception as e:
            print(f"OCR error: {e}")
            return None
    
    def _extract_text_sync(self, image_bytes: bytes) -> str:
        """Синхронное извлечение текста"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Улучшаем качество изображения для OCR
            image = image.convert('RGB')
            text = pytesseract.image_to_string(image, config=self.tesseract_config)
            return text.strip()
        except Exception as e:
            print(f"OCR sync error: {e}")
            return ""
    
    async def extract_text_from_pdf(self, pdf_bytes: bytes) -> Optional[str]:
        """Извлечь текст из PDF"""
        try:
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                None,
                self._extract_pdf_text_sync,
                pdf_bytes
            )
            return text
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return None
    
    def _extract_pdf_text_sync(self, pdf_bytes: bytes) -> str:
        """Синхронное извлечение текста из PDF"""
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            print(f"PDF sync error: {e}")
            return ""
    
    async def extract_text_from_docx(self, docx_bytes: bytes) -> Optional[str]:
        """Извлечь текст из DOCX"""
        try:
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                None,
                self._extract_docx_text_sync,
                docx_bytes
            )
            return text
        except Exception as e:
            print(f"DOCX extraction error: {e}")
            return None
    
    def _extract_docx_text_sync(self, docx_bytes: bytes) -> str:
        """Синхронное извлечение текста из DOCX"""
        try:
            docx_file = io.BytesIO(docx_bytes)
            doc = Document(docx_file)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            print(f"DOCX sync error: {e}")
            return ""
    
    async def extract_text_from_file(self, file_bytes: bytes, mime_type: str) -> Optional[str]:
        """Универсальный метод извлечения текста"""
        if mime_type in SUPPORTED_IMAGE_TYPES:
            return await self.extract_text_from_image(file_bytes)
        elif mime_type == "application/pdf":
            return await self.extract_text_from_pdf(file_bytes)
        elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return await self.extract_text_from_docx(file_bytes)
        else:
            return None
    
    def validate_file_size(self, file_size: int) -> bool:
        """Проверить размер файла"""
        max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
        return file_size <= max_size_bytes
    
    def get_file_type_info(self, mime_type: str) -> dict:
        """Получить информацию о типе файла"""
        if mime_type in SUPPORTED_IMAGE_TYPES:
            return {"type": "image", "supported": True}
        elif mime_type in SUPPORTED_DOCUMENT_TYPES:
            return {"type": "document", "supported": True}
        else:
            return {"type": "unknown", "supported": False}
