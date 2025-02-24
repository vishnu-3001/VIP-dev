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
Evaluate the dates in given array of dates based on the following criteria:
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


def references_prompt(citations,references):
    apa_citations = ", ".join(citations.get("APA", [])) or "No APA citations found"
    mla_citations = ", ".join(citations.get("MLA", [])) or "No MLA citations found"
    numeric_citations = ", ".join(citations.get("Numeric", [])) or "No Numeric citations found"

    prompt = f"""
    <system>
    You are an expert in academic writing and citation verification.
    Your task is to analyze citations extracted from a document and compare them with the provided References section.
    
    **Steps to follow:**
    1. Identify **citations in the main text** that do not have a corresponding entry in the References section.
    2. Identify **references in the References section** that were never cited in the main text.
    3. Provide a **rating out of 5** based on how well the citations and references match:
       - **5/5** = All citations are properly referenced, and there are no extra references.
       - **4/5** = Minor missing citations or extra references.
       - **3/5** = Some missing citations or extra references (moderate issue).
       - **2/5** = Several missing citations or many unused references (significant issue).
       - **1/5** = Most citations are missing or references are mostly incorrect.
    4. Give **constructive feedback** on how to improve citation accuracy.
    
      "rating": "Final rating out of 5",
      "feedback": "Brief feedback on how to improve citations"

    </system>

<data>
    **Citations Extracted from the Main Text**:
    APA Citations: {apa_citations}
    MLA Citations: {mla_citations}
    Numeric Citations: {numeric_citations}

    **References Extracted from the References Section**:
    {references}
    </data>
    """
    return prompt

        