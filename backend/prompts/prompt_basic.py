from typing import List

def build_batch_prompt(job_description: str, resume_list: List[dict]) -> str:
    prompt = f"""You are an advanced Applicant Tracking System (ATS).

Below is a Job Description:

{job_description}

Below are multiple resumes if same resume duplicated or copy again and again remove it keep once . Each resume is clearly marked between \"### Resume Start: <filename> ###\" and \"### Resume End ###\".

Tasks
1. Extract:
   • name
   • degree
   • experience_year
   • experience_details (list)
   • location (take personal address from resume only)
2. Extract all skills from JD, match against resume, score each (0‑100) and  Do not assume or infer skills from degree only based on what they are have.
3. Set JDMatch = mean(skill scores).
4. Return ONLY valid JSON.
example : For each resume, analyze and respond with a list of JSON objects with the following fields:
[
    {{
        "filename": "resume_1.pdf",
        "name": "",
        "degree": "",
        "experience_year": 0,
        "experience_details": [],
        "JDMatch": "75%",
        "overall_score": "80%",
        "location": "",
        "MatchingKeywords": {{
            "Python": "85%",
            "SQL": "60%"
        }}
    }}
]

Only return a valid JSON list. Here's the resumes:
"""
    for r in resume_list:
        prompt += f"\n### Resume Start: {r['filename']} ###\n{r['text']}\n### Resume End ###\n"
    return prompt