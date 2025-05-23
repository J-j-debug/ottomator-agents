import PyPDF2
from PyPDF2.errors import PdfReadError
import os
from reportlab.pdfgen import canvas

def extract_text_from_pdf(pdf_path: str, method: str = "pypdf2") -> str:
    '''
    Simplified text extraction, primarily using PyPDF2.
    Fallback for 'unstructured' or 'pdfminer' will just print a message.
    '''
    extracted_text = ""
    if method == "pypdf2":
        print(f"Attempting text extraction with: {method} from '{pdf_path}'")
        try:
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                if reader.is_encrypted:
                    try:
                        reader.decrypt('') 
                        print(f"Successfully decrypted '{pdf_path}' with empty password.")
                    except Exception as decrypt_err:
                        print(f"Failed to decrypt '{pdf_path}' with empty password: {decrypt_err}.")
                        return "" 
                
                text_parts = []
                if reader.pages:
                    for page_num in range(len(reader.pages)):
                        page = reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    extracted_text = "\n".join(text_parts) 
                else:
                    extracted_text = ""
            if extracted_text.strip():
                print(f"Successfully extracted text using {method}.")
            else:
                print(f"{method} extracted no text or only whitespace.")
            return extracted_text
        except FileNotFoundError:
            print(f"Error: File not found at '{pdf_path}'.")
            return ""
        except PdfReadError as pre:
            print(f"PyPDF2 PdfReadError for '{pdf_path}': {pre}.")
            return ""
        except Exception as e:
            print(f"General error using {method} for PDF text extraction from '{pdf_path}': {e}")
            return ""
    else:
        print(f"Method '{method}' is not the primary 'pypdf2' method for this simplified processor. No text extracted by this placeholder.")
        return ""


def extract_metadata_from_pdf(pdf_path: str) -> dict:
    '''
    Simplified metadata extraction, primarily using PyPDF2.
    '''
    metadata_dict = {}
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            if reader.is_encrypted:
                try:
                    reader.decrypt('')
                    print(f"Successfully decrypted '{pdf_path}' with empty password for metadata.")
                except Exception as decrypt_err:
                    print(f"Failed to decrypt '{pdf_path}' for metadata: {decrypt_err}")
                    return {"Error": "Encrypted PDF, decryption failed.", "FilePath": pdf_path}

            metadata = reader.metadata
            if metadata:
                metadata_dict["Title"] = str(metadata.title) if metadata.title is not None else None
                metadata_dict["Author"] = str(metadata.author) if metadata.author is not None else None
                metadata_dict["Subject"] = str(metadata.subject) if metadata.subject is not None else None
                metadata_dict["Creator"] = str(metadata.creator) if metadata.creator is not None else None
                metadata_dict["Producer"] = str(metadata.producer) if metadata.producer is not None else None
                
                raw_metadata = metadata.get_object()
                if raw_metadata: 
                    creation_date_obj = raw_metadata.get("/CreationDate")
                    mod_date_obj = raw_metadata.get("/ModDate")
                    metadata_dict["CreationDate"] = str(creation_date_obj) if creation_date_obj else None
                    metadata_dict["ModDate"] = str(mod_date_obj) if mod_date_obj else None
                else: 
                    metadata_dict["CreationDate"] = None 
                    metadata_dict["ModDate"] = None 
                
                metadata_dict["PageCount"] = len(reader.pages) if reader.pages else 0
            else: 
                 metadata_dict["PageCount"] = len(reader.pages) if reader.pages else 0


        return metadata_dict
    except FileNotFoundError:
        print(f"Error: File not found at '{pdf_path}' for metadata extraction.")
        return {"Error": "File not found.", "FilePath": pdf_path}
    except PdfReadError as pre:
        print(f"PyPDF2 PdfReadError for '{pdf_path}' during metadata extraction: {pre}.")
        return {"Error": f"PyPDF2 PdfReadError: {pre}", "FilePath": pdf_path}
    except Exception as e:
        print(f"An unexpected error occurred while extracting metadata from '{pdf_path}': {e}")
        return {"Error": f"Unexpected error: {e}", "FilePath": pdf_path}

if __name__ == '__main__':
    dummy_pdf_name = "dummy_simplified_processor_test.pdf"
    
    paths_to_try = []
    cwd = os.getcwd()
    if cwd == "/app":
        project_dir_path = "/app/multi_agent_doc_system"
        if os.path.exists(project_dir_path):
             paths_to_try.append(os.path.join(project_dir_path, dummy_pdf_name))
        else:
            paths_to_try.append(os.path.join(cwd, dummy_pdf_name))
    else:
        paths_to_try.append(os.path.join(cwd, dummy_pdf_name))
    paths_to_try.append(os.path.join("/tmp", dummy_pdf_name))
    paths_to_try = list(dict.fromkeys(paths_to_try))


    dummy_pdf_path = ""
    for path_option in paths_to_try:
        try:
            dir_name = os.path.dirname(path_option)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)

            c = canvas.Canvas(path_option)
            c.drawString(100, 750, "Hello from simplified pdf_processor.py!")
            c.drawString(100, 700, "This PDF is for testing the simplified version.")
            c.setTitle("Simplified Test Doc")
            c.setAuthor("Simplified Test Author")
            c.save()
            dummy_pdf_path = os.path.abspath(path_option)
            print(f"Dummy PDF for simplified test created at: {dummy_pdf_path}")
            break
        except Exception as e:
            print(f"Error creating dummy PDF at '{path_option}': {e}")
            dummy_pdf_path = ""

    if not dummy_pdf_path:
        print("Critical: Failed to create dummy PDF for simplified processor. Aborting demonstration.")
    else:
        print(f"\n--- Testing SIMPLIFIED PDF Processor for: {dummy_pdf_path} ---")
        
        print("\n--- Testing Metadata Extraction (Simplified) ---")
        metadata = extract_metadata_from_pdf(dummy_pdf_path)
        if metadata:
            print("Extracted Metadata:")
            for key, value in metadata.items():
                print(f"  {key}: {value}")
        else:
            print("No metadata extracted or an error occurred.")

        print("\n--- Testing Text Extraction (Simplified) ---")
        text_content = extract_text_from_pdf(dummy_pdf_path) 
        print(f"Extracted Text (pypdf2 try):\n'''{repr(text_content)}'''")
        
        text_content_unstructured = extract_text_from_pdf(dummy_pdf_path, method="unstructured")
        print(f"Extracted Text (unstructured try): '{repr(text_content_unstructured)}'")
        text_content_pdfminer = extract_text_from_pdf(dummy_pdf_path, method="pdfminer")
        print(f"Extracted Text (pdfminer try): '{repr(text_content_pdfminer)}'")

        try:
            os.remove(dummy_pdf_path)
            print(f"\nSuccessfully removed dummy PDF: {dummy_pdf_path}")
        except Exception as e:
            print(f"Error removing dummy PDF '{dummy_pdf_path}': {e}")

    print("\n--- Testing with a Non-Existent File (Simplified) ---")
    non_existent_file = "non_existent_for_simplified.pdf"
    metadata_non_existent = extract_metadata_from_pdf(non_existent_file)
    print(f"Metadata from non-existent file: {metadata_non_existent}")
    text_non_existent = extract_text_from_pdf(non_existent_file)
    print(f"Text from non-existent file: '{repr(text_non_existent)}'")
    print("\n--- End of simplified pdf_processor tests ---")
