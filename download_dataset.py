#!/usr/bin/env python3
"""
Download tobacco disease datasets for testing.
Supports multiple sources:
1. Hugging Face (PlantVillage) - General plant diseases including some tobacco
2. Kaggle (requires kaggle CLI)
3. Creates organized folders from existing images
"""

import os
import sys
import shutil
from pathlib import Path
import urllib.request
import zipfile

BASE_DIR = Path(__file__).parent
DATASET_DIR = BASE_DIR / "datasets"


def create_dataset_structure():
    """Create organized folder structure for datasets"""
    print("Creating dataset directory structure...")
    
    diseases = ['angular_leaf_spot', 'wildfire', 'healthy', 'other']
    
    for disease in diseases:
        folder = DATASET_DIR / disease
        folder.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {folder}")
    
    return DATASET_DIR


def organize_existing_images():
    """Move your WhatsApp images into the dataset folders for manual labeling"""
    print("\nOrganizing existing WhatsApp images...")
    
    # Find all WhatsApp images
    whatsapp_images = list(BASE_DIR.glob("WhatsApp Image*.jpeg"))
    
    if not whatsapp_images:
        print("  ⚠ No WhatsApp images found")
        return
    
    # Copy to 'unlabeled' folder for manual sorting
    unlabeled_dir = DATASET_DIR / "unlabeled"
    unlabeled_dir.mkdir(exist_ok=True)
    
    for img_path in whatsapp_images:
        dest = unlabeled_dir / img_path.name
        shutil.copy2(img_path, dest)
        print(f"  ✓ Copied {img_path.name} -> unlabeled/")
    
    print(f"\n  📁 {len(whatsapp_images)} images ready for manual labeling in: {unlabeled_dir}")
    print("  💡 After labeling, move images to: angular_leaf_spot/, wildfire/, healthy/ folders")


def download_plantvillage_sample():
    """Download a sample from PlantVillage via Hugging Face"""
    print("\n" + "="*70)
    print("PlantVillage Dataset (Hugging Face)")
    print("="*70)
    
    try:
        from datasets import load_dataset
        
        print("Downloading PlantVillage dataset...")
        print("(This may take a few minutes - ~1.5GB dataset)")
        
        # Load only a subset for tobacco-related images
        dataset = load_dataset("mohanty/PlantVillage", "color", split="train", streaming=True)
        
        # Filter for tobacco-related images (if any)
        tobacco_samples = []
        count = 0
        
        for sample in dataset:
            label = sample['label']
            # PlantVillage has tobacco classes - look for them
            if 'tobacco' in label.lower():
                tobacco_samples.append(sample)
                count += 1
                if count >= 20:  # Download 20 samples
                    break
        
        if tobacco_samples:
            print(f"✓ Found {len(tobacco_samples)} tobacco images")
            # Save them
            for i, sample in enumerate(tobacco_samples):
                img = sample['image']
                label = sample['label']
                
                # Determine folder based on label
                if 'bacterial' in label.lower() or 'angular' in label.lower():
                    folder = DATASET_DIR / 'angular_leaf_spot'
                elif 'wildfire' in label.lower():
                    folder = DATASET_DIR / 'wildfire'
                elif 'healthy' in label.lower():
                    folder = DATASET_DIR / 'healthy'
                else:
                    folder = DATASET_DIR / 'other'
                
                folder.mkdir(exist_ok=True)
                img.save(folder / f"plantvillage_{i}.jpg")
            
            print(f"✓ Saved {len(tobacco_samples)} images to {DATASET_DIR}")
        else:
            print("⚠ No tobacco images found in first 1000 samples")
            print("  You can still use general leaf disease images for testing")
            
    except ImportError:
        print("❌ Hugging Face 'datasets' library not installed")
        print("   Install with: pip install datasets")
    except Exception as e:
        print(f"❌ Error: {e}")


def print_manual_download_instructions():
    """Print instructions for manual dataset download"""
    print("\n" + "="*70)
    print("MANUAL DATASET DOWNLOAD OPTIONS")
    print("="*70)
    
    print("\n1. Kaggle Tobacco Dataset (RECOMMENDED)")
    print("   URL: https://www.kaggle.com/datasets/chzili/dataset-for-tobacco-leaf-disease-segmentation")
    print("   Steps:")
    print("   a) Create Kaggle account (free)")
    print("   b) Download dataset")
    print("   c) Extract to: ./datasets/")
    
    print("\n2. ResearchGate Tobacco Dataset")
    print("   Paper: Tobacco plant disease dataset")
    print("   URL: https://www.researchgate.net/publication/364508413_Tobacco_plant_disease_dataset")
    print("   Steps:")
    print("   a) Request dataset from authors")
    print("   b) Contains: 2009 images, 12 diseases including Wildfire & Angular Leaf Spot")
    
    print("\n3. PlantVillage (Subset)")
    print("   URL: https://github.com/spMohanty/PlantVillage-Dataset")
    print("   Steps:")
    print("   a) git clone https://github.com/spMohanty/PlantVillage-Dataset.git")
    print("   b) Look for 'tobacco' folder in raw/color/")
    print("   c) Copy relevant images to ./datasets/")
    
    print("\n4. Use Your Own Photos")
    print("   a) Take clear photos of infected leaves")
    print("   b) Place in ./datasets/unlabeled/")
    print("   c) Label them manually via Django admin")


def main():
    print("="*70)
    print("TOBACCO DISEASE DATASET DOWNLOADER")
    print("="*70)
    
    # Create structure
    create_dataset_structure()
    
    # Organize existing images
    organize_existing_images()
    
    # Try to download from Hugging Face
    try:
        download_plantvillage_sample()
    except:
        pass
    
    # Print manual options
    print_manual_download_instructions()
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print(f"1. Organize images into folders under: {DATASET_DIR}/")
    print("   - angular_leaf_spot/  <- Angular Leaf Spot images")
    print("   - wildfire/             <- Wildfire images")
    print("   - healthy/              <- Healthy leaf images")
    print("   - unlabeled/            <- Images to be labeled")
    print("\n2. Bulk upload to Django:")
    print("   a) Start server: uv run python manage.py runserver")
    print("   b) Go to http://127.0.0.1:8000/upload/")
    print("   c) Upload images with correct disease labels")
    print("\n3. Or use Django admin to label existing uploads:")
    print("   a) Go to http://127.0.0.1:8000/admin/")
    print("   b) Click 'Leaf images'")
    print("   c) Edit 'actual_disease' field for each image")
    print("="*70)


if __name__ == '__main__':
    main()
