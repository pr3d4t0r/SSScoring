# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

from click.testing import CliRunner

from ssscoring.cli import _assertDataLake
from ssscoring.cli import die
from ssscoring.cli import _ssscoreCommand

import pathlib
import pytest


# +++ constants +++

TEST_DATA_LAKE = './resources/test-tracks'
TEST_DATA_LAKE_BOGUS = './resources/bogus'


# +++ tests +++

@pytest.fixture
def _bogusFile(tmp_path_factory):
    bogusFile = pathlib.Path(tmp_path_factory.mktemp('data')/'bogusdir.dat')
    bogusFile.touch()
    yield bogusFile.as_posix()
    bogusFile.unlink()


@pytest.fixture
def _bogusDir(tmp_path_factory):
    bogusDir = pathlib.Path(tmp_path_factory.mktemp('data')/'bogusdir.dat')
    bogusDir.mkdir(mode = 0o000)
    yield bogusDir.as_posix()
    bogusDir.rmdir()


def test_die():
    assert 42 == die('Bogus error', 42, isUnitTest = True)


def test__assertDataLake(_bogusFile, _bogusDir):
    assert _assertDataLake(TEST_DATA_LAKE, isUnitTest = True)
    assert not _assertDataLake(TEST_DATA_LAKE_BOGUS, isUnitTest = True)
    assert not _assertDataLake(_bogusFile, isUnitTest = True)
    assert not _assertDataLake(_bogusDir, isUnitTest = True)


def test_ssscoreCommand():
    runner = CliRunner()
    result = runner.invoke(_ssscoreCommand, [ 42.0, True, TEST_DATA_LAKE, ])
    result = runner.invoke(_ssscoreCommand, [ True, TEST_DATA_LAKE, ])
    result = runner.invoke(_ssscoreCommand, [ 42.0, TEST_DATA_LAKE, ])
    assert result

