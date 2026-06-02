import random
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Avg
from .models import LeafImage
from .forms import LeafImageForm
from .claude_classifier import classify_with_claude


def upload_image(request):
    """Upload a leaf image with environmental conditions"""
    if request.method == 'POST':
        form = LeafImageForm(request.POST, request.FILES)
        if form.is_valid():
            leaf = form.save()
            # Auto-classify after upload
            classify_disease(leaf)
            messages.success(request, 'Image uploaded and classified!')
            return redirect('diagosis:classify', pk=leaf.pk)
    else:
        form = LeafImageForm()
    
    return render(request, 'diagosis/upload.html', {'form': form})


def classify_disease(leaf):
    """
    Use Claude Vision API to classify tobacco leaf disease.
    Falls back to rule-based if API key not available.
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    if api_key and leaf.image:
        try:
            result = classify_with_claude(
                leaf.image.path,
                temperature=leaf.temperature,
                humidity=leaf.humidity,
                moisture=leaf.moisture_content
            )
            
            leaf.predicted_disease = result['disease']
            leaf.confidence_score = result['confidence']
            leaf.claude_reasoning = result.get('reasoning', '')
            leaf.claude_features = result.get('distinguishing_features', '')
            leaf.save()
            return result
            
        except Exception as e:
            # Log error and fall back to rule-based
            print(f"Claude classification failed: {e}")
            return classify_rule_based(leaf)
    else:
        return classify_rule_based(leaf)


def classify_rule_based(leaf):
    """Fallback rule-based classifier"""
    temp = leaf.temperature or 25
    humidity = leaf.humidity or 60
    
    score_angular = 0
    score_wildfire = 0
    
    if temp < 25:
        score_angular += 10
    if humidity > 70:
        score_angular += 15
        
    if temp > 28:
        score_wildfire += 15
    if 50 <= humidity <= 70:
        score_wildfire += 10
    
    if score_angular > score_wildfire:
        leaf.predicted_disease = 'angular_leaf_spot'
        leaf.confidence_score = min(50 + score_angular, 85)
    elif score_wildfire > score_angular:
        leaf.predicted_disease = 'wildfire'
        leaf.confidence_score = min(50 + score_wildfire, 85)
    else:
        leaf.predicted_disease = 'unknown'
        leaf.confidence_score = 40
    
    leaf.claude_reasoning = 'Classified using environmental conditions only (rule-based fallback)'
    leaf.claude_features = 'N/A'
    leaf.save()
    
    return {
        'disease': leaf.predicted_disease,
        'confidence': leaf.confidence_score,
        'reasoning': leaf.claude_reasoning,
        'distinguishing_features': leaf.claude_features
    }


def classify_image(request, pk):
    """Show classification results for a specific image"""
    leaf = get_object_or_404(LeafImage, pk=pk)
    
    # Get similar images for comparison
    similar_images = LeafImage.objects.filter(
        actual_disease=leaf.predicted_disease
    ).exclude(pk=pk)[:4]
    
    # Get classification details
    classification_details = {
        'reasoning': getattr(leaf, 'claude_reasoning', 'N/A'),
        'features': getattr(leaf, 'claude_features', 'N/A'),
        'method': 'Claude Vision API' if os.environ.get('ANTHROPIC_API_KEY') else 'Rule-based (fallback)'
    }
    
    context = {
        'leaf': leaf,
        'similar_images': similar_images,
        'disease_info': get_disease_info(leaf.predicted_disease),
        'classification_details': classification_details,
    }
    return render(request, 'diagosis/result.html', context)


def get_disease_info(disease_code):
    """Return information about a disease"""
    info = {
        'angular_leaf_spot': {
            'name': 'Angular Leaf Spot',
            'pathogen': 'Pseudomonas syringae pv. tabaci',
            'symptoms': [
                'Angular lesions bounded by leaf veins',
                'Dark green water-soaked spots initially',
                'Brown necrotic centers with yellow halos',
                'Spots remain angular due to vein restrictions'
            ],
            'conditions': 'Cool, wet weather (20-25°C, high humidity)',
            'favorable_temp': '20-25°C',
            'favorable_humidity': '>70%',
            'recommendations': [
                'Remove and destroy all infected leaves immediately to reduce spread',
                'Avoid overhead irrigation — water at the base to keep foliage dry',
                'Apply copper-based bactericide (e.g., copper hydroxide) as a preventive spray',
                'Improve field drainage to reduce prolonged leaf wetness',
                'Do not work in the field while plants are wet — bacteria spread on hands and tools',
                'Rotate crops — avoid tobacco and solanaceous plants on the same land for at least 2 years',
                'Scout remaining plants every 2–3 days for new infections',
            ],
        },
        'wildfire': {
            'name': 'Wildfire',
            'pathogen': 'Pseudomonas syringae pv. tabaci (toxin-producing strain)',
            'symptoms': [
                'Circular to irregular brown spots',
                'Prominent yellow halos around lesions',
                'Halos caused by tabtoxin production',
                'Spots may merge under severe infection'
            ],
            'conditions': 'Warm, humid weather (28-32°C)',
            'favorable_temp': '28-32°C',
            'favorable_humidity': '50-70%',
            'recommendations': [
                'Remove and burn heavily infected plants — do not compost them',
                'Reduce nitrogen fertilizer application — excess nitrogen promotes soft, vulnerable growth',
                'Apply copper-based bactericide preventively, especially before expected rain',
                'Avoid any mechanical damage to plants — wounds are the main entry point for the bacteria',
                'Disinfect tools and equipment with bleach solution (1:10) between rows',
                'Ensure good plant spacing to improve airflow and reduce humidity around leaves',
                'Harvest early if infection is spreading rapidly to salvage unaffected leaves',
            ],
        },
        'healthy': {
            'name': 'Healthy Leaf',
            'pathogen': 'N/A',
            'symptoms': ['No visible disease symptoms'],
            'conditions': 'Normal growing conditions',
            'favorable_temp': '25-30°C',
            'favorable_humidity': '60-70%',
            'recommendations': [
                'Continue current management practices — the crop looks good',
                'Scout the field weekly for early signs of Angular Leaf Spot or Wildfire',
                'Maintain good plant spacing for airflow and to reduce humidity between plants',
                'Avoid overhead irrigation and water early in the day so leaves dry quickly',
                'Keep nitrogen fertilizer at recommended levels — do not over-apply',
                'Practice crop rotation at the end of the season to prevent soil buildup of pathogens',
                'Remove and dispose of crop debris after harvest to reduce disease carryover',
            ],
        },
        'unknown': {
            'name': 'Unknown/Unclassified',
            'pathogen': 'Unknown',
            'symptoms': ['Unable to determine disease type'],
            'conditions': 'Environmental conditions unclear',
            'favorable_temp': 'N/A',
            'favorable_humidity': 'N/A',
            'recommendations': [
                'Take a clearer photo in good lighting and re-upload for a better diagnosis',
                'Collect a sample of the affected leaf and consult a local agricultural extension officer',
                'Monitor the plant closely over the next 48 hours for symptom progression',
            ],
        }
    }
    return info.get(disease_code, info['unknown'])


def dataset_list(request):
    """List all images in the dataset"""
    images = LeafImage.objects.all()
    
    # Statistics
    stats = {
        'total': images.count(),
        'angular': images.filter(actual_disease='angular_leaf_spot').count(),
        'wildfire': images.filter(actual_disease='wildfire').count(),
        'healthy': images.filter(actual_disease='healthy').count(),
        'unknown': images.filter(actual_disease='unknown').count(),
    }
    
    context = {
        'images': images,
        'stats': stats,
    }
    return render(request, 'diagosis/dataset.html', context)


def dashboard(request):
    """Analytics dashboard with charts and insights"""
    images = LeafImage.objects.all()
    
    # Basic stats
    total = images.count()
    
    # Disease distribution
    disease_counts = images.values('predicted_disease').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Average confidence by disease
    confidence_by_disease = images.values('predicted_disease').annotate(
        avg_confidence=Avg('confidence_score')
    ).order_by('-avg_confidence')
    
    # Recent uploads (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)
    recent_uploads = images.filter(uploaded_at__gte=week_ago).count()
    
    # High confidence predictions (>80%)
    high_confidence = images.filter(confidence_score__gte=80).count()
    
    # API status
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    api_status = 'Connected' if api_key else 'Not configured (using fallback)'
    
    context = {
        'total': total,
        'disease_counts': list(disease_counts),
        'confidence_by_disease': list(confidence_by_disease),
        'recent_uploads': recent_uploads,
        'high_confidence': high_confidence,
        'api_status': api_status,
        'recent_images': images[:6],
    }
    return render(request, 'diagosis/dashboard.html', context)
