from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=api_key)


async def fetch_project_team(project_name: str, website: str) -> str:
    prompt = f"""
Kamu adalah pakar analisis investigatif dalam dunia cryptocurrency dan blockchain.

Tugas kamu adalah melakukan audit dan analisis mendalam terhadap tim inti dari proyek berikut:

Proyek: {project_name}
Website: {website}

1. PROFILING & ANALISIS KREDIBILITAS TIM

Informasi utama:
- Nama lengkap, peran di proyek, pengalaman sebelumnya, kredensial
- Link sosial media resmi (LinkedIn, Twitter, GitHub)
- Aktivitas terbaru (posting, AMA, podcast)
- Apakah tim sudah doxxed / publik?
- Keterlibatan di proyek besar sebelumnya
- Transparansi tim di web/docs/media

2. SENTIMEN DAN KOMUNITAS
- Ulasan komunitas (Discord, Twitter, Reddit)
- Tuduhan, pujian, atau isu scam

3. FORMAT OUTPUT
- Ringkasan kredibilitas tim
- Daftar anggota + peran + link medsos
- Catatan khusus / red flag
- Skor kredibilitas (0–10) + confidence level
- Link referensi yang valid

Jika informasi tidak tersedia, berikan analisis kemungkinan penyebab (anonim, stealth dev, eksternal). Jawaban harus realistis dan actionable.
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