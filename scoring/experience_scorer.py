from typing import List, Dict, Any
from utils.experience_utils import calculate_duration_months, clean_job_title
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ExperienceScorer:
    """
    Calculates total experience, detects gaps and overlaps,
    and analyzes relevance of roles to job requirements.
    """
    
    def analyze_timeline(self, experiences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates total exp, gaps, and overlaps."""
        valid_exps = [e for e in experiences if e.get('parsed_start') and e.get('parsed_end')]
        
        if not valid_exps:
            return {
                "total_calc_months": 0, 
                "total_span_months": 0,
                "gaps_months": 0, 
                "overlaps_months": 0, 
                "gaps": [], 
                "overlaps": []
            }
            
        # Sort by start date
        valid_exps.sort(key=lambda x: x['parsed_start'])
        
        total_months = 0
        gaps_months = 0
        overlaps_months = 0
        gaps_list = []
        overlaps_list = []
        
        # To avoid double-counting overlapping durations, compute total timeline span
        min_start = min(e['parsed_start'] for e in valid_exps)
        max_end = max(e['parsed_end'] for e in valid_exps)
        
        total_months = calculate_duration_months(min_start, max_end)
        
        for i in range(len(valid_exps) - 1):
            curr = valid_exps[i]
            nxt = valid_exps[i+1]
            
            delta_gap = (nxt['parsed_start'] - curr['parsed_end']).days
            
            if delta_gap > 30: # > 1 month gap buffer
                gap_m = calculate_duration_months(curr['parsed_end'], nxt['parsed_start'])
                gaps_months += gap_m
                gaps_list.append({
                    "from": curr['parsed_end'].strftime("%Y-%m-%d"),
                    "to": nxt['parsed_start'].strftime("%Y-%m-%d"),
                    "duration_months": gap_m
                })
            
            # Check overlap
            if curr['parsed_end'] > nxt['parsed_start']:
                overlap_end = min(curr['parsed_end'], nxt['parsed_end'])
                overlap_m = calculate_duration_months(nxt['parsed_start'], overlap_end)
                if overlap_m > 0:
                    overlaps_months += overlap_m
                    overlaps_list.append({
                        "role1": curr.get('job_title', 'Unknown'),
                        "role2": nxt.get('job_title', 'Unknown'),
                        "duration_months": overlap_m
                    })
                    
        return {
            "total_calc_months": max(0, total_months - gaps_months), # Adjust total actual working months
            "total_span_months": total_months,
            "gaps_months": gaps_months,
            "overlaps_months": overlaps_months,
            "gaps": gaps_list,
            "overlaps": overlaps_list
        }

    def compute_role_relevance(self, candidate_roles: List[str], target_role: str) -> List[Dict[str, Any]]:
        """
        Uses TF-IDF and Cosine Similarity to compute relevance between a candidate's
        historical roles and the target job description's title / core requirement.
        """
        if not candidate_roles or not target_role:
            return [{"role": r, "relevance_score": 0.0} for r in candidate_roles]
            
        clean_target = clean_job_title(target_role)
        clean_candidates = [clean_job_title(r) for r in candidate_roles]
        
        corpus = [clean_target] + clean_candidates
        
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(corpus)
            
            # Target is at index 0
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            
            results = []
            for i, role in enumerate(candidate_roles):
                results.append({
                    "role": role,
                    "relevance_score": round(float(cosine_sim[i]), 2)
                })
            return results
        except Exception:
             # Fallback if vocabulary is empty
             return [{"role": r, "relevance_score": 0.0} for r in candidate_roles]

    def score_experience(self, experiences: List[Dict[str, Any]], target_role: str, target_required_months: int = 0) -> Dict[str, Any]:
        """
        Generates the final structured experience object containing parses and relevance scoring.
        """
        timeline_analysis = self.analyze_timeline(experiences)
        
        candidate_titles = [e.get('job_title', '') for e in experiences if e.get('job_title')]
        relevance_analysis = self.compute_role_relevance(candidate_titles, target_role)
        
        # Aggregate Relevance
        avg_relevance = 0
        if relevance_analysis:
            avg_relevance = sum(r['relevance_score'] for r in relevance_analysis) / len(relevance_analysis)
            
        # Is experienced enough?
        is_experienced = timeline_analysis['total_calc_months'] >= target_required_months
        
        return {
            "parsed_experiences": [
                {
                    "company": e.get('company'),
                    "job_title": e.get('job_title'),
                    "start_date": e.get('start_date_str'),
                    "end_date": e.get('end_date_str'),
                    "duration_months": calculate_duration_months(e.get('parsed_start'), e.get('parsed_end'))
                }
                for e in experiences
            ],
            "timeline": timeline_analysis,
            "role_relevance": relevance_analysis,
            "overall_relevance_score": round(avg_relevance, 2),
            "meets_experience_requirement": is_experienced
        }
