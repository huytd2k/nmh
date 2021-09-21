import os
import click

from nmh.git.github import CreateRepoOption, GithubClient


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
def rpush(token, repo_dir, repo_name, private):
    client = GithubClient(token)
    repo_name = repo_name or os.path.split(os.path.abspath(repo_dir))[-1]
    client.bootstrap_repo(repo_dir, CreateRepoOption(repo_name, private))


cli()
