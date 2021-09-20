import click


@click.group()
def cli():
    pass


@cli.command()
@click.option("-t", "--token", required=True, help="Github token")
@click.option("-u", "--user", required=True, help="Github username")
@click.option("-f", "--folder", required=True, help="Path to project folder")
@click.option(
    "--repo-name",
    help="Repository name to push to github. Default to project folder name",
)
def rpush(token, user, repo_name):
    print(token, user, repo_name)


cli()
