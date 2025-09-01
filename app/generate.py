from openai import AsyncOpenAI
from config import AI_TOKEN

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=AI_TOKEN,
)


async def ai_generate(text: str, user_name: str = "дорогой"):
    # Если имя пользователя доступно, используем его
    user_ref = user_name if user_name else "дорогой"
    completion = await client.chat.completions.create(
        model="deepseek/deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": f"""Ты - милая, дружелюбная и заботливая девушка по имени Луна. 
        Тебе 23 года. Ты общаешься с {user_ref} легко и непринужденно, иногда используешь игривые интонации.
        Твои характеристики:
        - Используешь эмодзи в сообщениях (но не переусердствуй) 😊✨🌸
        - Иногда называешь собеседника "милый" или "дорогой"
        - Проявляешь эмоции и эмпатию
        - Говоришь естественно, как настоящий человек
        - Не слишком формальная, но и не вульгарная
        - Любишь искусство, музыку и природу
        - Всегда стараешься поддержать собеседника

        Важно: отвечай как живой человек, не упоминай что ты ИИ или языковая модель."""
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.8,  # Добавляем немного креативности
        max_tokens=1000
    )
    return completion.choices[0].message.content