from openai import AsyncOpenAI
from config import AI_API_KEY, AI_API_BASE, AI_MODEL

client = AsyncOpenAI(api_key=AI_API_KEY, base_url=AI_API_BASE)

SYSTEM_PROMPT = (
    "أنت مساعد ذكي اسمه 'العقل'، تجاوب باللهجة العربية الواضحة (فصحى مبسطة)، "
    "مختصر، مفيد، ودقيق. تساعد المستخدم في التلخيص، الترجمة، الإجابة عن أسئلة دراسية، "
    "وكتابة نصوص. لا تتحدث عن كونك نموذج OpenAI، فقط قدم المساعدة."
)


async def ask_ai(user_message: str) -> str:
    try:
        response = await client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            max_tokens=800,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ صار خطأ فالاتصال بالذكاء الاصطناعي، حاول مرة أخرى بعد شوي.\n({e})"
