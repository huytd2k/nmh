from unittest import TestCase
from unittest.mock import Mock, patch

import pytest
from nmh.git.github import (
    CreateRepoOption,
    GithubClient,
    GithubClientException,
)


class TestGithubClient(TestCase):
    @patch("requests.post")
    def test_create_repo(self, mock_post: Mock):
        # Happy case
        client = GithubClient(token="token")
        mock_post.return_value.status_code = 201
        mock_post.return_value.json = lambda: {"ssh_url": "link"}

        ret = client.create_repo(
            CreateRepoOption("created_with_api", private=True, description="des")
        )
        assert ret == "link"
        mock_post.assert_called_once_with(
            f"{client._host}/user/repos",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "token token",
            },
            data="".join(
                [
                    '{"name": "created_with_api", "private": true, ',
                    '"auto_init": false, "description": "des"}',
                ]
            ),
        )

        # Sad cases (lol)
        mock_post.reset_mock()
        mock_post.return_value.status_code = 422
        with pytest.raises(GithubClientException):
            client.create_repo(
                CreateRepoOption("created_with_api", private=True, description="des")
            )
