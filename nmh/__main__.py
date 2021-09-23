import logging
import os
import click

from nmh.git.github import CreateRepoOption, FakeClient, GitManager, GithubClient


@click.group()
def cli():
    pass


@cli.command()
@click.option("-t", "--token", required=True, help="Github token")
@click.option(
    "-d", "--repo-dir", required=True, help="Directory of local project folder"
)
@click.option(
    "-n",
    "--repo-name",
    help="Repository name to push to github. Default to project folder name",
)
@click.option(
    "-p", "--private", is_flag=True, default=False, help="Upload private repo"
)
@click.option(
    "--dry", is_flag=True, default=False, help="Dry run, no remote is uploaded"
)
@click.option("--log-level", default="WARNING", help="Logging level")
def bootstrap(token, repo_dir, repo_name, private, dry, log_level):
    logging.basicConfig(level=log_level)
    client = GithubClient(token)
    repo_name = repo_name or os.path.split(os.path.abspath(repo_dir))[-1]
    git_manager = GitManager(client) if not dry else GitManager(FakeClient())
    git_manager.bootstrap_repo(
        repo_dir, CreateRepoOption(repo_name, private), dry_run=dry
    )


cli()
