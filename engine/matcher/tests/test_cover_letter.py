"""
Test Cover Letter Generator
Uses actual parsed profile and job JSON files
"""

import json
import os
from engine.matcher import generate_cover_letter


def load_test_data():
    """Load actual test JSON files."""
    test_dir = os.path.dirname(__file__)
    data = {}
    
    files = {
        'resume': 'output_resume.json',
        'linkedin': 'output_linkedin.json',
        'portfolio': 'output_portfolio.json',
        'job_posting': 'posting_test.json'
    }
    
    for key, filename in files.items():
        path = os.path.join(test_dir, filename)
        if os.path.exists(path):
            with open(path, 'r') as f:
                data[key] = json.load(f)
            print(f"✓ Loaded {filename}")
    
    return data


def test_cover_letter():
    """Test cover letter generation with actual data."""
    print(f"\n{'='*70}")
    print("Testing Cover Letter Generator")
    print(f"{'='*70}\n")
    
    # Load actual test data
    data = load_test_data()
    
    if 'job_posting' not in data:
        print("⚠ No job posting data found")
        return None
    
    job_data = data['job_posting']
    
    # Test professional style
    print(f"\n📝 Generating PROFESSIONAL cover letter...")
    
    result = generate_cover_letter(
        job_data,
        resume=data.get('resume'),
        linkedin=data.get('linkedin'),
        portfolio=data.get('portfolio'),
        style="professional"
    )
    
    if 'error' in result:
        print(f"⚠ Error: {result['error']}")
        return result
    
    # Print cover letter
    print(f"\n{'='*70}")
    print("GENERATED COVER LETTER")
    print(f"{'='*70}\n")
    
    print(result.get('letter', ''))
    
    print(f"\n{'='*70}")
    print(f"📊 Word Count: {result.get('word_count', 0)}")
    
    key_points = result.get('key_points_highlighted', [])
    if key_points:
        print(f"\n✨ Key Points Highlighted:")
        for point in key_points:
            print(f"  • {point}")
    
    gaps_addressed = result.get('gaps_addressed', [])
    if gaps_addressed:
        print(f"\n🔧 Gaps Addressed:")
        for gap in gaps_addressed:
            print(f"  • {gap}")
    
    # Save result
    output_path = os.path.join(os.path.dirname(__file__), 'cover_letter_result.json')
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    # Also save just the letter as text
    letter_path = os.path.join(os.path.dirname(__file__), 'cover_letter.txt')
    with open(letter_path, 'w') as f:
        f.write(result.get('letter', ''))
    
    print(f"\n💾 Saved to: cover_letter_result.json, cover_letter.txt")
    print(f"\n{'='*70}\n")
    
    return result


if __name__ == "__main__":
    test_cover_letter()
