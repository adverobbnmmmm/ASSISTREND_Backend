#!/usr/bin/env bash

# Exit on any error
set -e

echo "📦 Installing dependencies for accounts..."
pip install -r ./accounts/requirements.txt

echo "📦 Installing dependencies for social_service..."
pip install -r ./social_service/requirements.txt

echo "✅ Dependencies installed!"
