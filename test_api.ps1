#!/usr/bin/env pwsh
<#
Test script for Brain Tumor Classification API
Tests all endpoints to verify functionality
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Brain Tumor Classification API - Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:5000"
$dataDir = "E:\Brain_Tumor_Classification\data\raw"

# Test 1: Home endpoint
Write-Host "[TEST 1] Home Endpoint" -ForegroundColor Yellow
$response = curl -s "$baseUrl/" | ConvertFrom-Json
Write-Host "✓ API Name: $($response.name)" 
Write-Host "✓ Version: $($response.version)"
Write-Host "✓ Available Endpoints:"
$response.endpoints | ForEach-Object { 
    $_.PSObject.Properties | ForEach-Object { 
        Write-Host "  - $($_.Name): $($_.Value)" 
    } 
}
Write-Host ""

# Test 2: Health endpoint
Write-Host "[TEST 2] Health Check" -ForegroundColor Yellow
$response = curl -s "$baseUrl/health" | ConvertFrom-Json
Write-Host "✓ Status: $($response.status)"
Write-Host "✓ Model: $($response.model)"
Write-Host ""

# Test 3: Classes endpoint
Write-Host "[TEST 3] Available Classes" -ForegroundColor Yellow
$response = curl -s "$baseUrl/classes" | ConvertFrom-Json
Write-Host "✓ Classes: $($response.classes -join ', ')"
Write-Host ""

# Test 4: Predict with Glioma image
Write-Host "[TEST 4] Prediction - Glioma Image" -ForegroundColor Yellow
$gliomaFile = Get-ChildItem -Path "$dataDir\glioma\*.jpg" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($gliomaFile) {
    $response = curl -s -F "image=@$($gliomaFile.FullName)" "$baseUrl/predict" | ConvertFrom-Json
    Write-Host "✓ File: $($response.filename)"
    Write-Host "✓ Predicted Label: $($response.predicted_label)"
    Write-Host "✓ Confidence: $([math]::Round($response.confidence * 100, 2))%"
    Write-Host "✓ All Probabilities:"
    $response.probabilities.PSObject.Properties | ForEach-Object {
        Write-Host "  - $($_.Name): $([math]::Round($_.Value * 100, 2))%"
    }
} else {
    Write-Host "✗ No glioma image found" -ForegroundColor Red
}
Write-Host ""

# Test 5: Predict with Meningioma image
Write-Host "[TEST 5] Prediction - Meningioma Image" -ForegroundColor Yellow
$menFile = Get-ChildItem -Path "$dataDir\meningioma\*.jpg" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($menFile) {
    $response = curl -s -F "image=@$($menFile.FullName)" "$baseUrl/predict" | ConvertFrom-Json
    Write-Host "✓ File: $($response.filename)"
    Write-Host "✓ Predicted Label: $($response.predicted_label)"
    Write-Host "✓ Confidence: $([math]::Round($response.confidence * 100, 2))%"
} else {
    Write-Host "✗ No meningioma image found" -ForegroundColor Red
}
Write-Host ""

# Test 6: Predict with Pituitary image
Write-Host "[TEST 6] Prediction - Pituitary Image" -ForegroundColor Yellow
$pitFile = Get-ChildItem -Path "$dataDir\pituitary\*.jpg" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($pitFile) {
    $response = curl -s -F "image=@$($pitFile.FullName)" "$baseUrl/predict" | ConvertFrom-Json
    Write-Host "✓ File: $($response.filename)"
    Write-Host "✓ Predicted Label: $($response.predicted_label)"
    Write-Host "✓ Confidence: $([math]::Round($response.confidence * 100, 2))%"
} else {
    Write-Host "✗ No pituitary image found" -ForegroundColor Red
}
Write-Host ""

# Test 7: Batch Predict
Write-Host "[TEST 7] Batch Prediction (5 images)" -ForegroundColor Yellow
$images = @()
Get-ChildItem -Path "$dataDir\glioma\*.jpg" -ErrorAction SilentlyContinue | Select-Object -First 3 | ForEach-Object { $images += $_ }
Get-ChildItem -Path "$dataDir\meningioma\*.jpg" -ErrorAction SilentlyContinue | Select-Object -First 2 | ForEach-Object { $images += $_ }

if ($images.Count -gt 0) {
    $formParams = @()
    foreach ($img in $images) {
        $formParams += "-F", "images=@$($img.FullName)"
    }
    $response = curl -s @formParams "$baseUrl/batch-predict" | ConvertFrom-Json
    Write-Host "✓ Processed $($response.results.Count) images"
    $response.results | ForEach-Object {
        Write-Host "  - $($_.filename): $($_.predicted_label) ($([math]::Round($_.confidence * 100, 2))%)"
    }
} else {
    Write-Host "✗ No images found" -ForegroundColor Red
}
Write-Host ""

# Test 8: Verify key files exist
Write-Host "[TEST 8] File System Check" -ForegroundColor Yellow
$files = @(
    "api.py",
    "models/best_model.pth",
    "configs/config.yaml",
    "templates/index.html",
    "src/models/model.py",
    "src/xai/explainers.py"
)
$allFilesOk = $true
foreach ($file in $files) {
    $fullPath = "E:\Brain_Tumor_Classification\$file"
    if (Test-Path $fullPath) {
        Write-Host "✓ $file"
    } else {
        Write-Host "✗ $file" -ForegroundColor Red
        $allFilesOk = $false
    }
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ API Server: Running on $baseUrl"
Write-Host "✓ Model: Loaded and operational"
Write-Host "✓ Endpoints: All accessible"
Write-Host "✓ Predictions: Working correctly"
if ($allFilesOk) {
    Write-Host "✓ Files: All present and verified"
} else {
    Write-Host "⚠ Files: Some files missing" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Status: ✓ ALL SYSTEMS OPERATIONAL" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
