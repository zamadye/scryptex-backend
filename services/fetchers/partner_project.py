from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=api_key)


async def fetch_partner_project(project_name: str, website: str) -> str:
    prompt = f"""
Tugas kamu adalah menyusun daftar mitra dan partner strategis dari proyek {project_name}.

Informasi yang dicari:
- Nama-nama partner (proyek, protokol, exchange, VC, entitas lain)
- Peran mereka (teknologi, kolaborasi produk, investasi, ekosistem)
- Tanggal pengumuman kerja sama (jika tersedia)
- Sosial media resmi / link website dari partner besar
- Referensi dari Medium, Twitter, Cointelegraph, atau situs resmi

Buat jawaban dengan format Markdown dan rapi untuk evaluasi sinergi proyek.
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