import os
import fitz
import asyncio
import json
from utils import *;

llm = model()
emodel = embeddings_model()

headings_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "utils", "headings.json"))
PDF_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "utils", "download_file.pdf"))
index=get_index()

# date_pattern = re.compile(
#     r'\b('
#     r'\d{2}/\d{2}/\d{4}|'               
#     r'\d{2}/\d{2}/\d{2}|'                
#     r'\d{2}-\d{2}-\d{2}|'               
#     r'\d{2}-\d{2}-\d{4}|'               
#     r'\d{2}\.\d{2}\.\d{2}|'               
#     r'\d{2}\.\d{2}\.\d{4}|'               
#     r'\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4}|'  
#     r'\w+\s+\d{1,2},\s+\d{4}|'            
#     r'\d{1,2}-\w+-\d{4}|'                 
#     r'\w+\s+\d{1,2}(?:st|nd|rd),\s+\d{4}|' 
#     r'\w+\s+\d{1,2}(?:st|nd|rd)?\s+\d{4}|' 
#     r'\b\w+\s+\d{1,2}(?:st|nd|rd|th),\s+\d{4}\b'  
#     r')\b'
# )

# async def extract_text_by_date(pdf_path):
#     doc = fitz.open(pdf_path)
#     extracted_text = ""
#     for page in doc:
#         extracted_text += page.get_text("text") + "\n"
#     dates = date_pattern.findall(extracted_text)
#     normalized_dates = await normalize_dates(dates)
#     try:
#         with open(dates_json_path, "w") as json_file:
#             json.dump(normalized_dates, json_file, indent=4)
#     except Exception as e:
#         print(f"Error while saving dates to JSON file: {e}")
    
#     return normalized_dates

# async def normalize_dates(dates):
#     prompt_template = normalize_dates_prompt(dates)
#     prompt = PromptTemplate(input_variables=["dates"], template=prompt_template)
#     chain = prompt | llm
#     response = await asyncio.to_thread(chain.invoke, {'dates': dates})  
#     date_string = response.content.strip("[]").replace("'", "").split(", ")
#     return date_string

# async def extract():
#     try:
#         date_content = await extract_text_by_date(PDF_PATH)
#         return {"message": "Dates extracted and stored successfully.", "data": date_content}
#     except Exception as e:
#         raise Exception(f"Date extraction failed: {e}")
def extract_text_by_headings(pdf_path):
    doc = fitz.open(pdf_path)
    sections = {}  
    
    headings = extract_headings(doc)
    try:
        with open(headings_json_path,'w') as json_file:
            json.dump(headings,json_file,indent=2)
    except Exception as e:
        print(f"Error occured while saving heaidngs to headings json file : {e}")
    extracted_text = {page.number: page.get_text("text") for page in doc}  # Full text per page

    if headings:  # Ensure there is at least one heading
        first_heading_page = headings[0][1]  # Page number of first heading
        first_heading = headings[0][0]  # First heading text

        end_pos = extracted_text[first_heading_page].find(first_heading)  # Locate first heading start
        intro_text = ""

        # Extract text from all pages before the first heading appears
        for page_no in range(first_heading_page):
            intro_text += "\n" + extracted_text[page_no].strip()

        # Add the portion of the first heading's page before the heading
        intro_text += "\n" + extracted_text[first_heading_page][:end_pos].strip()
        if intro_text.strip():  # Store only if there's actual content
            sections["UNLABELED_SECTION"] = {"text": intro_text.strip(), "page": 0}


    for i in range(len(headings)):
        heading, page_num = headings[i]  # Current heading and its page number
        start_pos = extracted_text[page_num].find(heading)  # Locate heading start

        # Get next heading details (if exists)
        if i + 1 < len(headings):  
            next_heading, next_heading_page = headings[i + 1]  # Extract next heading's text & page num
            end_pos = extracted_text[next_heading_page].find(next_heading)  # Locate next heading start
        else:
            end_pos = None  # If no next heading, extract till the end

        # Extract content
        if next_heading_page == page_num:
            # Next heading is on the SAME page
            content = extracted_text[page_num][start_pos + len(heading):end_pos].strip()
        else:
            
            # Next heading is on a DIFFERENT page
            content = extracted_text[page_num][start_pos + len(heading):].strip()  # Take remaining content on current page

            # Append content from pages in between
            for page_no in range(page_num + 1, next_heading_page):
                content += "\n" + extracted_text[page_no].strip()

            # Finally, take content from the next heading's page up to `end_pos`
            content += "\n" + extracted_text[next_heading_page][:end_pos].strip()
        if end_pos is None:
                for page_no in range(page_num + 1, len(extracted_text)):
                    content += "\n" + extracted_text[page_no].strip()

        # Store extracted section
        sections[heading] = {"text": content, "page": page_num}

    return sections


def extract_headings(doc):
    """Extracts bold text as headings from the document."""
    headings = []
    
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_name = span["font"].lower()
                        if "bold" in font_name:  # Heading detected
                            heading_text = span["text"].strip()
                            if heading_text:
                                headings.append((heading_text, page.number))  # Store with page number

    return headings


async def generate_embeddings(heading_content):
    """Generates embeddings for extracted text sections based on bold headings."""
    combined_texts = [
        f"Heading: {heading}\nText: {info['text']}"
        for heading, info in heading_content.items()
    ]
    tasks = [emodel.aembed_query(text) for text in combined_texts]
    results = await asyncio.gather(*tasks)
    return dict(zip(heading_content.keys(), results))

async def store_embeddings(heading_content):
    """Stores extracted heading-content pairs in Pinecone."""
    embeddings = await generate_embeddings(heading_content)
    vectors = [
        (heading, vector, {
            "heading": heading,
            "text": heading_content[heading]["text"],
        })
        for heading, vector in embeddings.items()
    ]
    index.upsert(vectors)
    print("Data successfully uploaded to Pinecone!")
async def extract():
    try:
        sections = extract_text_by_headings(PDF_PATH)
        await store_embeddings(sections)
        return {"message": "Extraction successful", "data": sections}
    except Exception as e:
        print(f"Error in extract(): {e}")
        return {"error": str(e)}
