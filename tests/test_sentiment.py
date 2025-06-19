from app.agents.sentiment import analyze_sentiment


def test_analyze_sentiment_positive():
    text = "I absolutely love this product! It works great and makes life easier."
    label, score = analyze_sentiment(text)
    assert label == "POSITIVE"
    assert score > 0.9


def test_analyze_sentiment_negative():
    text = "This was the worst experience ever. I hate how buggy and slow it is."
    label, score = analyze_sentiment(text)
    assert label == "NEGATIVE"
    assert score > 0.9


def test_analyze_sentiment_neutral_or_fallback():
    text = ""
    # Define your expected fallback behavior for empty input
    label, score = analyze_sentiment(text)
    assert isinstance(label, str)
    assert isinstance(score, float)
