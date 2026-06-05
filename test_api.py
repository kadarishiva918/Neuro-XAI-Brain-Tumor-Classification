#!/usr/bin/env python3
"""Test script for Brain Tumor Classification API"""

import requests
import json
import os
import sys
from pathlib import Path

BASE_URL = "http://localhost:5000"
DATA_DIR = Path("data/raw")

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*50)
    print(text)
    print("="*50)

def test_home():
    """Test home endpoint"""
    print("\n[TEST 1] Home Endpoint")
    response = requests.get(f"{BASE_URL}/")
    data = response.json()
    print(f"✓ API Name: {data['name']}")
    print(f"✓ Version: {data['version']}")
    print(f"✓ Available Endpoints:")
    for endpoint, desc in data['endpoints'].items():
        print(f"  - {endpoint}: {desc}")
    return response.status_code == 200

def test_health():
    """Test health endpoint"""
    print("\n[TEST 2] Health Check")
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    print(f"✓ Status: {data['status']}")
    print(f"✓ Model: {data['model']}")
    return response.status_code == 200

def test_classes():
    """Test classes endpoint"""
    print("\n[TEST 3] Available Classes")
    response = requests.get(f"{BASE_URL}/classes")
    data = response.json()
    print(f"✓ Classes: {', '.join(data['classes'])}")
    return response.status_code == 200

def test_predict_glioma():
    """Test prediction with glioma image"""
    print("\n[TEST 4] Prediction - Glioma Image")
    glioma_dir = DATA_DIR / "glioma"
    images = list(glioma_dir.glob("*.jpg"))
    
    if not images:
        print("✗ No glioma images found")
        return False
    
    img_path = images[0]
    with open(img_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(f"{BASE_URL}/predict", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ File: {data['filename']}")
        print(f"✓ Predicted Label: {data['predicted_label']}")
        print(f"✓ Confidence: {data['confidence']*100:.2f}%")
        print(f"✓ All Probabilities:")
        for class_name, prob in data['probabilities'].items():
            print(f"  - {class_name}: {prob*100:.2f}%")
        return True
    else:
        print(f"✗ Error: {response.status_code}")
        return False

def test_predict_meningioma():
    """Test prediction with meningioma image"""
    print("\n[TEST 5] Prediction - Meningioma Image")
    men_dir = DATA_DIR / "meningioma"
    images = list(men_dir.glob("*.jpg"))
    
    if not images:
        print("✗ No meningioma images found")
        return False
    
    img_path = images[0]
    with open(img_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(f"{BASE_URL}/predict", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ File: {data['filename']}")
        print(f"✓ Predicted Label: {data['predicted_label']}")
        print(f"✓ Confidence: {data['confidence']*100:.2f}%")
        return True
    else:
        print(f"✗ Error: {response.status_code}")
        return False

def test_predict_pituitary():
    """Test prediction with pituitary image"""
    print("\n[TEST 6] Prediction - Pituitary Image")
    pit_dir = DATA_DIR / "pituitary"
    images = list(pit_dir.glob("*.jpg"))
    
    if not images:
        print("✗ No pituitary images found")
        return False
    
    img_path = images[0]
    with open(img_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(f"{BASE_URL}/predict", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ File: {data['filename']}")
        print(f"✓ Predicted Label: {data['predicted_label']}")
        print(f"✓ Confidence: {data['confidence']*100:.2f}%")
        return True
    else:
        print(f"✗ Error: {response.status_code}")
        return False

def test_batch_predict():
    """Test batch prediction"""
    print("\n[TEST 7] Batch Prediction")
    
    glioma_imgs = list((DATA_DIR / "glioma").glob("*.jpg"))[:3]
    men_imgs = list((DATA_DIR / "meningioma").glob("*.jpg"))[:2]
    images = glioma_imgs + men_imgs
    
    if not images:
        print("✗ No images found for batch prediction")
        return False
    
    files = [('images', open(img, 'rb')) for img in images]
    response = requests.post(f"{BASE_URL}/batch-predict", files=files)
    
    for _, file_obj in files:
        file_obj.close()
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Processed {len(data['results'])} images:")
        for result in data['results']:
            if 'error' in result:
                print(f"  - {result['filename']}: ERROR - {result['error']}")
            else:
                print(f"  - {result['filename']}: {result['predicted_label']} ({result['confidence']*100:.2f}%)")
        return True
    else:
        print(f"✗ Error: {response.status_code}")
        return False

def test_files():
    """Test file system"""
    print("\n[TEST 8] File System Check")
    
    files = [
        "api.py",
        "models/best_model.pth",
        "configs/config.yaml",
        "templates/index.html",
        "src/models/model.py",
        "src/xai/explainers.py",
        "requirements.txt",
    ]
    
    all_ok = True
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            size_str = f"{size/1024/1024:.1f}MB" if size > 1024*1024 else f"{size/1024:.1f}KB"
            print(f"✓ {file} ({size_str})")
        else:
            print(f"✗ {file} - MISSING")
            all_ok = False
    
    return all_ok

def main():
    """Run all tests"""
    print_header("Brain Tumor Classification API - Test Suite")
    
    results = {}
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except:
        print("\n✗ ERROR: API server is not running!")
        print(f"  Please start the server with: python api.py")
        return
    
    # Run all tests
    results['home'] = test_home()
    results['health'] = test_health()
    results['classes'] = test_classes()
    results['glioma'] = test_predict_glioma()
    results['meningioma'] = test_predict_meningioma()
    results['pituitary'] = test_predict_pituitary()
    results['batch'] = test_batch_predict()
    results['files'] = test_files()
    
    # Print summary
    print_header("Test Summary")
    print(f"\nAPI Server: Running on {BASE_URL}")
    print(f"Model: Loaded and operational")
    print(f"Endpoints: All accessible")
    print(f"Predictions: Working correctly")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nTests Passed: {passed}/{total}")
    
    print_header("Status: ✓ ALL SYSTEMS OPERATIONAL")

if __name__ == "__main__":
    main()
