# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Command line tools package.
"""


from ssscoring import __VERSION__
from ssscoring.calc import aggregateResults
from ssscoring.calc import processAllJumpFiles
from ssscoring.calc import roundedAggregateResults
from ssscoring.constants import FT_IN_M
from ssscoring.flysight import getAllSpeedJumpFilesFrom

import os
import pathlib
import sys

import click


# +++ implementation +++

def die(message: str, exitCode: int, isUnitTest = False) -> int:
    """
    Display an end-user `message` and exit the program with `exitCode`.

    Arguments
    ---------
        message
    A string, most often with a descriptive error message.

        exitCode
    An exit code, where `0` is normal exit, and any other value is an error
    condition.

        isUnitTest
    A Boolean; if `True`, the program returns the value of `exitCode` to the
    caller, otherwise it terminates with `sys.exit(exitCode)`.
    """
    if isUnitTest:
        return exitCode
    else:
        click.secho('%s - exit code %d' % (message, exitCode))
        sys.exit(exitCode)


def _assertDataLake(dataLake: str, isUnitTest = False) -> bool:
    """
    Assert that the path exists and that the program has read access permission
    for at least the topmost directory.

    Arguments
    ---------
        dataLake
    A string path corresponding to the data lake, used as the basis to create
    an instance of `pathlib.Path` to test path validity.

    Returns
    -------
    `True` if the path exists and is accessible.


    Raises
    ------
    Various system-level exceptions depending on file system conditions and
    command line argument validity.  `FileNotFound` is a common one.
    """
    retVal = False
    try:
        path = pathlib.Path(dataLake)
        if not path.exists():
            die('%s - data lake not found' % dataLake, 2, isUnitTest)
        elif not path.is_dir():
            die('%s - please specify a directory' % dataLake, 3, isUnitTest)
        elif not os.access(path.as_posix(), os.R_OK):
            die('%s - ssscore lacks permission to read the track files', 4, isUnitTest)
        else:
            retVal = True
    except Exception as e:
        die('Data lake assertion failed - %s' % str(e), 1, isUnitTest)
    return retVal


def ssscore(elevation: float, trainingOutput: bool, dataLake: str) -> int:
    """
    Process all the speed skydiving files contained in `dataLakeSpec`.  This
    function implements the business logic for the `/usr/local/bin/ssscore`
    command.  See `pyproject.toml` for command details.

    Arguments
    ---------
        elevation
    The drop zone elevation MSL in feet.

        trainingOutput
    If `True`, output will use rounded values.

        dataLake
    Command line argument with the path to the data lake.

    Returns
    -------
    The number of jump results from processing all the FlySight files in the
    data lake.
    """
    _assertDataLake(dataLake)

    elevationMeters = elevation/FT_IN_M
    click.secho("elevation = %.2f m (%.2f')" % (elevationMeters, elevation))
    click.secho('Processing speed tracks in %s...\n' % dataLake)
    jumpResults = processAllJumpFiles(getAllSpeedJumpFilesFrom(dataLake), altitudeDZMeters=elevationMeters)
    if jumpResults:
        if trainingOutput:
            resultsSummary = roundedAggregateResults(aggregateResults(jumpResults))
        else:
            resultsSummary = aggregateResults(jumpResults)
        click.secho(resultsSummary, fg = 'bright_green')
        click.secho('\nTotal score = %5.2f, mean speed = %5.2f\n' % (resultsSummary.score.sum(), resultsSummary.score.mean()), fg = 'bright_white')
    else:
        click.secho('There were no speed track files to score in %s', fg = 'bright_red')
    return len(jumpResults)


@click.command('ssscore')
@click.argument('datalake', nargs = 1, type = click.STRING)
@click.version_option(__VERSION__, prog_name = 'ssscore')
@click.option('-e', '--elevation', default=0.0, show_default=True, help='DZ elevation in ft')
@click.option('-t', '--training', is_flag=True, show_default=True, default=False, help='Show training output values')
def _ssscoreCommand(elevation: float, training: bool, datalake: str) -> int:
    return ssscore(elevation, training, datalake)


# +++ main +++

# For interactive testing and symbolic debugging:
if '__main__' == __name__:
    _ssscoreCommand()

