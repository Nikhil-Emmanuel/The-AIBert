#!/usr/bin/env python3
"""
Setup script for The AIBert - AI-Assisted Grading System
Automates the installation and configuration process
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("🤖 The AIBert - AI-Assisted Grading System Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_node_version():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js version: {version}")
            return True
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Python dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        return False
    return True

def install_node_dependencies():
    """Install Node.js dependencies"""
    print("\n📦 Installing Node.js dependencies...")
    try:
        subprocess.run(['npm', 'install'], check=True)
        print("✅ Node.js dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Node.js dependencies")
        return False
    return True

def create_env_file():
    """Create .env file with template"""
    env_path = Path('.env')
    env_example_path = Path('.env.example')
    
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    env_template = """# Google OAuth & API Configuration
VITE_GOOGLE_CLIENT_ID=your_google_oauth_client_id
VITE_GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
VITE_GEMINI_API_KEY=your_gemini_api_key
VITE_GOOGLE_CLASSROOM_API_KEY=your_google_api_key

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/aibert

# AI Backend Configuration
AI_BACKEND_PORT=5000
FLASK_DEBUG=False

# Model Configuration (Optional)
CUDA_VISIBLE_DEVICES=0
MODEL_CACHE_DIR=./models
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_template)
        print("✅ Created .env file with template")
        print("⚠️  Please edit .env file with your actual API keys")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_mongodb():
    """Check if MongoDB is available"""
    try:
        import pymongo
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✅ MongoDB connection successful")
        return True
    except Exception:
        print("⚠️  MongoDB not available - you can use MongoDB Atlas instead")
        return False

def download_models():
    """Download required AI models"""
    print("\n🤖 Downloading AI models (this may take a while)...")
    
    download_script = """
try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    from sentence_transformers import SentenceTransformer
    
    print("Downloading TrOCR model for handwriting recognition...")
    TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
    VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten')
    
    print("Downloading sentence transformer for semantic analysis...")
    SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    print("✅ Models downloaded successfully")
except Exception as e:
    print(f"⚠️  Model download failed: {e}")
    print("Models will be downloaded automatically on first use")
"""
    
    try:
        subprocess.run([sys.executable, '-c', download_script], check=True)
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Model download failed - models will download on first use")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        'ai_backend/models',
        'ai_backend/logs',
        'ai_backend/data',
        'uploads'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created necessary directories")

def run_tests():
    """Run basic tests to verify installation"""
    print("\n🧪 Running basic tests...")
    try:
        subprocess.run([sys.executable, 'test_grading_system.py'], 
                      check=True, capture_output=True)
        print("✅ Basic tests passed")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Some tests failed - this is normal if models aren't downloaded yet")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Edit the .env file with your actual API keys")
    print("2. Start MongoDB (if using local installation)")
    print("3. Start the AI backend:")
    print("   cd ai_backend")
    print("   python app.py")
    print("4. Start the frontend (in another terminal):")
    print("   npm run dev")
    print("5. Open http://localhost:5173 in your browser")
    print()
    print("For the AI Grading System:")
    print("- Visit http://localhost:5173/grading.html")
    print("- API documentation: http://localhost:5000/status")
    print()
    print("Need help? Check the README.md or create an issue on GitHub")
    print()

def main():
    """Main setup function"""
    print_banner()
    
    # Check prerequisites
    check_python_version()
    node_available = check_node_version()
    
    if not node_available:
        print("\n❌ Node.js is required. Please install Node.js 14+ and run setup again.")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_python_dependencies():
        print("\n❌ Setup failed during Python dependency installation")
        sys.exit(1)
    
    if not install_node_dependencies():
        print("\n❌ Setup failed during Node.js dependency installation")
        sys.exit(1)
    
    # Create configuration
    create_env_file()
    
    # Check database
    check_mongodb()
    
    # Download models (optional)
    user_input = input("\nDownload AI models now? (y/N): ").lower().strip()
    if user_input in ['y', 'yes']:
        download_models()
    else:
        print("⚠️  Models will be downloaded automatically on first use")
    
    # Run tests (optional)
    user_input = input("\nRun basic tests? (y/N): ").lower().strip()
    if user_input in ['y', 'yes']:
        run_tests()
    
    # Print completion message
    print_next_steps()

if __name__ == '__main__':
    main()
