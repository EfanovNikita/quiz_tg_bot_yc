from aiogram import types, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject, CREATOR
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from service import generate_options_keyboard, get_question, new_quiz, get_quiz_index, update_quiz_index_and_score, get_score, get_question_db

router = Router()

@router.callback_query(F.data.contains("answer"))
async def right_answer(callback: types.CallbackQuery):
    cb_data = callback.data.split(' ')
    current_score = await get_score(callback.from_user.id)
    current_question_index = await get_quiz_index(callback.from_user.id)
    quiz_d = await get_question_db(current_question_index)
    options = quiz_d[0]['options'].split(', ')

    text = f"{callback.message.text} Ваш ответ: {options[int(cb_data[1])]}"

    await callback.bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        text = text,
        reply_markup=None
    )

    if 'right_answer' == cb_data[0]:
        await callback.message.answer("Верно!")
        current_score += 1
    elif 'wrong_answer' == cb_data[0]:
        await callback.message.answer(f"Неправильно. Правильный ответ: {options[int(cb_data[2])]}")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index_and_score(callback.from_user.id, current_question_index, current_score)

    await get_question(callback.message, callback.from_user.id)


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


# Хэндлер на команду /quiz
@router.message(F.text=="Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)
    

