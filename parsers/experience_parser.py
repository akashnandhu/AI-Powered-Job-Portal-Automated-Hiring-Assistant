import re
from typing import List, Dict, Any
from utils.experience_utils import parse_date

class ExperienceParser:
    """
    Parses unstructured text representing an experience section into structured objects.
    Extracts: Company names, Job titles, Employment durations.
    """
    
    def __init__(self):
        # Common patterns for dates in resumes:
        # Month YYYY - Month YYYY
        # MM/YYYY - MM/YYYY
        # YYYY - YYYY
        # ... - Present
        # Enhanced pattern to catch various date formats and handling 'Ongoing' or missing end dates
        self.date_range_pattern = re.compile(
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{1,2}/\d{4}|\d{4})\s*(?:-|to|–|—|until|till)\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{1,2}/\d{4}|\d{4}|Present|Current|Now|Till Date|To Date|Ongoing)?',
            re.IGNORECASE
        )
        
        self.job_title_keywords = ['Engineer', 'Developer', 'Manager', 'Analyst', 'Consultant', 'Director', 'Specialist', 'Lead', 'Architect', 'Data', 'Scientist', 'Researcher', 'Assistant', 'Intern', 'Officer', 'Executive', 'Administrator']
        
    def parse(self, text: str) -> List[Dict[str, Any]]:
        """
        Parses the experience text into a list of structured experience objects.
        Warning: This uses a heuristic approach. For highly irregular texts, NLP might be needed.
        """
        if not text:
            return []
            
        # Find all date matches and their spans
        matches = list(self.date_range_pattern.finditer(text))
        if not matches:
            return []
            
        experiences = []
        
        for i, match in enumerate(matches):
            exp = {}
            start_str = match.group(1)
            end_str = match.group(2) if match.group(2) else "Present"
            
            exp['start_date_str'] = start_str
            exp['end_date_str'] = end_str
            exp['parsed_start'] = parse_date(start_str)
            exp['parsed_end'] = parse_date(end_str)
            
            # Text before this date match
            start_search_idx = 0 if i == 0 else matches[i-1].end()
            pre_text = text[start_search_idx:match.start()].strip()
            
            # Handle inline title/company on the same line as the date
            inline_pre = text[:match.start()].split('\n')[-1].strip()
            if len(inline_pre) > 5 and start_search_idx < text.rfind('\n', 0, match.start()):
                 # There's a decent amount of text on the same line before the date
                 pass # We rely on lines logic below

            if i > 0:
                lines = [l.strip() for l in pre_text.split('\n') if l.strip()]
                
                # Assume last 1 or 2 lines before date is title/company of current job
                title_comp_lines = []
                idx = len(lines) - 1
                while idx >= 0 and len(title_comp_lines) < 2:
                    words = lines[idx].split()
                    # Sentences usually end with a period or are long. Job titles/companies usually don't and are short.
                    if len(words) < 15 and not lines[idx].endswith('.'):
                        title_comp_lines.insert(0, lines[idx])
                        idx -= 1
                    else:
                        break
                        
                desc_lines = lines[:idx+1]
                experiences[-1]['description'] = "  ".join(desc_lines)
                self._extract_title_company(" | ".join(title_comp_lines), exp)
            else:
                # First experience block
                self._extract_title_company(pre_text.replace('\n', ' | '), exp)
                
            experiences.append(exp)
            
        # Final job description is anything after the last match
        if experiences:
            last_match = matches[-1]
            experiences[-1]['description'] = text[last_match.end():].strip().replace('\n', '  ')
            
        for exp_dict in experiences:
            self._finalize_experience(exp_dict)
            
        return experiences
        
    def _extract_title_company(self, text: str, exp_dict: Dict[str, Any]):
        """Heuristic to separate job title from company name."""
        text = text.strip(" |,-:")
        if not text:
            return
            
        # Often separated by comma, hypen, or 'at'
        parts = re.split(r'\s+at\s+|[,|–—-]', text, maxsplit=1)
        if len(parts) == 2:
            part1, part2 = parts[0].strip(), parts[1].strip()
            # If part1 has title keywords, assume it's title, part2 is company
            if any(kw.lower() in part1.lower() for kw in self.job_title_keywords):
                exp_dict['job_title'] = part1
                exp_dict['company'] = part2
            else:
                # Default guess: Company - Title
                exp_dict['company'] = part1
                exp_dict['job_title'] = part2
        else:
             # Just one part, guess based on keywords
             if any(kw.lower() in text.lower() for kw in self.job_title_keywords):
                 exp_dict['job_title'] = text
                 exp_dict['company'] = "Unknown Company"
             else:
                 exp_dict['company'] = text
                 exp_dict['job_title'] = "Unknown Title"

    def _finalize_experience(self, exp_dict: Dict[str, Any]):
        if 'description' in exp_dict and isinstance(exp_dict['description'], list):
            exp_dict['description'] = " ".join(exp_dict['description'])
        
        # Ensure fields exist
        exp_dict.setdefault('company', 'Unknown')
        exp_dict.setdefault('job_title', 'Unknown')
