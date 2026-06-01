"""Composite risk scoring."""

from typosquat.score import DEFAULT_WEIGHTS, score


def test_score_record_shape():
    rec = score("reqests", "requests")
    assert set(rec) == {"risk", "base", "popularity", "similarities", "weights"}
    assert 0.0 <= rec["risk"] <= 1.0
    assert set(rec["similarities"]) == set(DEFAULT_WEIGHTS)


def test_closer_candidate_scores_higher():
    near = score("reqests", "requests")["risk"]  # one deletion
    far = score("flask", "requests")["risk"]
    assert near > far


def test_popularity_multiplies():
    full = score("reqests", "requests", popularity=1.0)["risk"]
    half = score("reqests", "requests", popularity=0.5)["risk"]
    assert abs(full * 0.5 - half) < 1e-9


def test_custom_weights_change_ranking():
    # zero every channel except keyboard; risk becomes the keyboard similarity
    only_kbd = {k: 0.0 for k in DEFAULT_WEIGHTS}
    only_kbd["keyboard"] = 1.0
    rec = score("asdg", "asdf", weights=only_kbd)
    assert abs(rec["base"] - rec["similarities"]["keyboard"]) < 1e-9
