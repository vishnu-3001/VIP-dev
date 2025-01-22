def collaboration_prompt(log_entries:dict):
    prompt= """
    You are a team collaboration analyst. Using the log data below, evaluate team performance:
1. Assign a collaboration score (1-10) based on the criteria.
2. Provide key observations about team dynamics.
3. Recommend specific actions for improvement.

Log Data: {log_entries}

Scoring Criteria:
- Participation Balance: Are contributions evenly distributed?
- Consistency: Are contributions spread over time or clustered?
- Engagement: Do all members contribute actively?
- Collaboration Timing: Is the work synchronous or asynchronous?
- Workload Distribution: Are contributions proportionate?

Constraints:
- Only use the provided data for evaluation.
- Keep insights and suggestions concise and precise.
    """
    return prompt
def format_prompt(headings):
    prompt="""
    Evaluate the format of a research paper based on its headings and provide a score out of 5. Use these criteria:
    1. Coverage**: Do the headings include standard sections (Abstract, Introduction, Methodology, Results, Discussion, Conclusion, References)?
    2. Order**: Are the headings logically arranged?
    3. Clarity**: Are the headings clear and professional?
    4. Consistency**: Is the formatting uniform (e.g., capitalization, numbering)?

    {headings}

    Provide a score (1-5):
    - 5 = Excellent: Meets all criteria.
    - 4 = Good: Minor issues.
    - 3 = Average: Noticeable gaps.
    - 2 = Poor: Significant issues.
    - 1 = Very Poor: Fails most criteria.
    """
    return prompt
