"""Setup script for the document parser and RAG pipeline."""

import os
import subprocess
import sys
from pathlib import Path


def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_environment():
    """Set up environment file."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from template...")
        env_file.write_text(env_example.read_text())
        print("✅ .env file created. Please add your OpenAI API key.")
    elif env_file.exists():
        print("✅ .env file already exists.")
    else:
        print("⚠️ No .env.example found. Creating basic .env file...")
        env_file.write_text("OPENAI_API_KEY=your_openai_api_key_here\n")
        print("✅ Basic .env file created. Please add your OpenAI API key.")


def create_data_directory():
    """Create data directory for LanceDB."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print("✅ Data directory created.")


def main():
    """Main setup function."""
    print("🚀 Setting up Document Parser and RAG Pipeline...")
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Setup environment
    setup_environment()
    
    # Create data directory
    create_data_directory()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Add your OpenAI API key to the .env file")
    print("2. Run the application: streamlit run app.py")
    print("3. Or test the pipeline: python example_usage.py")
    
    return True


if __name__ == "__main__":
    main()
