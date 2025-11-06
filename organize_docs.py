"""
Documentation Organizer
Moves all .md files (except README.MD) to docs folder with priority numbers.
"""

import os
import shutil

# Define the documentation files and their priority order
docs_to_move = {
    "DATABASE_DOCUMENTATION_GUIDE.md": "02_DATABASE_DOCUMENTATION_GUIDE.md",
    "PRODUCTION_SECURITY.md": "03_PRODUCTION_SECURITY.md",
    "MULTILINGUAL_GUIDE.md": "04_MULTILINGUAL_GUIDE.md",
    "ANIME_ARABIC_EXAMPLES.md": "05_ANIME_ARABIC_EXAMPLES.md",
    "ERROR_HANDLING_GUIDE.md": "06_ERROR_HANDLING_GUIDE.md",
    "ARCHITECTURE.md": "07_ARCHITECTURE.md",
    "PROJECT_SUMMARY.md": "08_PROJECT_SUMMARY.md",
}

def main():
    print("📚 Organizing documentation files...")
    print()
    
    # Create docs folder if it doesn't exist
    if not os.path.exists("docs"):
        os.makedirs("docs")
        print("✅ Created docs/ folder")
    
    # Move each file
    moved_count = 0
    for old_name, new_name in docs_to_move.items():
        if os.path.exists(old_name):
            new_path = os.path.join("docs", new_name)
            shutil.move(old_name, new_path)
            print(f"✅ Moved {old_name} → {new_path}")
            moved_count += 1
        else:
            print(f"⚠️  {old_name} not found (may already be moved)")
    
    print()
    print(f"🎉 Done! Moved {moved_count} files to docs/ folder")
    print()
    print("📖 Documentation is now organized by priority:")
    print("   00_READ_ME_FIRST.md - Start here!")
    print("   01_QUICKSTART.md - Get running in 5 minutes")
    print("   02_DATABASE_DOCUMENTATION_GUIDE.md - Document your DB")
    print("   03_PRODUCTION_SECURITY.md - Security guide")
    print("   04_MULTILINGUAL_GUIDE.md - Language support")
    print("   05_ANIME_ARABIC_EXAMPLES.md - Anime examples")
    print("   06_ERROR_HANDLING_GUIDE.md - Error handling")
    print("   07_ARCHITECTURE.md - System architecture")
    print("   08_PROJECT_SUMMARY.md - Complete overview")
    print()
    print("✨ README.MD stays in the root folder")

if __name__ == "__main__":
    main()

