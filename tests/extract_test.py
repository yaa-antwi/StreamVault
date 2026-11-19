from unittest.mock import Mock
import pytest

from pipeline.extract import fetch_movie, fetch_credits

# Testing Movie details extraction
def test_movie_extraction():
    movie, status = fetch_movie("155", session=None)

    assert movie is not None
    assert movie.get("id") == 155
    assert movie.get("title") == "The Dark Knight"
    assert status in ["downloaded", "cached"]

#Tesing movie credits extraction
def test_credits_extraction():
    credits, status = fetch_credits("155", session=None)

    assert credits is not None
    assert credits.get("id") == 155
    assert "cast" in credits
    assert "crew" in credits
    assert status in ["downloaded", "cached"]


#Testing the movie cache
def test_movie_cache():
    fake_session = Mock()

    movie, status = fetch_movie("155", session=fake_session)

    assert movie is not None
    assert status == "cached"
    fake_session.get.assert_not_called()


#Tesing the credit cache
def test_credits_cache():
    fake_session = Mock()
    credits, status = fetch_credits("155", session=fake_session)
    assert credits is not None
    assert status == "cached"
    fake_session.get.assert_not_called()