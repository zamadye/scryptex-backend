from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=api_key)


async def fetch_airdrop_confirm(project_name: str, website: str) -> str:
    """
    Fungsi untuk menyelidiki kemungkinan adanya program airdrop dari proyek tertentu.
    """
    prompt = f"""
Kamu adalah analis crypto yang bertugas menyelidiki kemungkinan adanya program airdrop dari proyek {project_name} ({website}).

Langkah investigasi:
1. Periksa sinyal berikut:
   - Apakah sedang ada testnet aktif?
   - Campaign di Galxe / Zealy / Crew3?
   - Ada kata kunci "airdrop", "reward", "points" di whitepaper atau docs?
   - Apakah mereka punya program ambassador atau komunitas aktif?
   - Apakah ada pengumuman di Twitter atau Discord tentang snapshot atau reward?

2. Evaluasi tingkat keyakinan proyek ini akan melakukan airdrop.

Output yang harus diberikan:
- Ringkasan status airdrop
- Daftar sinyal yang ditemukan (positif / negatif)
- Tingkat kemungkinan (0–100%)
- Link / sumber jika tersedia (Galxe, Discord, X, dsb)

Jawaban harus informatif, tidak mengada-ada, dan bisa dijadikan dasar keputusan.
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