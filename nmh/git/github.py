"""This module contains functions to comminucate with github api,
Why use third party if I can write???"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import json
import logging
import os
from os.path import join as join_path
from typing import Optional
from abc import ABC, abstractmethod

import requests
import git


INITIAL_COMMIT_MESSAGE = "Initiated with nmh 😎"
DEFAULT_GITHUB_API = "https://api.github.com"

logger = logging.getLogger(__name__)


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


class FakeClient(GitRemoteClient):
    def create_repo(self, options: CreateRepoOption) -> str:
        return "fake_url"


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


class GitManager:
    def __init__(self, client: GitRemoteClient) -> None:
        self._client = client

    def bootstrap_repo(
        self,
        repo_path: str,
        create_option: CreateRepoOption = None,
        init_msg: str = INITIAL_COMMIT_MESSAGE,
        override_git: bool = True,
        dry_run: bool = False,
    ):
        logger.debug("handling repo %s", repo_path)
        if not os.path.isdir(repo_path):
            raise OSError(f"{repo_path} is not a valid directory")

        _handle_exist_git_data(repo_path, override_git)
        remote_ssh_url = self._client.create_repo(create_option)
        repo = git.Repo.init(repo_path)
        _init_repo_and_push(repo, init_msg, remote_ssh_url, dry_run)


def time_indentifer() -> int:
    """Generate unique indentifier by UNIX timestamp

    Returns:
        int: current timestamp * 10e6
    """
    return int(datetime.now().timestamp() * 1_000_000)


def _init_repo_and_push(repo: git.Repo, init_msg: str, ssh_url: str, dry_run: bool):
    """Stage all file, commit, add remote repo, and push to remote

    Args:
        repo (git.Repo): Repo instance
        init_msg (str): Initial commit message
        ssh_url (str): Repo remote
    """
    repo.git.add(".")
    repo.git.commit("-m", f'"{init_msg}"')
    repo.git.remote("add", "origin", f"{ssh_url}")
    repo.git.branch("-M", "main")
    if not dry_run:
        repo.git.push("-u", "origin", "main")


def _handle_exist_git_data(repo_path: str, override: bool):
    dot_git_path = f"{repo_path}/.git"
    if os.path.exists(dot_git_path):
        if not override:
            raise Exception(
                "`.git` folder existed in your local repo, maybe override it"
            )
        _override_git(repo_path)


def _override_git(repo_path: str):
    old_git_path = f"{repo_path}/.git"
    recover = f".recover-git-{time_indentifer()}"
    recover_path = join_path(repo_path, recover)
    os.system(f"mv {old_git_path} {recover_path}")
    gitignore_path = join_path(repo_path, ".gitignore")
    os.system(f'echo "{recover}" >> f{gitignore_path}')
