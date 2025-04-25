from .fetchers.about_project import fetch_about_project
from .fetchers.project_goals import fetch_project_goals
from .fetchers.innovation import fetch_project_innovation
from .fetchers.competitor import fetch_project_competitor
from .fetchers.project_team import fetch_project_team
from .fetchers.social_media import fetch_social_media
from .fetchers.roadmap import fetch_project_roadmap
from .fetchers.vc_investor import fetch_project_vc
from .fetchers.tokenomics import fetch_project_tokenomics
from .fetchers.partner_project import fetch_partner_project
from .fetchers.airdrop_confirm import fetch_airdrop_confirm

fetcher_map = {
    "fetch_about": fetch_about_project,
    "fetch_goals": fetch_project_goals,
    "fetch_innovation": fetch_project_innovation,
    "fetch_competitor": fetch_project_competitor,
    "fetch_team": fetch_project_team,
    "fetch_social": fetch_social_media,
    "fetch_roadmap": fetch_project_roadmap,
    "fetch_vc": fetch_project_vc,
    "fetch_tokenomics": fetch_project_tokenomics,
    "fetch_partner": fetch_partner_project,
    "fetch_airdrop": fetch_airdrop_confirm,
} 

class FetcherHandler:
    def __init__(self, project_name: str, website: str, fetch_type: str):
        self.project_name = project_name
        self.website = website
        self.fetch_type = fetch_type

    async def handle(self):
        fetcher = fetcher_map.get(self.fetch_type)
        if not fetcher:
            return f"❌ Fetcher '{self.fetch_type}' tidak ditemukan."
        try:
            result = await fetcher(self.project_name, self.website)
            return result
        except Exception as e:
            return f"❌ Gagal menjalankan '{self.fetch_type}': {str(e)}"