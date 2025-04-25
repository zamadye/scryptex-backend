from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=api_key)


async def fetch_project_innovation(project_name: str, website: str) -> str:
    prompt = f"""
Kamu adalah pakar analis crypto dan blockchain.

Tugas kamu adalah menjelaskan "inovasi teknologi utama" dari proyek {project_name}.

Fokuskan jawaban pada:
- Teknologi baru yang dibawa (zk, modular, AI-native, dsb)
- Perbedaan dibanding proyek kompetitor
- Arsitektur atau desain token unik
- Insight dari whitepaper, docs, atau Medium
- Relevansi inovasi dengan kebutuhan ekosistem

Tulis ringkas, berbobot, dan dalam 1 paragraf.
Website: {website}
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