from  database import pool, execute_update_query, execute_select_query
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types
import json


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for i, option in enumerate(answer_options):
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"right_answer {i}" if i == right_answer else f"wrong_answer {i} {right_answer}")
        )

    builder.adjust(1)
    return builder.as_markup()



async def get_question(message, user_id):
    
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    quiz_d = await get_question_db(current_question_index)
    print(current_question_index)

    if len(quiz_d) == 0:
        score = await get_score(user_id)
        await message.answer("Это был последний вопрос. Квиз завершен!")
        await message.answer(f"Количество правильных ответов: {score} из {current_question_index}")
        return
    
    question = quiz_d[0]['question']
    options = quiz_d[0]['options'].split(', ')
    correct_option = quiz_d[0]['correct_option']

    kb = generate_options_keyboard(options, correct_option)
    await message.answer(f"{question}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    current_score = 0
    await message.answer_photo(
        types.URLInputFile('https://storage.yandexcloud.net/quiz-b/quiz_python.jpg')
    )
    await update_quiz_index_and_score(user_id, current_question_index, current_score)
    await get_question(message, user_id)


async def get_quiz_index(user_id):
    get_user_index = f"""
        DECLARE $user_id AS Uint64;

        SELECT question_index
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["question_index"] is None:
        return 0
    return results[0]["question_index"]

async def get_question_db(question_index):
    get_q = f"""
    DECLARE $question_index AS Uint64;

    SELECT * FROM `question_state`
    WHERE question_index == $question_index;
    """
    result = execute_select_query(pool, get_q, question_index=question_index)

    return result

async def get_score(user_id):
    get_score = f"""
        DECLARE $user_id AS Uint64;

        SELECT score
        FROM `quiz_state`
        WHERE user_id = $user_id;
    """
    results = execute_select_query(pool, get_score, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["score"] is None:
        return 0
    return results[0]["score"]

    

async def update_quiz_index_and_score(user_id, index, score):
    set_quiz_state = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $index AS Uint64;
        DECLARE $score AS Uint64;

        UPSERT INTO `quiz_state` (`user_id`, `question_index`, `score`)
        VALUES ($user_id, $index, $score);
    """

    execute_update_query(
        pool,
        set_quiz_state,
        user_id=user_id,
        index=index,
        score=score,
    )
