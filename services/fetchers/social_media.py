from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=api_key)


async def fetch_social_media(project_name: str, website: str) -> str:
    prompt = f"""
Kamu adalah analis investigatif crypto.

Analisa dan tampilkan overview aktivitas sosial media proyek berikut:

Proyek: {project_name}  
Website: {website}

📌 Tampilkan:
- Link resmi Twitter, Telegram, Discord
- Tools analitik (LunarCrush, SocialBlade, dsb)
- Thread penting, engagement tinggi
- Reaksi komunitas (positif, FUD, netral)
- Influencer yang menyebutkan proyek
- Link referensi dan screenshot data jika tersedia

Buat output dalam format Markdown. Sertakan minimal 5 referensi link.
"""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Kamu adalah pakar analisis investigatif dalam dunia cryptocurrency dan blockchain."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.9
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"