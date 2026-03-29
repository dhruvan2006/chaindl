import pytest
from chaindl.scraper.utils import _join_url


@pytest.mark.parametrize(
    "base_url, path, expected",
    [
        (
            "https://example.com/",
            "/path/to/resource",
            "https://example.com/path/to/resource",
        ),
        (
            "https://www.example.com",
            "path/to/resource",
            "https://www.example.com/path/to/resource",
        ),
        (
            "https://www.example.com",
            "/path/to/resource",
            "https://www.example.com/path/to/resource",
        ),
    ],
)
def test_join_url(base_url, path, expected):
    assert _join_url(base_url, path) == expected
