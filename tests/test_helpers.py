#!/bin/python

from src import helpers


def test_count_consecutive():
    result = helpers.count_successive_repetitions("F#o##o###", "#")
    assert result.values == [1, 2, 3]


def test_count_consecutive_none():
    result = helpers.count_successive_repetitions("F#o##o###", "*")
    assert result.values == [0]
