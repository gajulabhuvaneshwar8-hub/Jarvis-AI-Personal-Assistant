#!/bin/bash
# ==============================================================================
#  JARVIS AI PERSONAL ASSISTANT - 1-CLICK MACOS / LINUX SETUP SCRIPT
# ==============================================================================

set -e

echo ""
echo "=================================================================="
echo "          ⚡ WELCOME TO JARVIS AI ASSISTANT SETUP ⚡             "
echo "=================================================================="
echo ""

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ and re-run."
    exit 1
fi

echo "✅ Python $(python3 --version) detected."

# 2. Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating isolated Python environment (.venv)..."
    python3 -m venv .venv
fi

echo "📦 Activating environment..."
source .venv/bin/activate

# 3. Upgrade pip and install requirements
echo "⬇️  Installing required packages..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure Groq API Key
CONFIG_DIR="$HOME/.openjarvis"
mkdir -p "$CONFIG_DIR"

if [ ! -f "$CONFIG_DIR/free.key" ]; then
    echo ""
    echo "🔑 Setup your free Groq API key (from https://console.groq.com/keys):"
    read -p "Enter Groq API Key (or press Enter to skip and use local offline mode): " API_KEY
    if [ -n "$API_KEY" ]; then
        echo "$API_KEY" > "$CONFIG_DIR/free.key"
        chmod 600 "$CONFIG_DIR/free.key"
        echo "✅ API Key saved."
    else
        echo "⚠️ Skipping API key. Jarvis will run in local offline mode."
    fi
else
    echo "✅ Found existing Groq API key."
fi

# 5. Launch Option
echo ""
echo "=================================================================="
echo "          🎉 JARVIS SETUP COMPLETED SUCCESSFULLY!                "
echo "=================================================================="
echo ""
echo "To start Jarvis at any time, run:"
echo "    source .venv/bin/activate && python jarvis_voice.py"
echo ""
echo "To open the 3D Holographic Workplace HUD, open:"
echo "    jarvis_workplace.html in your browser"
echo ""

read -p "Would you like to start Jarvis now? (y/n): " START_NOW
if [[ "$START_NOW" =~ ^[Yy]$ ]]; then
    python jarvis_voice.py
fi
