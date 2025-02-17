def collaboration_prompt(log_entries):
    prompt= """
   <System>
You are a collaboration analyst specializing in evaluating individual work patterns. Your goal is to assess how regularly a specific person updates their logs. You must base your analysis only on the provided data, using statistical inference if needed. Avoid assumptions, hallucinations, or fabricated insights.
</System>

<Task>
Evaluate the update consistency of the given individual based on the following criteria:
1. Assign a **consistency score (1-10)** based on update frequency and regularity.
2. Identify key patterns in their activity, such as streaks, gaps, or trends.
3. Use **statistical inference if necessary** to detect patterns in contributions.
4. Provide concise, data-driven insights on their update habits.

### **Scoring Criteria:**
- **Update Frequency:** How often does the person make updates?
- **Regularity:** Are updates consistent or irregular?
- **Trend Patterns:** Are updates increasing, decreasing, or sporadic?
- **Gaps & Streaks:** Are there long gaps between updates or continuous activity?
- **Time Distribution:** Are updates clustered within short time frames or evenly spread?

### **Constraints:**
- **Analyze only the given person’s log data**—do not compare with others.
- **Do not assume, fabricate, or infer beyond the provided data.**
- **Use clear, precise, and actionable insights.**
</Task>

<Data>
{log_entries}
</Data>

    """
    return prompt
def format_prompt(dates):
    prompt="""
    <System>
You are an expert in analyzing sequences and patterns in data. Your task is to assess the organization of a given array of dates and determine how well they follow a structured order.
</System>

<Task>
Evaluate the given array of dates based on the following criteria:
1. **Identify the predominant order**:
   - **Chronological (oldest to newest)**
   - **Reverse chronological (newest to oldest)**
   - **Segmented order (a structured transition between chronological and reverse chronological)**
   - **Disorganized (no clear pattern or structure)**

2. **Rate the organization of the sequence on a scale of 1 to 5**, based on its consistency and logical order:
   - **5/5** → Perfectly structured with no inconsistencies.
   - **4/5** → Mostly structured, with minor inconsistencies that don’t disrupt the overall pattern.
   - **3/5** → Noticeable deviations or partial structuring, but a general order exists.
   - **2/5** → Mostly disorganized with only small segments following a pattern.
   - **1/5** → Completely random or chaotic ordering with no discernible structure.

3. **Provide detailed feedback**, including:
   - The overall structure of the sequence.
   - Any sections where the pattern changes or is inconsistent.
   - Suggestions to improve the organization, if necessary.

</Task>

<Data>
Here is the array of dates:
{dates}
</Data>"""
    return prompt

def normalize_dates_prompt(dates):
    formatted_dates = "\n".join([f"- {date}" for date in dates])  
    prompt = f"""
        Normalize the following dates into ISO format (YYYY-MM-DD):
        {formatted_dates}
        
        Example Output:
        Input: 2nd March 2025 → Output: 2025-03-02
        Input: 04-05-25 → Output: 2025-05-04
        
        Provide ONLY an array of formatted dates without extra text.
    """
    return prompt.strip()  

        