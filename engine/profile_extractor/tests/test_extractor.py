"""
Test script for the profile extractor module.
"""

import json
import os
from engine.profile_extractor.extractor import parse_profile


def print_section(data, section_name, indent=0):
    """Recursively print a section of the extracted data."""
    prefix = "  " * indent
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                print(f"{prefix}📁 {key}:")
                print_section(value, key, indent + 1)
            else:
                print(f"{prefix}  • {key}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                print(f"{prefix}  [{i+1}]")
                print_section(item, section_name, indent + 1)
            else:
                print(f"{prefix}  • {item}")
    else:
        print(f"{prefix}{data}")


def main():
    """Test profile extraction with actual test files."""
    
    print("=" * 70)
    print("Profile Extractor - Comprehensive Extraction Test")
    print("=" * 70)
    
    # Get the directory where this test file is located
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Test 1: Parse PDF Resume
    print("\n📄 Test 1: Parsing PDF Resume")
    print("-" * 70)
    
    try:
        resume_path = os.path.join(test_dir, "resume.pdf")
        with open(resume_path, 'rb') as f:
            file_bytes = f.read()
        result = parse_profile(file_bytes, "pdf")
        data = json.loads(result)
        
        # Save to JSON file
        output_path = os.path.join(test_dir, "output_resume.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print("\n✓ Extraction successful!")
        print(f"💾 Saved to: {output_path}")
        print(f"\n📊 Extracted {len(data)} top-level sections")
        print("\n🔍 Data Structure:")
        print_section(data, "root")
        
        print(f"\n\n📋 Full JSON Output:")
        print(result)
        
    except FileNotFoundError:
        print("⚠ resume.pdf not found in tests directory")
    except Exception as e:
        print(f"⚠ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Parse LinkedIn PDF
    print("\n\n" + "=" * 70)
    print("📄 Test 2: Parsing LinkedIn PDF Profile")
    print("-" * 70)
    
    try:
        linkedin_path = os.path.join(test_dir, "linkedin.pdf")
        with open(linkedin_path, 'rb') as f:
            file_bytes = f.read()
        result = parse_profile(file_bytes, "pdf")
        data = json.loads(result)
        
        # Save to JSON file
        output_path = os.path.join(test_dir, "output_linkedin.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print("\n✓ Extraction successful!")
        print(f"💾 Saved to: {output_path}")
        print(f"\n📊 Extracted {len(data)} top-level sections")
        print("\n🔍 Data Structure:")
        print_section(data, "root")
        
        print(f"\n\n📋 Full JSON Output:")
        print(result)
        
    except FileNotFoundError:
        print("⚠ linkedin.pdf not found in tests directory")
    except Exception as e:
        print(f"⚠ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Parse HTML Portfolio
    print("\n\n" + "=" * 70)
    print("🌐 Test 3: Parsing HTML Portfolio")
    print("-" * 70)
    
    try:
        html_path = os.path.join(test_dir, "index.html")
        with open(html_path, 'rb') as f:
            file_bytes = f.read()
        result = parse_profile(file_bytes, "html")
        data = json.loads(result)
        
        # Save to JSON file
        output_path = os.path.join(test_dir, "output_portfolio.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print("\n✓ Extraction successful!")
        print(f"💾 Saved to: {output_path}")
        print(f"\n📊 Extracted {len(data)} top-level sections")
        print("\n🔍 Data Structure:")
        print_section(data, "root")
        
        print(f"\n\n📋 Full JSON Output:")
        print(result)
        
    except FileNotFoundError:
        print("⚠ index.html not found in tests directory")
    except Exception as e:
        print(f"⚠ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✅ Test suite completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
