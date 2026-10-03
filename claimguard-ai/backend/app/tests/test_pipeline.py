from app.nlp.pipeline import classify_claim, detect_language, preprocess_text


def test_detect_language_returns_confidence():
    res = detect_language('यह एक बीमा दावा है')
    assert 'confidence' in res


def test_classify_claim_output_shape():
    res = classify_claim('Need urgent payout after theft of my vehicle')
    assert res['label'] in {'LOW_SUSPICION', 'MEDIUM_SUSPICION', 'HIGH_SUSPICION'}
    assert 'probabilities' in res


def test_preprocess_contains_tokens():
    res = preprocess_text('Claim submitted on 10/10/2026.')
    assert len(res['tokens']) > 0
