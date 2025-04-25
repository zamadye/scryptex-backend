from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=api_key)

async def fetch_about_project(project_name: str, website: str) -> str:
    prompt = f"""
Kamu adalah pakar analis crypto dengan kemampuan merangkum informasi proyek secara singkat, padat, dan informatif.

Buat deskripsi proyek {project_name} yang mudah dipahami dalam 1 paragraf.

Fokus konten:
- Apa yang dilakukan proyek ini?
- Masalah apa yang diselesaikan?
- Siapa target user-nya?
- Teknologi utama jika ada
- Ekosistem mana yang terkait (Ethereum, Cosmos, dsb)

Sumber: website resmi ({website}), docs, atau artikel jika tersedia.

Pastikan jawaban padat, tidak mengulang, dan cocok sebagai pembuka analisa proyek. Gunakan format Markdown.
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