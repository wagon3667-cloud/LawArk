from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ..utils.keyboards import get_main_menu, get_consultation_type_menu, get_healthark_promo
from ..utils.prompts import HEALTHARK_PROMO
from ..database.database import Database
from ..services.ai_service import AIService
from ..services.subscription_service import SubscriptionService

router = Router()

class ConsultationStates(StatesGroup):
    waiting_question = State()
    waiting_document = State()

# Счетчик консультаций для кросс-промо
consultation_counters = {}

@router.message(F.text == "💬 Задать вопрос")
async def start_consultation(message: Message, state: FSMContext):
    """Начать консультацию"""
    db = Database()
    subscription_service = SubscriptionService(db)
    
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
        "💬 Выберите тип консультации:",
        reply_markup=get_consultation_type_menu()
    )
    await state.set_state(ConsultationStates.waiting_question)

@router.message(F.text == "📝 Текстовый вопрос")
async def text_consultation(message: Message, state: FSMContext):
    """Текстовая консультация"""
    await message.answer(
        "📝 Опишите ваш юридический вопрос:\n\n"
        "💡 Примеры:\n"
        "• Как расторгнуть договор?\n"
        "• Какие права у работника при увольнении?\n"
        "• Как оформить наследство?\n\n"
        "Жду ваш вопрос...",
        reply_markup=get_main_menu()
    )
    await state.set_state(ConsultationStates.waiting_question)

@router.message(F.text == "📄 Загрузить документ")
async def document_consultation(message: Message, state: FSMContext):
    """Консультация по документу"""
    await message.answer(
        "📄 Загрузите документ для анализа:\n\n"
        "📋 Поддерживаемые форматы:\n"
        "• Изображения: JPG, PNG\n"
        "• Документы: PDF, DOCX\n\n"
        "⚠️ Максимальный размер: 20MB",
        reply_markup=get_main_menu()
    )
    await state.set_state(ConsultationStates.waiting_document)

@router.message(ConsultationStates.waiting_question)
async def process_question(message: Message, state: FSMContext):
    """Обработать вопрос пользователя"""
    question = message.text.strip()
    
    if len(question) < 10:
        await message.answer(
            "❌ Вопрос слишком короткий. Пожалуйста, опишите вашу ситуацию подробнее.",
            reply_markup=get_main_menu()
        )
        return
    
    # Показываем, что обрабатываем
    processing_msg = await message.answer("🤖 Анализирую ваш вопрос...")
    
    try:
        # Проверяем, что вопрос юридический
        ai_service = AIService()
        is_legal = await ai_service.is_legal_question(question)
        
        if not is_legal:
            await processing_msg.edit_text(
                "❌ Вопрос не относится к юридической тематике. "
                "Пожалуйста, задайте вопрос о праве, законах или правовых ситуациях.",
                reply_markup=get_main_menu()
            )
            await state.clear()
            return
        
        # Получаем консультацию
        answer = await ai_service.get_consultation(question)
        
        # Сохраняем в базу данных
        db = Database()
        await db.add_consultation(
            message.from_user.id,
            question,
            answer,
            "text"
        )
        
        # Обновляем счетчик для кросс-промо
        user_id = message.from_user.id
        consultation_counters[user_id] = consultation_counters.get(user_id, 0) + 1
        
        await processing_msg.edit_text(answer)
        
        # Показываем кросс-промо каждую 3-ю консультацию
        if consultation_counters[user_id] % 3 == 0:
            await message.answer(
                HEALTHARK_PROMO,
                reply_markup=get_healthark_promo()
            )
        
    except Exception as e:
        print(f"Consultation error: {e}")
        await processing_msg.edit_text(
            "❌ Произошла ошибка при обработке вопроса. Попробуйте позже.",
            reply_markup=get_main_menu()
        )
    
    await state.clear()

@router.message(ConsultationStates.waiting_document)
async def process_document(message: Message, state: FSMContext):
    """Обработать документ"""
    if not message.document and not message.photo:
        await message.answer(
            "❌ Пожалуйста, загрузите документ или изображение.",
            reply_markup=get_main_menu()
        )
        return
    
    # Показываем, что обрабатываем
    processing_msg = await message.answer("📄 Обрабатываю документ...")
    
    try:
        from ..services.ocr_service import OCRService
        from ..handlers.documents import process_uploaded_file
        
        # Используем общую логику обработки файлов
        result = await process_uploaded_file(message, processing_msg)
        
        if result:
            # Сохраняем в базу данных
            db = Database()
            await db.add_consultation(
                message.from_user.id,
                f"Анализ документа: {message.document.file_name if message.document else 'изображение'}",
                result,
                "document"
            )
            
            # Обновляем счетчик для кросс-промо
            user_id = message.from_user.id
            consultation_counters[user_id] = consultation_counters.get(user_id, 0) + 1
            
            # Показываем кросс-промо каждую 3-ю консультацию
            if consultation_counters[user_id] % 3 == 0:
                await message.answer(
                    HEALTHARK_PROMO,
                    reply_markup=get_healthark_promo()
                )
        
    except Exception as e:
        print(f"Document processing error: {e}")
        await processing_msg.edit_text(
            "❌ Произошла ошибка при обработке документа. Попробуйте позже.",
            reply_markup=get_main_menu()
        )
    
    await state.clear()

@router.message(F.text == "🔙 Главное меню")
async def back_to_main(message: Message, state: FSMContext):
    """Вернуться в главное меню"""
    await message.answer(
        "⚖️ LawArk - Ваш AI-юрист 24/7\n\nВыберите действие:",
        reply_markup=get_main_menu()
    )
    await state.clear()
