from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=api_key)


async def fetch_project_competitor(project_name: str, website: str) -> str:
    prompt = f"""
Tugas kamu adalah mengidentifikasi kompetitor utama dari proyek crypto berikut:

**Proyek:** {project_name}  
**Website:** {website}

Berikan jawaban dengan struktur:
- Siapa saja kompetitor langsung?
- Apa persamaan dan perbedaannya?
- Apakah proyek ini punya keunggulan teknologi, komunitas, atau adopsi lebih baik?
- Apakah ada risiko kalah bersaing?

Tambahkan referensi dari CoinGecko, Messari, DefiLlama, atau analisa lain jika tersedia.
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