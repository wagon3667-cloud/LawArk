from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ..utils.keyboards import get_main_menu
from ..utils.config import SUPPORTED_IMAGE_TYPES, SUPPORTED_DOCUMENT_TYPES, MAX_FILE_SIZE_MB
from ..services.ocr_service import OCRService
from ..services.ai_service import AIService
from ..database.database import Database

router = Router()

@router.message(F.text == "📄 Анализ документа")
async def start_document_analysis(message: Message, state: FSMContext):
    """Начать анализ документа"""
    db = Database()
    
    # Проверяем возможность консультации
    can_consult = await db.can_user_consult(message.from_user.id)
    
    if not can_consult['can_consult']:
        if can_consult['reason'] == 'subscription_expired':
            await message.answer(
                "⏰ Ваша подписка истекла. Оформите новую подписку для продолжения.",
                reply_markup=get_main_menu()
            )
        elif can_consult['reason'] == 'consultations_limit':
            await message.answer(
                f"📊 {can_consult['message']}. Оформите подписку с большим лимитом.",
                reply_markup=get_main_menu()
            )
        return
    
    await message.answer(
        "📄 Загрузите документ для анализа:\n\n"
        "📋 Поддерживаемые форматы:\n"
        "• Изображения: JPG, PNG\n"
        "• Документы: PDF, DOCX\n\n"
        f"⚠️ Максимальный размер: {MAX_FILE_SIZE_MB}MB",
        reply_markup=get_main_menu()
    )

@router.message(F.photo)
async def handle_photo(message: Message):
    """Обработать загруженное фото"""
    processing_msg = await message.answer("📸 Обрабатываю изображение...")
    await process_uploaded_file(message, processing_msg)

@router.message(F.document)
async def handle_document(message: Message):
    """Обработать загруженный документ"""
    if not message.document:
        return
    
    # Проверяем тип файла
    mime_type = message.document.mime_type
    
    if mime_type not in SUPPORTED_IMAGE_TYPES + SUPPORTED_DOCUMENT_TYPES:
        await message.answer(
            "❌ Неподдерживаемый формат файла.\n\n"
            "📋 Поддерживаются:\n"
            "• Изображения: JPG, PNG\n"
            "• Документы: PDF, DOCX",
            reply_markup=get_main_menu()
        )
        return
    
    # Проверяем размер файла
    file_size_mb = message.document.file_size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        await message.answer(
            f"❌ Файл слишком большой ({file_size_mb:.1f}MB).\n"
            f"Максимальный размер: {MAX_FILE_SIZE_MB}MB",
            reply_markup=get_main_menu()
        )
        return
    
    processing_msg = await message.answer("📄 Обрабатываю документ...")
    await process_uploaded_file(message, processing_msg)

async def process_uploaded_file(message: Message, processing_msg):
    """Обработать загруженный файл"""
    try:
        # Скачиваем файл
        file_bytes = await download_file(message)
        if not file_bytes:
            await processing_msg.edit_text(
                "❌ Ошибка скачивания файла. Попробуйте позже.",
                reply_markup=get_main_menu()
            )
            return None
        
        # Определяем тип файла
        mime_type = get_file_mime_type(message)
        
        # Извлекаем текст
        ocr_service = OCRService()
        document_text = await ocr_service.extract_text_from_file(file_bytes, mime_type)
        
        if not document_text or len(document_text.strip()) < 10:
            await processing_msg.edit_text(
                "❌ Не удалось извлечь текст из документа. "
                "Попробуйте другое изображение или документ с более четким текстом.",
                reply_markup=get_main_menu()
            )
            return None
        
        # Анализируем документ с помощью AI
        ai_service = AIService()
        analysis = await ai_service.analyze_document(document_text)
        
        await processing_msg.edit_text(analysis)
        return analysis
        
    except Exception as e:
        print(f"Document processing error: {e}")
        await processing_msg.edit_text(
            "❌ Произошла ошибка при обработке документа. Попробуйте позже.",
            reply_markup=get_main_menu()
        )
        return None

async def download_file(message: Message) -> bytes:
    """Скачать файл"""
    try:
        if message.photo:
            # Для фото берем самое большое разрешение
            file_id = message.photo[-1].file_id
        elif message.document:
            file_id = message.document.file_id
        else:
            return None
        
        # Скачиваем файл
        file = await message.bot.get_file(file_id)
        file_bytes = await message.bot.download_file(file.file_path)
        
        return file_bytes.read()
        
    except Exception as e:
        print(f"Download error: {e}")
        return None

def get_file_mime_type(message: Message) -> str:
    """Получить MIME тип файла"""
    if message.photo:
        return "image/jpeg"  # Telegram конвертирует все фото в JPEG
    elif message.document:
        return message.document.mime_type
    else:
        return "unknown"
