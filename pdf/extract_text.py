import PyPDF2
import argparse

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def save_text_to_file(text, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text)

def main():
    parser = argparse.ArgumentParser(description="Extract text from a PDF file.")
    parser.add_argument("input_pdf", help="Path to the input PDF file")
    args = parser.parse_args()

    text = extract_text_from_pdf(args.input_pdf)
    print(text)
if __name__ == "__main__":
    main()
