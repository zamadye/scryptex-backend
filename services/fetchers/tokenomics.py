from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=api_key)


async def fetch_project_tokenomics(project_name: str, website: str) -> str:
    prompt = f"""
Tugas kamu adalah menganalisis tokenomics dari proyek {project_name}.
Website: {website}

Jika proyek belum meluncurkan token, berikan estimasi atau referensi dari whitepaper atau artikel.

Informasi penting:
- Nama token, simbol, total supply
- Distribusi: tim, investor, komunitas, treasury
- Jadwal vesting
- Utilitas token (governance, staking, gas, voting)
- Model ekonomi (inflasi, deflasi, fixed supply)
- Rencana TGE (token generation event)

Format hasil:
1. Ringkasan singkat tokenomics
2. Tabel distribusi (jika ada)
3. Catatan khusus / red flag / potensi kekuatan
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