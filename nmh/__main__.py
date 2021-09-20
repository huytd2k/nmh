from nmh.git.github import GithubClient
import click


@click.group()
def cli():
    pass


@cli.command()
@click.option("-t", "--token", required=True, help="Github token")
@click.option("-r", "--repodir", required=True, help="Path to project folder")
@click.option(
    "--repo-name",
    help="Repository name to push to github. Default to project folder name",
)
def rpush(token, repo_name, repodir):
    client = GithubClient(token)
    client.bootstrap_repo(repodir)


cli()
