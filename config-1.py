import os
from dotenv import load_dotenv

load_dotenv()

# توكن البوت من BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")

# آيدي الأدمن (رقمك في تيليجرام) - للوصول للوحة التحكم /admin
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "0").split(",") if x.strip()]

# مفتاح API الخاص بخدمة الذكاء الاصطناعي
# نستخدم Groq بشكل افتراضي: مجاني 100%، بلا بطاقة بنكية، وسريع جدا.
# احصل على مفتاحك من console.groq.com (تسجيل بإيميلك فقط)
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_API_BASE = os.getenv("AI_API_BASE", "https://api.groq.com/openai/v1")
AI_MODEL = os.getenv("AI_MODEL", "llama-3.3-70b-versatile")

# عدد الطلبات المجانية يوميا للمستخدم العادي
FREE_DAILY_CREDITS = 5

# سعر الاشتراك المميز بعملة Stars (XTR) - شهر كامل
PREMIUM_PRICE_STARS = 150  # ~ 3$ تقريبا، عدل الرقم كيما تحب

# عدد الردود المجانية بينهم يظهر إعلان ممول (0 = تعطيل)
ADS_EVERY_N_REPLIES = 3

# مكافأة الإحالة: عدد الطلبات الإضافية اللي ياخذها من دعا صديق جديد
REFERRAL_BONUS_CREDITS = 5

DB_PATH = "bot_database.db"
