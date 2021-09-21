import os
import click

from nmh.git.github import CreateRepoOption, GithubClient


@click.group()
def cli():
    pass


@cli.command()
@click.option("-t", "--token", required=True, help="Github token")
@click.option("-d", "--dir", required=True, help="Directory of local project folder")
@click.option(
    "--repo-name",
    help="Repository name to push to github. Default to project folder name",
)
def rpush(token, repo_dir, repo_name):
    client = GithubClient(token)
    repo_name = repo_name or os.path.split(os.path.abspath(repo_dir))[-1]
    client.bootstrap_repo(repo_dir, CreateRepoOption(repo_name))


cli()
