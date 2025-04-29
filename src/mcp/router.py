from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional, Tuple
import re
import json
import uuid
from datetime import datetime

from src.database import get_db
from src.itinerary import service as itinerary_service
from src.itinerary.schemas import ItineraryFilter
from src.mcp.schemas import MCPGenerateRequest, MCPCompletionResponse
from src.mcp.exceptions import ModelNotSupportedException, NoUserMessageException

router = APIRouter(
    prefix="/mcp",
    tags=["mcp"],
)

# MCP Endpoint for model information
@router.get("/models")
async def get_models():
    """Return available models in MCP format"""
    return {
        "data": [
            {
                "id": "itinerary-recommender",
                "object": "model",
                "created": 1682777962,
                "owned_by": "itinerary-app",
                "capabilities": {
                    "completion": True,
                    "chat_completion": True,
                    "embeddings": False,
                }
            }
        ],
        "object": "list"
    }

# Helper function to get recommended itineraries by nights with fallback to similar durations
def get_recommended_itineraries_with_fallback(db: Session, nights: int) -> Tuple[List[Dict[str, Any]], Optional[int]]:
    """
    Get recommended itineraries filtered by number of nights
    If none are found, find the nearest available duration
    
    Returns:
        Tuple containing:
        - List of itinerary dictionaries
        - The actual duration used (None if original duration was used)
    """
    # First try exact match
    filters = ItineraryFilter(
        is_recommended=True,
        min_nights=nights,
        max_nights=nights
    )
    
    itineraries = itinerary_service.get_itineraries(db, filters=filters)
    
    # If no itineraries found, search for nearest available duration
    if not itineraries:
        # Get all available recommended itineraries
        all_recommended = itinerary_service.get_itineraries(
            db, 
            filters=ItineraryFilter(is_recommended=True)
        )
        
        if not all_recommended:
            return [], None
        
        # Find the closest duration
        durations = [item['duration_nights'] for item in all_recommended]
        closest_duration = min(durations, key=lambda x: abs(x - nights))
        
        # Get itineraries with that duration
        filters = ItineraryFilter(
            is_recommended=True,
            min_nights=closest_duration,
            max_nights=closest_duration
        )
        
        itineraries = itinerary_service.get_itineraries(db, filters=filters)
        return itineraries, closest_duration
    
    return itineraries, None

# Parse user query to understand intent and parameters
def parse_user_query(text: str) -> Dict[str, Any]:
    """
    Parse the user query to extract relevant parameters
    
    Returns a dict with:
    - nights: int or None
    - destination: str or None
    - budget: str or None
    - other extracted parameters
    """
    result = {
        "nights": None,
        "destination": None,
        "budget": None,
    }
    
    # Extract number of nights
    night_patterns = [
        r'(\d+)[- ]night',
        r'(\d+) days',
        r'for (\d+) nights',
        r'(\d+)[- ]day trip',
    ]
    
    for pattern in night_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                result["nights"] = int(match.group(1))
                # If it's days, convert to nights (days-1)
                if 'day' in pattern and not 'night' in pattern:
                    # Only subtract if it's a "day trip" pattern
                    if result["nights"] > 1:  # Don't go negative
                        result["nights"] -= 1
                break
            except (ValueError, IndexError):
                pass
    
    # Extract destination (basic implementation - could be enhanced)
    # Look for destinations after "to", "in", "for"
    destination_patterns = [
        r'to ([A-Za-z\s]+?)(?:\.|\,|\for|\with|\?|$)',
        r'in ([A-Za-z\s]+?)(?:\.|\,|\for|\with|\?|$)',
        r'visit(?:ing)? ([A-Za-z\s]+?)(?:\.|\,|\for|\with|\?|$)',
    ]
    
    for pattern in destination_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["destination"] = match.group(1).strip()
            break
    
    # Extract budget preference
    budget_keywords = {
        "low": ["cheap", "budget", "inexpensive", "affordable", "low cost", "economical"],
        "medium": ["moderate", "mid-range", "reasonable", "standard"],
        "high": ["luxury", "expensive", "high-end", "premium", "deluxe"]
    }
    
    for budget_level, keywords in budget_keywords.items():
        if any(keyword in text.lower() for keyword in keywords):
            result["budget"] = budget_level
            break
    
    return result

# Helper function to format itineraries into rich MCP response
def format_itineraries_response(
    itineraries: List[Dict[str, Any]], 
    requested_nights: int, 
    actual_nights: Optional[int] = None
) -> Dict[str, Any]:
    """Format itineraries into a structured MCP response with both text and data"""
    
    # Prepare the text response
    if not itineraries:
        text_response = f"I'm sorry, but I couldn't find any recommended itineraries for {requested_nights} nights."
        text_response += " We don't have any recommended itineraries available at the moment."
        
        # Return simple text response when no itineraries found
        return {
            "text_response": text_response,
            "structured_data": None
        }
    
    # Start text response
    if actual_nights is not None:
        text_response = (
            f"I couldn't find itineraries for exactly {requested_nights} nights, "
            f"but I found some options for {actual_nights} nights that you might like:"
        )
    else:
        text_response = f"Here are recommended itineraries for {requested_nights} nights:"
    
    # Add itinerary details to text
    for idx, itinerary in enumerate(itineraries, 1):
        text_response += f"\n\n{idx}. {itinerary.get('title', 'Untitled Itinerary')}"
        text_response += f"\n   Duration: {itinerary.get('duration_nights', 'N/A')} nights"
        if itinerary.get('description'):
            text_response += f"\n   Description: {itinerary.get('description')}"
        if itinerary.get('total_estimated_cost'):
            text_response += f"\n   Estimated Cost: ${itinerary.get('total_estimated_cost'):.2f}"
    
    # Add view instructions
    text_response += "\n\nYou can view full details of any itinerary by its ID."
    
    # Create structured data
    itinerary_data = []
    for itinerary in itineraries:
        itinerary_data.append({
            "id": itinerary.get("id"),
            "uuid": itinerary.get("uuid"),
            "title": itinerary.get("title"),
            "duration_nights": itinerary.get("duration_nights"),
            "description": itinerary.get("description"),
            "total_estimated_cost": itinerary.get("total_estimated_cost"),
            "is_recommended": itinerary.get("is_recommended", True),
            "preferences": itinerary.get("preferences", {})
        })
    
    return {
        "text_response": text_response,
        "structured_data": {
            "itineraries": itinerary_data,
            "requested_nights": requested_nights,
            "actual_nights": actual_nights,
            "count": len(itineraries)
        }
    }

# MCP Generate endpoint
@router.post("/generate")
async def generate(
    request: MCPGenerateRequest = Body(...),
    db: Session = Depends(get_db)
):
    """MCP generate endpoint to return recommended itineraries based on user input"""
    # Only accept the itinerary-recommender model
    if request.model != "itinerary-recommender":
        raise ModelNotSupportedException(request.model)
    
    # Extract user query from messages
    user_messages = [msg for msg in request.messages if msg.get("role") == "user"]
    if not user_messages:
        raise NoUserMessageException()
    
    last_user_message = user_messages[-1]
    if isinstance(last_user_message.get("content"), list):
        text_content = next((item.get("text") for item in last_user_message.get("content", []) 
                             if item.get("type") == "text"), "")
    else:
        text_content = last_user_message.get("content", "")
    
    # Parse the user query to understand intent and extract parameters
    parsed_query = parse_user_query(text_content)
    
    # Use nights from query or default to 3
    nights = parsed_query.get("nights") or 3
    
    # Get recommended itineraries with fallback
    itineraries, actual_nights = get_recommended_itineraries_with_fallback(db, nights)
    
    # Format the response
    formatted_response = format_itineraries_response(itineraries, nights, actual_nights)
    
    # Generate a unique ID for this response
    response_id = f"mcp-{request.model}-{str(uuid.uuid4())[:8]}"
    
    # Build MCP response format with both text and structured data
    response = {
        "id": response_id,
        "model": request.model,
        "created": int(datetime.now().timestamp()),
        "object": "completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": formatted_response["text_response"]
                        }
                    ]
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": len(text_content),
            "completion_tokens": len(formatted_response["text_response"]),
            "total_tokens": len(text_content) + len(formatted_response["text_response"])
        }
    }
    
    # Add structured data if available
    if formatted_response["structured_data"]:
        response["choices"][0]["message"]["content"].append({
            "type": "itinerary_data",
            "data": formatted_response["structured_data"]
        })
    
    return response