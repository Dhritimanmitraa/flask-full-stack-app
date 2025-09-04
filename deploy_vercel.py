#!/usr/bin/env python3
"""
Vercel Deployment Helper Script
This script helps prepare and deploy your Flask app to Vercel
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def check_vercel_cli():
    """Check if Vercel CLI is installed"""
    try:
        subprocess.run(["vercel", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    print("🚀 Vercel Deployment Helper")
    print("=" * 50)
    
    # Check if Vercel CLI is installed
    if not check_vercel_cli():
        print("❌ Vercel CLI is not installed")
        print("📦 Please install it with: npm install -g vercel")
        print("🔗 Or visit: https://vercel.com/cli")
        sys.exit(1)
    
    print("✅ Vercel CLI is installed")
    
    # Check if user is logged in
    try:
        subprocess.run(["vercel", "whoami"], check=True, capture_output=True)
        print("✅ You are logged in to Vercel")
    except subprocess.CalledProcessError:
        print("🔐 Please log in to Vercel first:")
        print("   vercel login")
        sys.exit(1)
    
    # Check for required files
    required_files = ["vercel.json", "api/index.py", "requirements.txt"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        sys.exit(1)
    
    print("✅ All required files are present")
    
    # Prompt for environment variables
    print("\n🔧 Environment Variables Setup")
    print("You need to set up the following environment variables:")
    print("1. SECRET_KEY - Flask secret key")
    print("2. DATABASE_URL - PostgreSQL connection string")
    
    setup_env = input("\nDo you want to set up environment variables now? (y/N): ").lower().strip()
    
    if setup_env == 'y':
        print("\n📝 Setting up environment variables...")
        print("💡 Tip: You can generate a secret key at https://randomkeygen.com/")
        
        if not run_command("vercel env add SECRET_KEY", "Adding SECRET_KEY"):
            sys.exit(1)
            
        if not run_command("vercel env add DATABASE_URL", "Adding DATABASE_URL"):
            sys.exit(1)
    
    # Deploy
    print("\n🚀 Deploying to Vercel...")
    deploy_choice = input("Deploy to production? (y/N): ").lower().strip()
    
    if deploy_choice == 'y':
        if run_command("vercel --prod", "Deploying to production"):
            print("\n🎉 Deployment completed successfully!")
            print("🌐 Your app should be available at the URL shown above")
        else:
            print("\n❌ Deployment failed")
            sys.exit(1)
    else:
        print("\n📋 To deploy later, run: vercel --prod")
    
    print("\n📚 For more information, check VERCEL_DEPLOYMENT.md")

if __name__ == "__main__":
    main()
