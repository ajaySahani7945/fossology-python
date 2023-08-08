# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import secrets

import pytest
import responses

from fossology import Fossology
from fossology.exceptions import AuthorizationError, FossologyApiError
from fossology.obj import SearchTypes, Upload


# See: https://github.com/fossology/fossology/pull/2390
@pytest.mark.skip(
    reason="current Fossology version has a bug, /search is not supported, fixed in 4.3.0"
)
def test_search_nogroup(foss: Fossology):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.search(searchType=SearchTypes.ALLFILES, filename="GPL%", group="test")
    assert "Searching for group test not authorized" in str(excinfo.value)


@pytest.mark.skip(
    reason="current Fossology version has a bug, /search is not supported, fixed in 4.3.0"
)
def test_search(foss: Fossology, upload: Upload):
    search_result = foss.search(searchType=SearchTypes.ALLFILES, filename="GPL%")
    assert search_result


@pytest.mark.skip(
    reason="current Fossology version has a bug, /search is not supported, fixed in 4.3.0"
)
def test_search_nothing_found(foss: Fossology, upload: Upload):
    search_result = foss.search(
        searchType=SearchTypes.ALLFILES,
        filename="test%",
        tag="test",
        filesizemin="0",
        filesizemax="1024",
        license="Artistic",
        copyright="Debian",
    )
    assert search_result == []


@pytest.mark.skip(
    reason="current Fossology version has a bug, /search is not supported, fixed in 4.3.0"
)
def test_search_directory(foss: Fossology, upload: Upload):
    search_result = foss.search(
        searchType=SearchTypes.DIRECTORIES,
        filename="share",
    )
    assert search_result


@pytest.mark.skip(
    reason="current Fossology version has a bug, /search is not supported, fixed in 4.3.0"
)
def test_search_upload(foss: Fossology, upload: Upload):
    search_result = foss.search(
        searchType=SearchTypes.ALLFILES,
        upload=upload,
        filename="share",
    )
    assert search_result


@pytest.mark.skip(
    reason="current Fossology version has a bug, /search is not supported, fixed in 4.3.0"
)
def test_search_upload_does_not_exist(foss: Fossology):
    hash = {"sha1": "", "md5": "", "sha256": "", "size": ""}
    fake_upload = Upload(
        secrets.randbelow(1000),
        "fake_folder",
        secrets.randbelow(1000),
        "",
        "fake_upload",
        "2020-12-30",
        hash=hash,
    )
    search_result = foss.search(
        searchType=SearchTypes.ALLFILES,
        upload=fake_upload,
        filename="share",
    )
    assert not search_result


@pytest.mark.skip(
    reason="current Fossology version has a bug, /search is not supported, fixed in 4.3.0"
)
@responses.activate
def test_search_error(foss_server: str, foss: Fossology):
    responses.add(responses.GET, f"{foss_server}/api/v1/search", status=404)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.search()
    assert "Unable to get a result with the given search criteria" in str(excinfo.value)


def test_filesearch(foss: Fossology, upload: Upload):
    filelist = [
        {"md5": "F921793D03CC6D63EC4B15E9BE8FD3F8"},
        {"sha1": upload.hash.sha1},
    ]
    search_result = foss.filesearch(filelist=filelist)
    assert len(search_result) == 2
    assert (
        f"File with SHA1 {upload.hash.sha1} doesn't have any concluded license yet"
        in str(search_result[1])
    )

    filelist = [{"sha1": "FAKE"}]
    result = foss.filesearch(filelist=filelist)
    assert result == "Unable to get a result with the given filesearch criteria"
    assert foss.filesearch() == []


def test_filesearch_nogroup(foss: Fossology):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.filesearch(filelist=[], group="test")
    assert "Not authorized to get a result with the given filesearch criteria" in str(
        excinfo.value
    )


@responses.activate
def test_filesearch_error(foss_server: str, foss: Fossology):
    responses.add(responses.POST, f"{foss_server}/api/v1/filesearch", status=404)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.filesearch()
    assert "Unable to get a result with the given filesearch criteria" in str(
        excinfo.value
    )
