# 🚀 GitHub Repository Setup Guide

## Prerequisites

1. Git installed on your system
2. GitHub account with access to: https://github.com/ChiragPatankar/Intel_Unnati_2026
3. GitHub CLI or Git credentials configured

## Steps to Upload Project

### 1. Initialize Git Repository (if not already done)

```bash
cd D:\Intel_Unnati
git init
```

### 2. Add All Files (respecting .gitignore)

```bash
git add .
```

### 3. Verify What Will Be Committed

```bash
git status
```

**Expected exclusions (should NOT appear):**
- `backend/venv/` - Virtual environment
- `backend/uploads/*` - User uploaded files
- `backend/profiles/*` - User profiles
- `backend/.env` - API keys
- `frontend/node_modules/` - Node dependencies
- `__pycache__/` - Python cache files
- `*.pyc` - Compiled Python files

### 4. Create Initial Commit

```bash
git commit -m "Initial commit: AI-Powered Form Filling Assistant

- Complete backend with OCR, entity extraction, and form mapping
- React frontend with multi-language support
- Voice input functionality
- PDF generation
- 6 government form templates
- Performance benchmarks
- Complete documentation"
```

### 5. Add Remote Repository

```bash
git remote add origin https://github.com/ChiragPatankar/Intel_Unnati_2026.git
```

### 6. Push to GitHub

```bash
git branch -M main
git push -u origin main
```

## If Repository Already Has Content

If the repository is not empty, you may need to pull first:

```bash
git pull origin main --allow-unrelated-histories
# Resolve any conflicts if they occur
git push -u origin main
```

## Alternative: Using GitHub CLI

If you have GitHub CLI installed:

```bash
gh repo clone ChiragPatankar/Intel_Unnati_2026
cd Intel_Unnati_2026
# Copy all files from D:\Intel_Unnati (except .git)
git add .
git commit -m "Initial commit: AI-Powered Form Filling Assistant"
git push
```

## Important Notes

### Files NOT Uploaded (Protected by .gitignore):
- ✅ `.env` files (contains API keys)
- ✅ `venv/` (virtual environment)
- ✅ `node_modules/` (Node.js dependencies)
- ✅ `uploads/` (user uploaded documents)
- ✅ `profiles/` (user profile data)
- ✅ `__pycache__/` (Python cache)
- ✅ `benchmarks/results/` (generated benchmark files)

### Files Included:
- ✅ All source code
- ✅ Configuration files (`.env.example` instead of `.env`)
- ✅ Documentation (README.md, DESIGN.md, etc.)
- ✅ Requirements files
- ✅ Package.json files
- ✅ Test files
- ✅ Benchmark scripts

## After Upload

1. **Add .env.example to repository** - Users can copy this to create their own .env
2. **Update README.md** - Add setup instructions for API keys
3. **Add repository description** on GitHub:
   - "AI-Powered Form Filling Assistant for Indian Citizen Services - Auto-fill government forms using OCR and voice input"

## Security Checklist

Before pushing, ensure:
- ✅ No `.env` files are committed
- ✅ No API keys in source code
- ✅ No user data (uploads, profiles) committed
- ✅ `.gitignore` is properly configured

