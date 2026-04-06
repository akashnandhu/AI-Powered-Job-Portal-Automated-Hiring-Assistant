import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from ranking.shortlisting_engine import ShortlistingEngine

def main():
    print("=" * 50)
    print("FINAL Candidate Ranking & Shortlisting System")
    print("=" * 50)
    
    engine = ShortlistingEngine()
    
    print("1. Loading ATS scores...")
    if not engine.load_scores():
        return
        
    print("2. Applying ranking and shortlisting logic...")
    engine.process_and_rank()
    
    print("3. Generating structured and recruiter-friendly outputs...")
    f1 = engine.generate_final_shortlisting_json()
    f2 = engine.generate_top_5_matches_json()
    f3 = engine.generate_recruiter_report()
    
    print(f"   - Saved: {f1}")
    print(f"   - Saved: {f2}")
    print(f"   - Saved: {f3}")
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    sum_data = engine.summary
    print(f"Total Roles: {sum_data['total_jobs']}")
    print(f"Priority: {sum_data['priority']}")
    print(f"Shortlisted: {sum_data['shortlisted']}")
    print(f"Review: {sum_data['review']}")
    print(f"Rejected: {sum_data['rejected']}")
    print("==================================================")

if __name__ == "__main__":
    main()
