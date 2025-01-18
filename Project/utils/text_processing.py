import fitz

def extract_headings(path:str):
    headings=[]
    fonts_used=set()
    pdf_document=fitz.open(path)
    for page_number in range(len(pdf_document)):
        page=pdf_document[page_number]
        blocks=page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        fonts_used.add(span["font"])
                        if span["size"]>12:
                            text=span["text"]
                            if len(text)>0:
                                headings.append(text)
    pdf_document.close()
    return headings