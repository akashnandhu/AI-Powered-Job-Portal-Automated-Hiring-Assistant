import json
import os

def load_results(filepath="outputs/ranked_jobs.json"):
    """Loads ranked jobs data from JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                print("Error: JSON data is not a list.")
                return []
            return data
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: File '{filepath}' contains invalid JSON.")
        return []
    except Exception as e:
        print(f"Error loading results: {e}")
        return []

def evaluate_accuracy(results, expected_jobs):
    """Computes Top-K accuracy and other metrics based on ranked results."""
    if not results:
        print("No results to evaluate.")
        return None

    # Retrieve job titles for Top-K checking
    top_1_job = results[0].get("job_title", "") if len(results) >= 1 else ""
    top_3_jobs = [r.get("job_title", "") for r in results[:3]]
    top_5_jobs = [r.get("job_title", "") for r in results[:5]]

    # 1 if any expected job is found within the Top K, else 0
    top_1_accuracy = 1 if top_1_job in expected_jobs else 0
    top_3_accuracy = 1 if any(job in expected_jobs for job in top_3_jobs) else 0
    top_5_accuracy = 1 if any(job in expected_jobs for job in top_5_jobs) else 0

    total_score = 0
    match_distribution = {
        "Strong": 0,
        "Moderate": 0,
        "Weak": 0
    }
    
    section_totals = {
        "skills": 0,
        "experience": 0,
        "projects": 0,
        "education": 0
    }
    
    valid_section_counts = {
        "skills": 0,
        "experience": 0,
        "projects": 0,
        "education": 0
    }

    num_results = len(results)

    for result in results:
        # Avoid missing or corrupted scores
        score = result.get("score")
        if score is None:
            score = 0
        total_score += score
        
        # Match distribution
        # Handle cases where match_level might be "Strong Match", "Moderate Match", etc.
        match_level = result.get("match_level", "Weak Match")
        if "Strong" in match_level:
            match_distribution["Strong"] += 1
        elif "Moderate" in match_level:
            match_distribution["Moderate"] += 1
        else:
            match_distribution["Weak"] += 1

        # Section averages
        section_scores = result.get("section_scores", {})
        for section in section_totals.keys():
            sec_score = section_scores.get(section)
            if sec_score is not None:
                section_totals[section] += sec_score
                valid_section_counts[section] += 1

    # Calculate averages
    average_similarity_score = total_score / num_results if num_results > 0 else 0

    section_average_scores = {}
    for section in section_totals.keys():
        if valid_section_counts[section] > 0:
            section_average_scores[section] = section_totals[section] / valid_section_counts[section]
        else:
            section_average_scores[section] = 0

    report = {
        "top_1_accuracy": top_1_accuracy,
        "top_3_accuracy": top_3_accuracy,
        "top_5_accuracy": top_5_accuracy,
        "average_similarity_score": round(average_similarity_score, 4),
        "match_distribution": match_distribution,
        "section_average_scores": {k: round(v, 4) for k, v in section_average_scores.items()}
    }

    return report

def save_report(report, filepath="outputs/accuracy_report.json"):
    """Saves the evaluation report to a JSON file."""
    try:
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)
        print(f"Report saved successfully to '{filepath}'")
    except Exception as e:
        print(f"Error saving report: {e}")

def main():
    results_path = "outputs/ranked_jobs.json"
    report_path = "outputs/accuracy_report.json"
    
    # Expected jobs that are a good match for the input resume. 
    # Defined manually as per requirement.
    expected_jobs = [
        "Clinical Pharmacist",
        "Hospital Pharmacist",
        "Pharmacy Informatics Specialist"
    ]
    
    print("\n--- Semantic Matching Engine Evaluation ---")
    results = load_results(results_path)
    if not results:
        return
    
    report = evaluate_accuracy(results, expected_jobs)
    if not report:
        return

    save_report(report, report_path)

    # Print summary to the terminal
    print("\n[ Summary Report ]")
    print(f"Total Jobs Evaluated : {len(results)}")
    print(f"Avg Similarity Score : {report['average_similarity_score']:.4f}")
    
    print("\n[ Match Distribution ]")
    for level, count in report['match_distribution'].items():
        print(f"  {level}: {count}")
    
    print("\n[ Top-K Accuracies ]")
    print(f"  Top-1 Accuracy : {report['top_1_accuracy']}")
    print(f"  Top-3 Accuracy : {report['top_3_accuracy']}")
    print(f"  Top-5 Accuracy : {report['top_5_accuracy']}")

    print("\n[ Section-wise Averages ]")
    for section, avg in report['section_average_scores'].items():
        print(f"  {section.capitalize():<10}: {avg:.4f}")
    print("-------------------------------------------\n")

if __name__ == "__main__":
    main()
