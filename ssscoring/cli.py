# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Command line tools package.
"""


from ssscoring import __VERSION__

import click


# +++ implementation +++

@click.command('ssscore')
@click.version_option(__VERSION__, prog_name = 'ssscore')
@click.argument('datalake', nargs = 1, type = click.STRING)
def ssscore(datalake: str) -> None:
    """
    Process all the speed skydiving files contained in `dataLakeSpec`.
    """
    click.secho('Hello, world', fg = 'bright_green')


# +++ main +++

# For interactive testing and symbolic debugging:
if '__main__' == __name__:
    ssscore()


