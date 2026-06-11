import pytest
from unittest.mock import AsyncMock, patch
from app.ai.revenue_predictor import predict_revenue, RevenuePredictionOutput

@pytest.mark.asyncio
@patch("app.ai.revenue_predictor.get_gemini_client")
async def test_predict_revenue(mock_get_client):
    # Mock return JSON for Gemini
    mock_response = {
        "revenue_score": 85,
        "estimated_revenue": 15000.0,
        "conversion_probability": 0.9,
        "competitor_risk": "low",
        "urgency": "high",
        "recommendation": "Call back within 15 minutes to confirm booking.",
        "scoring_factors": {
            "urgency_score": 0.95,
            "service_type_score": 0.8,
            "estimated_value_score": 0.75,
            "business_category_score": 0.8,
            "sentiment_score": 0.9,
            "buying_intent_score": 0.95
        }
    }

    # Set up mock client instance
    mock_client = AsyncMock()
    mock_client.generate_structured.return_value = mock_response
    mock_client.fast_model = "gemini-2.5-flash"
    mock_client.pro_model = "gemini-2.5-pro"
    mock_get_client.return_value = mock_client

    # Call target function
    result = await predict_revenue(
        conversation_text="I need AC repair immediately. The budget is around ₹15,000.",
        business_category="home_services",
        service_type="AC Repair",
        currency="INR"
    )

    # Asserts
    assert isinstance(result, RevenuePredictionOutput)
    assert result.revenue_score == 85
    assert result.estimated_revenue == 15000.0
    assert result.conversion_probability == 0.9
    assert result.competitor_risk == "low"
    assert result.urgency == "high"
    assert result.recommendation == "Call back within 15 minutes to confirm booking."
    assert result.scoring_factors.urgency_score == 0.95
    assert result.scoring_factors.buying_intent_score == 0.95

    # Verify Gemini Client usage
    mock_client.generate_structured.assert_called_once()
    _, kwargs = mock_client.generate_structured.call_args
    assert kwargs["schema"] == RevenuePredictionOutput
    assert kwargs["model"] == mock_client.pro_model
    assert "15,000" in kwargs["prompt"]
