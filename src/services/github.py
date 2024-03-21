import requests

from typing import List

class GitHub:
    def __init__(self, token: str) -> None:
        self.token = token

    def get_repositories(self) -> List[str]:
        headers = {"Authorization": f"token {self.token}"}
        response = requests.get(
            "https://api.github.com/user/repos", headers=headers
        )
        response.raise_for_status()
        return [repo["full_name"] for repo in response.json()]