# Tobacco Disease Classifier - Usage Guide

A Django web application that uses Claude Vision AI to classify tobacco leaf diseases (Angular Leaf Spot vs Wildfire).

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd plant-diagnosis

# Install dependencies
pip install uv
uv sync
```

### 2. Configure Environment

Create `.env` file in project root:

```env
# Required: Get API key from https://console.anthropic.com/
ANTHROPIC_API_KEY=your-api-key-here

# Optional (defaults work for development)
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-production
```

### 3. Database Setup

```bash
# Run migrations
uv run python manage.py makemigrations
uv run python manage.py migrate

# Create admin user (optional)
uv run python manage.py createsuperuser
```

### 4. Start Server

```bash
uv run python manage.py runserver
```

Visit: http://127.0.0.1:8000/

---

## Usage

### Upload & Classify a Leaf Image

1. Go to http://127.0.0.1:8000/
2. Click "Upload Image"
3. Select a tobacco leaf photo
4. Enter environmental conditions (temp, humidity, moisture)
5. Click "Analyze Image"
6. View AI classification results with reasoning

### Dashboard

The homepage shows:
- Total images analyzed
- Disease distribution (charts)
- Recent uploads with predictions
- API connection status

### Dataset Management

**View all images:** http://127.0.0.1:8000/dataset/

**Admin panel:** http://127.0.0.1:8000/admin/
- Login with superuser credentials
- Edit image labels (actual_disease)
- Manage all records

---

## Bulk Import Dataset

### Option 1: Import from folders

Organize images in `datasets/` folder:
```
datasets/
├── angular_leaf_spot/    # Angular Leaf Spot images
├── wildfire/             # Wildfire images
├── healthy/              # Healthy leaf images
└── unlabeled/            # Unknown/needs labeling
```

Import all at once:
```bash
uv run python import_dataset.py
```

### Option 2: Manual upload via web

1. Go to http://127.0.0.1:8000/upload/
2. Upload images one by one
3. Set correct disease label
4. Environmental conditions are optional

---

## Testing Claude API

Test API is working before uploading:

```bash
# Add your API key to .env first
uv run python test_claude.py
```

This will classify your WhatsApp images and show the response.

---

## How It Works

### AI Classification Flow:

1. **Image Upload** → Stored in `media/leaf_images/`
2. **Claude Vision API** → Analyzes image + environmental conditions
3. **Prediction** → Disease type + confidence score + reasoning
4. **Storage** → Saved to database with prediction details
5. **Display** → Results page shows disease info + AI explanation

### Without API Key:

Falls back to rule-based classification using environmental conditions only:
- Angular Leaf Spot: Cool (<25°C) + Humid (>70%)
- Wildfire: Warm (>28°C) + Moderate humidity (50-70%)

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `uv run python manage.py runserver` | Start web server |
| `uv run python manage.py makemigrations` | Create DB migrations |
| `uv run python manage.py migrate` | Apply migrations |
| `uv run python import_dataset.py` | Bulk import from folders |
| `uv run python import_dataset.py --verify` | Check prediction accuracy |
| `uv run python test_claude.py` | Test API with existing images |

---

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
- Add your API key to `.env` file
- Get key from: https://console.anthropic.com/

### ModuleNotFoundError
```bash
uv sync  # Reinstall dependencies
```

### Database locked errors
```bash
# Stop server, then:
rm db.sqlite3
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

### Images not showing
```bash
# Check media folder exists
mkdir -p media/leaf_images
```

---

## Cost Information

- **Claude API**: ~$0.003-0.015 per image (Haiku model)
- **Dataset**: Free, use your own photos or public datasets
- **No API key**: Free (rule-based fallback)

---

## File Structure

```
plant-diagnosis/
├── tobaccoclassifier/      # Django project
│   ├── diagosis/           # Main app
│   │   ├── models.py       # LeafImage model
│   │   ├── views.py        # Upload & classification logic
│   │   ├── claude_classifier.py  # AI integration
│   │   └── templates/        # HTML templates
│   └── settings.py         # Django settings
├── datasets/               # Training images
├── media/                  # Uploaded images (auto-created)
├── .env                    # API keys (not in git)
├── manage.py               # Django commands
└── import_dataset.py       # Bulk import script
```

---

## Support

For issues:
1. Check `.env` file has correct API key
2. Run `uv sync` to update dependencies
3. Check Django admin for data issues
4. Review logs in terminal
