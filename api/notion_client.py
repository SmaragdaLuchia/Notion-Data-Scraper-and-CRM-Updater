import requests


class NotionClient:
    """Class for communicating with the Notion API."""

    def __init__(self, token: str, database_id: str):
        self.token = token
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def get_page(self, page_id: str):
        """Tagastab konkreetse lehe andmed (koos properties metaandmetega)."""
        url = f"https://api.notion.com/v1/pages/{page_id}"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def create_page(self, payload: dict):
        """Adds a new page (entry) to the database."""
        url = "https://api.notion.com/v1/pages"
        r = requests.post(url, headers=self.headers, json=payload)
        r.raise_for_status()
        return r.json()

    def update_page(self, page_id: str, properties: dict):
        """Updates an existing page (entry)."""
        url = f"https://api.notion.com/v1/pages/{page_id}"
        r = requests.patch(url, headers=self.headers, json={"properties": properties})
        r.raise_for_status()
        return r.json()

    def query_by_regcode(self, regcode: str):
        """Searches for a page by registry code."""
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"

        payload = {
            "filter": {
                "property": "Registrikood",
                "number": {"equals": int(regcode)}
            }
        }

        r = requests.post(url, headers=self.headers, json=payload)
        r.raise_for_status()
        res = r.json()
        if res.get("results"):
            return res["results"][0]
        return None
