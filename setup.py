#!/usr/bin/env python3
"""
Setup script for DreamJobX
"""

import os
import subprocess
import sys

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    success, output = run_command("pip install -r requirements.txt")
    if success:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print("❌ Error installing dependencies:")
        print(output)
        return False

def setup_env_file():
    """Set up the environment file"""
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return True
    
    if os.path.exists("env_example.txt"):
        success, output = run_command("cp env_example.txt .env")
        if success:
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file and add your OpenAI API key")
            return True
        else:
            print("❌ Error creating .env file:")
            print(output)
            return False
    else:
        print("❌ env_example.txt not found")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up DreamJobX...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment file
    if not setup_env_file():
        sys.exit(1)
    
    print("=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: streamlit run app.py")
    print("3. Open your browser to http://localhost:8501")
    print("\n🎉 Happy job hunting!")

if __name__ == "__main__":
    main() 