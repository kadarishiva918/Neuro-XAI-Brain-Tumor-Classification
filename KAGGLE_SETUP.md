# Kaggle Dataset Setup Guide

## Quick Start

### 1. Install Kaggle API

```bash
pip install kaggle
```

### 2. Set Up Kaggle Credentials

#### Step-by-Step:

1. **Visit Kaggle Settings**
   - Go to: https://www.kaggle.com/settings/account
   
2. **Generate API Token**
   - Scroll down to "API" section
   - Click "Create New API Token"
   - This downloads `kaggle.json`

3. **Place Credentials File**

   **Windows:**
   ```
   Move/Copy kaggle.json to: C:\Users\<YourUsername>\.kaggle\kaggle.json
   ```
   
   **Linux/Mac:**
   ```bash
   mkdir -p ~/.kaggle
   cp kaggle.json ~/.kaggle/
   chmod 600 ~/.kaggle/kaggle.json
   ```

4. **Verify Setup**
   ```bash
   kaggle datasets list
   ```
   Should show a list of datasets without errors.

### 3. Download Dataset

Run the automated setup script:

```bash
python setup_kaggle_dataset.py
```

This will:
- ✅ Verify Kaggle API setup
- ✅ Download Brain Tumor MRI dataset
- ✅ Organize into class directories
- ✅ Validate and count images
- ✅ Save statistics

### 4. Manual Download (Alternative)

If you prefer to download manually:

1. Visit: https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset
2. Click "Download" button
3. Extract to `data/raw/`
4. Ensure structure:
   ```
   data/raw/
   ├── glioma/
   ├── meningioma/
   ├── pituitary/
   └── no_tumor/
   ```

## Dataset Information

**Dataset Name:** Brain Tumor MRI Dataset  
**Source:** Kaggle  
**Link:** https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset  
**Size:** ~5GB (approximately)  
**Images:** ~7,000+ MRI scans

### Classes:
- **Glioma**: ~1,300 images
- **Meningioma**: ~1,300 images
- **Pituitary**: ~1,300 images
- **No Tumor**: ~1,600 images

## Troubleshooting

### Issue: "Kaggle credentials not found"

**Solution:**
```bash
# Verify credentials exist
# Windows:
dir C:\Users\<YourUsername>\.kaggle\

# Linux/Mac:
ls ~/.kaggle/

# Should see: kaggle.json
```

### Issue: "Permission denied" (Linux/Mac)

**Solution:**
```bash
chmod 600 ~/.kaggle/kaggle.json
```

### Issue: Dataset not found on Kaggle

**Solution:**
1. Make sure you've accepted the dataset terms:
   - Visit: https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset
   - Click "I Understand and Accept"
2. Wait a few minutes for Kaggle API to sync
3. Try again

### Issue: Download stops or times out

**Solution:**
```bash
# Resume with a fresh run:
python setup_kaggle_dataset.py

# Or manually download from browser and extract
```

### Issue: "kaggle: command not found"

**Solution:**
```bash
pip install --upgrade kaggle
python -m pip install --upgrade kaggle
```

## Verify Installation

After downloading, verify the dataset:

```bash
# Check structure
python -c "from pathlib import Path; import json; \
stats = json.load(open('data/raw/dataset_stats.json')); \
print('Dataset Stats:', stats); \
print('Total:', sum(stats.values()))"
```

## Next Steps

Once dataset is ready:

```bash
# Start training
python train.py --data-dir data/raw

# Monitor training
tensorboard --logdir=results/logs

# Evaluate model
python evaluate.py --model-path models/best_model.pth

# Generate explanations
python generate_explanations.py --model-path models/best_model.pth
```

## Dataset License & Attribution

**License:** CC0 1.0 Universal (Public Domain)

**Citation:**
```
@dataset{brain_tumor_mri,
  title={Brain Tumor MRI Dataset},
  author={Nickparvar, Masoud},
  year={2021},
  url={https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset}
}
```

## FAQ

**Q: How much storage do I need?**  
A: ~5-8GB for the dataset + ~2GB for models and results

**Q: Can I use a subset for testing?**  
A: Yes, modify the script or manually use fewer images per class

**Q: What if I don't have Kaggle account?**  
A: Create one free at https://www.kaggle.com/register

**Q: How long does download take?**  
A: Depends on internet speed, typically 10-30 minutes for 5GB

**Q: Can I use a different dataset?**  
A: Yes, see `QUICKSTART.md` for dataset structure requirements
