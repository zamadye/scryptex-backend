from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=api_key)



async def fetch_project_vc(project_name: str, website: str) -> str:
    prompt = f"""
Kamu adalah pakar analisis investigatif dalam dunia cryptocurrency dan blockchain.

Tugas kamu adalah melakukan audit dan analisis mendalam tentang aktivitas pendanaan (VC / capital) untuk proyek {project_name} ({website}).

Fokus analisa:
- Total funding & valuation
- VC utama dan jenis funding round
- Track record VC di proyek lain
- Reputasi di komunitas crypto
- Potensi conflict of interest
- Komposisi token allocation

Berikan ringkasan dengan:
- Poin-poin insight
- Tabel VC + jumlah dana (jika tersedia)
- Link referensi aktif (min. 3 sumber)
- Skor resiko investor (1–10)

Gunakan format Markdown. Jika tidak ditemukan informasi, berikan analisa berdasarkan pola umum atau red flag tipikal.
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