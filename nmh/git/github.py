"""This module contains functions to comminucate with github api,
Why use third party if I can write???"""
from dataclasses import dataclass
import json
import os
from typing import Optional
import requests

from nmh.pathutils import cd


class GithubClientException(Exception):
    pass


@dataclass
class CreateRepoOption:
    name: str
    private: bool = False
    auto_init: bool = False
    description: Optional[str] = None


DEFAULT_GITHUB_API = "https://api.github.com"


class GithubClient:
    def __init__(self, token: str, host: str = DEFAULT_GITHUB_API) -> None:
        self._token = token
        self._host = host

    def create_repo(self, options: CreateRepoOption) -> dict:
        data = options.__dict__
        res = requests.post(
            f"{self._host}/user/repos",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {self._token}",
            },
            data=json.dumps(data),
        )
        if res.status_code != 201:
            raise GithubClientException("Cannot create repository", res.json())

        return res.json()

    def bootstrap_repo(self, repo_path: str, create_option: CreateRepoOption = None):
        name = os.path.split(os.path.abspath(repo_path))[-1]
        create_option = create_option or CreateRepoOption(name)
        create_result = self.create_repo(create_option)
        ssh_url = create_result.get("ssh_url")

        with cd(repo_path):
            os.system("rm -rf .git")
            os.system("git init")
            os.system("git add .")
            os.system('git commit -m "Init"')
            os.system(f"git remote add origin {ssh_url}")
            os.system(f"git branch -M main")
            os.system("git push -u origin main")
