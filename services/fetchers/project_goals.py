from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=api_key)


async def fetch_project_goals(project_name: str, website: str) -> str:
    prompt = f"""
Kamu adalah pakar analis crypto. Jelaskan secara singkat dan padat *tujuan utama* dari proyek {project_name}.

Fokus pada hal berikut:
- Masalah utama apa yang ingin diselesaikan proyek ini?
- Target pengguna (developer, enterprise, retail, dsb)
- Visi & misi proyek
- Cita-cita jangka panjang proyek
- Referensi jika tersedia (docs, Medium, Cointelegraph, dll)

Informasi harus akurat, ringkas, dan dapat digunakan untuk memahami *arah proyek* ini.
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