import base64
import json
import os
from anthropic import Anthropic


def classify_with_claude(image_path, temperature=None, humidity=None, moisture=None):
    """
    Use Claude Vision API to classify tobacco leaf disease.
    Returns dict with disease, confidence, and reasoning.
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    client = Anthropic(api_key=api_key)
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Build prompt with environmental conditions
    conditions_text = ""
    if temperature is not None:
        conditions_text += f"Temperature: {temperature}°C\n"
    if humidity is not None:
        conditions_text += f"Humidity: {humidity}%\n"
    if moisture is not None:
        conditions_text += f"Soil Moisture: {moisture}%\n"
    
    if not conditions_text:
        conditions_text = "No environmental data provided."
    
    prompt = f"""You are a plant pathology expert specializing in tobacco diseases. 

Analyze this tobacco leaf image and identify the disease. Consider both visual symptoms and environmental conditions.

Environmental Conditions:
{conditions_text}

Identify the disease from these options:
1. Angular Leaf Spot - Caused by Pseudomonas syringae. Symptoms: Angular lesions bounded by leaf veins, dark water-soaked spots turning brown, spots remain angular due to vein restrictions. Favors cool (20-25°C), wet conditions with high humidity (>70%).

2. Wildfire - Caused by Pseudomonas syringae pv. tabaci. Symptoms: Circular to irregular brown spots with prominent yellow halos, halos caused by tabtoxin production, spots may merge. Favors warm (28-32°C), humid conditions (50-70% humidity).

3. Healthy - No visible disease symptoms.

IMPORTANT: Respond with ONLY a valid JSON object in this exact format:
{{
    "disease": "angular_leaf_spot" or "wildfire" or "healthy",
    "confidence": 0.0 to 1.0,
    "reasoning": "Brief explanation of what you see in the image and why you chose this disease",
    "distinguishing_features": "What specific visual features distinguish this from the other diseases"
}}

Do not include any other text, markdown formatting, or explanations outside the JSON."""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Fast and cost-effective
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        
        # Parse JSON response
        content = response.content[0].text.strip()
        
        # Handle case where Claude might wrap in markdown
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        result = json.loads(content)
        
        # Validate required fields
        if 'disease' not in result or 'confidence' not in result:
            raise ValueError("Missing required fields in Claude response")
        
        # Normalize disease name
        disease_map = {
            'angular_leaf_spot': 'angular_leaf_spot',
            'angular leaf spot': 'angular_leaf_spot',
            'wildfire': 'wildfire',
            'healthy': 'healthy',
            'none': 'healthy',
            'no disease': 'healthy'
        }
        
        disease_key = result['disease'].lower().replace(' ', '_')
        result['disease'] = disease_map.get(disease_key, 'unknown')
        
        # Convert confidence to percentage
        confidence = result['confidence']
        if isinstance(confidence, (int, float)):
            if confidence <= 1.0:
                result['confidence'] = confidence * 100
            else:
                result['confidence'] = min(confidence, 100)
        
        return result
        
    except json.JSONDecodeError as e:
        return {
            'disease': 'unknown',
            'confidence': 0,
            'reasoning': f'Failed to parse Claude response: {str(e)}',
            'distinguishing_features': 'N/A',
            'raw_response': content if 'content' in locals() else 'No response'
        }
    except Exception as e:
        return {
            'disease': 'unknown',
            'confidence': 0,
            'reasoning': f'Error during classification: {str(e)}',
            'distinguishing_features': 'N/A'
        }
