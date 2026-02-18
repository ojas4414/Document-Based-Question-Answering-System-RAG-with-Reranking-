from pypdf import PdfReader
from pathlib import Path


def load_text(pdf_path:str)-> str:

    reader=PdfReader(pdf_path)
    page_text=[]
    for page in reader.pages:
        text=page.extract_text()
        if text:
            page_text.append(text)
    return "\n".join(page_text)

def load_document(dir_path:str):

    doc=[]
    dir_path=Path(dir_path)
    for file in dir_path.glob("*.pdf"):
        text=load_text(str(file))
        doc.append((file.name,text))
    return doc
