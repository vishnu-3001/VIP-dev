def get_montly_prompt(data):
    prompt="""<system>
You are a seasoned time-series analyst with deep expertise in date-based and label-based trends. You excel at producing insightful, narrative reports that uncover patterns, anomalies, and category contributions over time.
</system>

<task>
You will be given a JSON object mapping dates (MM-YYYY) to counts per label. Your job is to generate a detailed report of 350–400 words, covering:

1. **Overall Usage**  
   – Which label appears most frequently across the entire period?  
   – Total counts per label.

2. **Trends Over Time**  
   – Rising or declining patterns for each label.  
   – Any seasonal or cyclical behaviors.

3. **Key Events**  
   – Months with notable spikes or dips, and possible interpretations.

4. **Label Contributions**  
   – Percentage share of each label per month and overall.

5. **Narrative Summary**  
   – A concise “story” of how label usage evolved, highlighting key takeaways.

Produce your output in JSON format exactly as follows:

```json
{{
  "report": "Your 350–400 word analysis here…"
}}
Here is the data:

{data}
</task>
    """
    return prompt

def get_yearly_prompt(data):
    prompt="""
<system>
You are a seasoned data analyst with expertise in time-series and categorical trend analysis. I’m going to provide you with a JSON object called `yearly_data` that maps each year to counts of various labels (e.g., “project-update”, “todo”, etc.).
</system>
<task>
Your task is to produce a detailed analysis covering:

1. **High-level summary**  
   - Total number of items per year  
   - Breakdown of each label’s contribution and percentage share  

2. **Year-over-year trends**  
   - Which labels increased or decreased most dramatically  
   - Overall growth or decline in total items  

3. **Dominant labels**  
   - Identify the top 1–2 labels each year and discuss their significance  

4. **Anomalies & outliers**  
   - Years with unexpected spikes or dips in any label, and possible reasons  

5. **Patterns & insights**  
   - Recurring behaviors or shifts in focus over the years  
   - Any correlation between labels (e.g., when “project-update” falls, does “todo” rise?)  

6. **Actionable recommendations**  
   - Based on these patterns, suggest strategies to balance workload or resource allocation  
   - Highlight any labels that may warrant further investigation  

Produce your output in JSON format exactly as follows:
give me only text with only report as output no other text
{{
  "report": "Your 350–400 word analysis here…"
}}
Here is the data:
{data}
</task>
"""
    return prompt

def get_semester_prompt(data):
    prompt="""
<system>
You are a seasoned data analyst specializing in periodic and categorical trend analysis. I will provide you with a JSON object called `semester_data` that maps each academic semester (e.g., “Spring 24”, “Fall 24”, “Spring 25”) to counts of various labels (e.g., “project-update”, “todo”, etc.).
</system>
<task>
Your task is to generate a comprehensive report covering:

1. **Overview per Semester**  
   - Total item count for each semester  
   - Breakdown of each label’s absolute count and percentage share  

2. **Semester-over-Semester Trends**  
   - Which labels rose or fell most significantly between consecutive semesters  
   - Overall upticks or downturns in total engagement  

3. **Key Labels**  
   - Identify the top 1–2 labels each semester and discuss what they reveal about focus areas  

4. **Anomalies & Outliers**  
   - Semesters with unexpected spikes or dips in any label, along with possible explanations  

5. **Longitudinal Patterns & Correlations**  
   - Recurring shifts in label prominence across multiple semesters  
   - Any inverse or direct correlations between labels (e.g., does a drop in “project-update” coincide with a rise in “todo”?)  

6. **Strategic Recommendations**  
   - Suggestions for balancing efforts or reallocating resources based on observed trends  
   - Labels or semesters that warrant deeper investigation or follow-up  

Produce your output in JSON format exactly as follows:
give me only text with only report as output no other text
{{
  "report": "Your 350–400 word analysis here…"
}}
Here is the data:
{data}
</task>
"""
    return prompt
def get_quarterly_prompt(data):
    prompt="""
<system>
You are a seasoned data analyst specializing in periodic and categorical trend analysis. I will provide you with a JSON object called `quarterly_data` that maps each quarter (e.g., “Spring 24”, “Summer 24”, “Fall 24”, “Winter 25”) to counts of various labels (e.g., “project-update”, “todo”, etc.).
</system>
<task>
Your task is to generate a comprehensive report covering:

1. **Overview per Quarter**  
   - Total item count for each quarter  
   - Breakdown of each label’s absolute count and percentage share  

2. **Quarter-over-Quarter Trends**  
   - Which labels increased or decreased most significantly between consecutive quarters  
   - Overall upticks or downturns in total engagement  

3. **Key Labels**  
   - Identify the top 1–2 labels each quarter and discuss what they reveal about focus areas  

4. **Anomalies & Outliers**  
   - Quarters with unexpected spikes or dips in any label, along with possible explanations  

5. **Longitudinal Patterns & Correlations**  
   - Recurring shifts in label prominence across multiple quarters  
   - Any inverse or direct correlations between labels (e.g., does a drop in “project-update” coincide with a rise in “todo”?)  

6. **Strategic Recommendations**  
   - Suggestions for balancing efforts or reallocating resources based on observed trends  
   - Labels or quarters that warrant deeper investigation or follow-up  

Produce your output in JSON format exactly as follows:
give me only text with only report as output no other text
{{
  "report": "Your 350–400 word analysis here…"
}}
Here is the data:
{data}
</task>
"""

def get_component_prompt(data):
    prompt="""
<system>
You are a seasoned data analyst specializing in categorical composition analysis. I will provide you with a JSON object called `component_data` that maps each component label (e.g., “project-update”, “todo”, etc.) to its total count.
</system>
<task>
Your task is to generate a comprehensive report covering:

1. **Component Overview**  
   - Total count for each component  
   - Percentage share of each component relative to the overall total  

2. **Dominant vs. Underrepresented Components**  
   - Identify the most and least prevalent components  
   - Discuss what high or low counts imply about our focus and priorities  

3. **Composition Balance Analysis**  
   - Assess whether the distribution is balanced or skewed  
   - Highlight any components that disproportionately affect the overall composition  

4. **Insights & Interpretations**  
   - Interpret what the component distribution reveals about workflow patterns  
   - Correlate heavy usage of certain components with potential process bottlenecks or focus areas  

5. **Actionable Recommendations**  
   - Suggest strategies to address over- or under-emphasis on specific components  
   - Recommend components to monitor more closely or investigate further  

Produce your output in JSON format exactly as follows:
give me only text with only report as output no other text
{{
  "report": "Your 350–400 word analysis here…"
}}
Here is the data:
{data}
</task>
"""
    return prompt