#!/usr/bin/env python3
"""
Bulk import images from datasets/ folder into Django.
Labels images based on which subfolder they're in:
- angular_leaf_spot/ -> actual_disease = 'angular_leaf_spot'
- wildfire/ -> actual_disease = 'wildfire'
- healthy/ -> actual_disease = 'healthy'
- unlabeled/ or other/ -> actual_disease = 'unknown'
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tobaccoclassifier.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from pathlib import Path
from tobaccoclassifier.diagosis.models import LeafImage
from tobaccoclassifier.diagosis.claude_classifier import classify_with_claude
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DATASET_DIR = BASE_DIR / "datasets"

# Map folder names to disease codes
FOLDER_TO_DISEASE = {
    'angular_leaf_spot': 'angular_leaf_spot',
    'wildfire': 'wildfire',
    'healthy': 'healthy',
    'unlabeled': 'unknown',
    'other': 'unknown',
}


def import_images(auto_classify=True, test_conditions=None):
    """
    Import all images from datasets folder into Django.
    
    Args:
        auto_classify: If True, also run Claude classification on each image
        test_conditions: Dict with temperature, humidity, moisture for classification
    """
    if test_conditions is None:
        test_conditions = {
            'temperature': 25,
            'humidity': 65,
            'moisture': 45
        }
    
    print("="*70)
    print("BULK IMPORT - DATASET IMAGES")
    print("="*70)
    
    total_imported = 0
    total_skipped = 0
    
    # Process each disease folder
    for folder_name, disease_code in FOLDER_TO_DISEASE.items():
        folder_path = DATASET_DIR / folder_name
        
        if not folder_path.exists():
            continue
        
        # Find all images in this folder
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
        images = []
        for ext in image_extensions:
            images.extend(folder_path.glob(ext))
        
        if not images:
            continue
        
        print(f"\n📁 {folder_name}/ ({len(images)} images) -> {disease_code}")
        print("-"*70)
        
        for img_path in images:
            # Check if already imported (by filename)
            existing = LeafImage.objects.filter(
                image__endswith=img_path.name
            ).first()
            
            if existing:
                print(f"  ⏭️  Skipped (already imported): {img_path.name}")
                total_skipped += 1
                continue
            
            try:
                # Create LeafImage instance
                with open(img_path, 'rb') as f:
                    from django.core.files import File
                    
                    leaf = LeafImage(
                        actual_disease=disease_code,
                        temperature=test_conditions.get('temperature'),
                        humidity=test_conditions.get('humidity'),
                        moisture_content=test_conditions.get('moisture'),
                        notes=f"Imported from datasets/{folder_name}/"
                    )
                    
                    # Save with image file
                    leaf.image.save(
                        img_path.name,
                        File(f),
                        save=True
                    )
                    
                    print(f"  ✓ Imported: {img_path.name} (labeled as: {disease_code})")
                    total_imported += 1
                    
                    # Optionally auto-classify with Claude
                    if auto_classify and os.environ.get('ANTHROPIC_API_KEY'):
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
                            
                            match_status = "✓" if result['disease'] == disease_code else "✗"
                            print(f"    {match_status} Claude predicts: {result['disease']} ({result['confidence']:.1f}%)")
                            
                        except Exception as e:
                            print(f"    ⚠ Claude classification failed: {e}")
                    
            except Exception as e:
                print(f"  ❌ Error importing {img_path.name}: {e}")
    
    print("\n" + "="*70)
    print("IMPORT SUMMARY")
    print("="*70)
    print(f"  Total imported: {total_imported}")
    print(f"  Total skipped (already exist): {total_skipped}")
    print(f"  Total in database: {LeafImage.objects.count()}")
    
    # Show breakdown by actual_disease
    print("\n  Dataset composition:")
    for disease_code, label in LeafImage.DISEASE_CHOICES:
        count = LeafImage.objects.filter(actual_disease=disease_code).count()
        if count > 0:
            print(f"    - {label}: {count}")
    
    print("="*70)
    print("\nNext steps:")
    print("1. View imported images: http://127.0.0.1:8000/admin/")
    print("2. Check predictions vs labels in dataset view: http://127.0.0.1:8000/dataset/")
    print("3. Start server: uv run python manage.py runserver")
    print("="*70)


def verify_classifications():
    """Check how many Claude predictions match the actual labels"""
    print("\n" + "="*70)
    print("CLASSIFICATION ACCURACY CHECK")
    print("="*70)
    
    images = LeafImage.objects.exclude(actual_disease='unknown')
    
    if not images:
        print("No labeled images to check.")
        return
    
    correct = 0
    incorrect = 0
    
    for leaf in images:
        if leaf.predicted_disease == leaf.actual_disease:
            correct += 1
        else:
            incorrect += 1
            print(f"\n✗ Mismatch:")
            print(f"  Image: {leaf.image.name}")
            print(f"  Actual: {leaf.get_actual_disease_display()}")
            print(f"  Predicted: {leaf.get_predicted_disease_display()}")
            print(f"  Confidence: {leaf.confidence_score:.1f}%")
    
    total = correct + incorrect
    accuracy = (correct / total * 100) if total > 0 else 0
    
    print(f"\n  Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    print(f"  Correct: {correct}")
    print(f"  Incorrect: {incorrect}")
    print("="*70)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Import dataset images into Django')
    parser.add_argument('--no-classify', action='store_true', 
                        help='Skip Claude classification (faster)')
    parser.add_argument('--verify', action='store_true',
                        help='Check accuracy of existing predictions')
    parser.add_argument('--temp', type=float, default=25,
                        help='Default temperature for imported images (°C)')
    parser.add_argument('--humidity', type=float, default=65,
                        help='Default humidity for imported images (%)')
    parser.add_argument('--moisture', type=float, default=45,
                        help='Default moisture for imported images (%)')
    
    args = parser.parse_args()
    
    if args.verify:
        verify_classifications()
    else:
        conditions = {
            'temperature': args.temp,
            'humidity': args.humidity,
            'moisture': args.moisture
        }
        import_images(
            auto_classify=not args.no_classify,
            test_conditions=conditions
        )
