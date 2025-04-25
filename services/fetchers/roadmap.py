from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=api_key)


async def fetch_project_roadmap(project_name: str, website: str) -> str:
    prompt = f"""
Tugas kamu adalah menyusun ringkasan roadmap proyek {project_name} berdasarkan website resmi {website}, dokumentasi publik, atau pengumuman resmi.

**Poin yang harus dijelaskan:**
- Target jangka pendek, menengah, panjang
- Capaian milestone sebelumnya
- Apakah roadmap realistis dan transparan?
- Jika tersedia, tambahkan tautan roadmap atau screenshot

Sajikan dalam format rapi dan bisa langsung digunakan untuk penilaian kemajuan proyek.
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