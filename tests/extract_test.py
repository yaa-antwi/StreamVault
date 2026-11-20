
import json
from unittest.mock import Mock

from pipeline.extract import fetch_movie, fetch_credits


def test_movie_extraction():
    response = Mock()
    response.json.return_value = {"id": 155, "title": "The Dark Knight"}

    session = Mock()
    session.get.return_value = response

    movie, status = fetch_movie("155", session)

    assert movie["id"] == 155
    assert status in ["downloaded", "cached"]


def test_credits_extraction():
    response = Mock()
    response.json.return_value = {
        "id": 155,
        "cast": [],
        "crew": []
    }

    session = Mock()
    session.get.return_value = response

    credits, status = fetch_credits("155", session)

    assert credits["id"] == 155
    assert "cast" in credits
    assert "crew" in credits
    assert status in ["downloaded", "cached"]


def test_movie_cache():
    session = Mock()
    movie, status = fetch_movie("155", session)

    assert movie is not None
    assert status == "cached"
    session.get.assert_not_called()


def test_credits_cache():
    session = Mock()
    credits, status = fetch_credits("155", session)

    assert credits is not None
    assert status == "cached"
    session.get.assert_not_called()
