"""This module contains functions to comminucate with github api,
Why use third party if I can write???"""
from __future__ import annotations
from dataclasses import dataclass
import json
import os
from typing import Optional
from abc import ABC, abstractmethod
import requests

from nmh.osutils import cd


INITIAL_COMMIT_MESSAGE = "Initiated with nmh 😎"


class GitRemoteClient(ABC):  # pylint: disable=R0903
    @abstractmethod
    def create_repo(self, options: CreateRepoOption) -> str:
        """Create repo in remote repository

        Args:
            options (CreateRepoOption): create options

        Returns:
            str: ssh-url of remote repo
        """


class GithubClientException(Exception):
    pass


@dataclass
class CreateRepoOption:
    name: str
    private: bool = False
    auto_init: bool = False
    description: Optional[str] = None


DEFAULT_GITHUB_API = "https://api.github.com"


class GithubClient(GitRemoteClient):
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

        return res.json().get("ssh_url")

    def bootstrap_repo(
        self,
        repo_path: str,
        create_option: CreateRepoOption = None,
        init_msg: str = INITIAL_COMMIT_MESSAGE,
    ):
        if not os.path.isdir(repo_path):
            raise OSError(f"{repo_path} is not a valid directory")

        ssh_url = self.create_repo(create_option)
        with cd(repo_path):
            os.system("rm -rf .git")
            os.system("git init")
            os.system("git add .")
            os.system(f'git commit -m "{init_msg}"')
            os.system(f"git remote add origin {ssh_url}")
            os.system("git branch -M main")
            os.system("git push -u origin main")
