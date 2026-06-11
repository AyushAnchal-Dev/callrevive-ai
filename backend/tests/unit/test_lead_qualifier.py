import pytest
from unittest.mock import AsyncMock, patch
from app.ai.lead_qualifier import qualify_lead, LeadQualification

@pytest.mark.asyncio
@patch("app.ai.lead_qualifier.get_gemini_client")
async def test_qualify_lead(mock_get_client):
    # Mock return JSON for Gemini
    mock_response = {
        "category": "hot",
        "lead_score": 90,
        "urgency": "high",
        "purchase_readiness": "ready",
        "customer_intent": "service",
        "service_requested": "AC repair",
        "budget_range": "₹5,000 - ₹10,000",
        "qualification_notes": "Urgent AC repair requested by Rajesh."
    }

    # Set up mock client instance
    mock_client = AsyncMock()
    mock_client.generate_structured.return_value = mock_response
    mock_client.fast_model = "gemini-2.5-flash"
    mock_client.pro_model = "gemini-2.5-pro"
    mock_get_client.return_value = mock_client

    # Call target function
    result = await qualify_lead(
        conversation_text="I need my AC repaired immediately. It stopped cooling.",
        business_category="home_services"
    )

    # Asserts
    assert isinstance(result, LeadQualification)
    assert result.category == "hot"
    assert result.lead_score == 90
    assert result.urgency == "high"
    assert result.purchase_readiness == "ready"
    assert result.customer_intent == "service"
    assert result.service_requested == "AC repair"
    assert result.budget_range == "₹5,000 - ₹10,000"
    assert "Rajesh" in result.qualification_notes

    # Verify Gemini Client usage
    mock_client.generate_structured.assert_called_once()
    _, kwargs = mock_client.generate_structured.call_args
    assert kwargs["schema"] == LeadQualification
    assert "AC" in kwargs["prompt"]
