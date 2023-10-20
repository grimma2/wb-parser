import re
import os
import glob
import pdfminer.high_level

def get_email_from_file(pdf_file_path: str, text_file_path) -> str:
    with open(pdf_file_path, "rb") as pdf_file:
        text_file = open(text_file_path, "a+")
        pdfminer.high_level.extract_text_to_fp(pdf_file, text_file)
        text_file.close()

    with open(text_file_path, "r", encoding="utf-8") as file:
        all_text = file.read()

    #os.remove(pdf_file_path)
    os.remove(text_file_path)

    email = re.findall(r'E-mail(.*?)(\d)', all_text, re.DOTALL)
    if email == []:
        return ""
    
    return email[0][0].lower()

"""print(get_email_from_file(pdf_file_path=glob.glob("../pdf_files/*.pdf")[0], 
                          text_file_path="../pdf_files/current_pdf_text.txt"))"""

