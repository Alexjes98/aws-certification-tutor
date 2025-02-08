import pymupdf
import pdfplumber
import os

def lambda_handler(event, context):
    print("Hello World")
    doc = pymupdf.open("../sample_files/AWSLambda-DeveloperGuide.pdf")  # open a document
    out = open("output.txt", "wb")  # create a text output
    for page in doc:  # iterate the document pages
        text = page.get_text().encode("utf8")  # get plain text (is in UTF-8)        
        out.write(text)  # write text of page
        out.write(bytes((12,)))  # write page delimiter (form feed 0x0C)
    out.close()

if __name__ == "__main__":    
    lambda_handler(None, None)