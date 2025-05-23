import asyncio
import os
from dotenv import load_dotenv
from openai import OpenAI # Using synchronous OpenAI for now, can be AsyncOpenAI

# Assuming pdf_processor.py is in the same directory
from pdf_processor import extract_text_from_pdf, extract_metadata_from_pdf

# LightRAG imports
from lightrag import LightRAG
from lightrag.components.embedder import OpenAIEmbedder
from lightrag.components.llm import OpenAIChatLLM

# Placeholder for actual LightRAG models/config if different from defaults
# from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

class IndexingAgent:
    def __init__(self, openai_api_key: str = None):
        load_dotenv() # Load environment variables from .env file
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set it in .env or pass it directly.")
        
        self.openai_client = OpenAI(api_key=self.api_key)
        self.lightrag_instance = None
        print("IndexingAgent initialized.")

    def initialize_lightrag(self, working_dir: str = "./lightrag_data"):
        print(f"Initializing LightRAG in working directory: {working_dir}...")
        # Ensure the working directory exists
        os.makedirs(working_dir, exist_ok=True)

        # Using LightRAG's newer component style if applicable, else use direct functions
        # These are example components; actual LightRAG setup might vary based on its version/API.
        # Refer to LightRAG documentation for the most current way to initialize.
        try:
            # Example: Configure with specific models if desired
            # This assumes LightRAG components are compatible with direct model strings.
            # Adjust if LightRAG expects specific function wrappers like gpt_4o_mini_complete.
            embedder = OpenAIEmbedder(api_key=self.api_key, model="text-embedding-ada-002")
            llm = OpenAIChatLLM(api_key=self.api_key, model="gpt-4o-mini")


            self.lightrag_instance = LightRAG(
                # embedding_func=openai_embed, # Older style
                # llm_model_func=gpt_4o_mini_complete, # Older style
                embedder=embedder, # Newer component style
                llm=llm, # Newer component style
                working_dir=working_dir
            )
            # For synchronous initialization if LightRAG offers it, or if it handles async internally.
            # If LightRAG's initialize_storages is async, it needs to be handled in an async context.
            # For now, we'll assume LightRAG can be set up, and storage initialization is handled by its methods.
            # Example: asyncio.run(self.lightrag_instance.initialize_storages()) # If called from sync code
            print("LightRAG instance configured. Storage initialization might be pending or handled by LightRAG.")
        except Exception as e:
            print(f"Error initializing LightRAG: {e}")
            self.lightrag_instance = None


    def _summarize_text(self, text: str, max_chars: int = 500) -> str:
        print("Summarization started (placeholder)...")
        if not text:
            return "No text provided for summarization."
        # Placeholder: returns first N characters or a fixed message.
        # Actual summarization will use self.openai_client.chat.completions.create(...)
        summary = text[:max_chars] + "..." if len(text) > max_chars else text
        return f"[Placeholder Summary]: {summary}"

    def _classify_document(self, text: str) -> str:
        print("Classification started (placeholder)...")
        if not text:
            return "No text provided for classification."
        # Placeholder: returns a fixed message.
        # Actual classification will use self.openai_client.chat.completions.create(...)
        return "[Placeholder Classification]: General Legal Document"

    def process_pdf_document(self, pdf_path: str) -> dict:
        print(f"Processing PDF document: {pdf_path}...")
        try:
            # Ensure pdf_processor functions are available
            text = extract_text_from_pdf(pdf_path)
            metadata = extract_metadata_from_pdf(pdf_path)
        except Exception as e:
            print(f"Error during PDF processing via pdf_processor: {e}")
            return {"error": str(e), "path": pdf_path}

        summary = self._summarize_text(text)
        classification = self._classify_document(text)

        processed_data = {
            "file_path": pdf_path,
            "metadata": metadata,
            "extracted_text_snippet": text[:200] + "..." if text else "N/A", # Snippet for brevity
            "full_text_char_count": len(text) if text else 0,
            "summary": summary,
            "classification": classification,
        }
        
        print(f"Successfully processed {pdf_path}.")
        # In a real scenario, 'text' (full) would also be part of what's indexed or stored.
        return processed_data
    
    async def aprocess_pdf_document_and_index(self, pdf_path: str):
        # Example of how one might structure an async method for LightRAG if it's async
        if not self.lightrag_instance:
            print("Error: LightRAG instance not initialized. Call initialize_lightrag first.")
            return None
        
        print(f"Asynchronously processing and indexing PDF: {pdf_path}")
        processed_info = self.process_pdf_document(pdf_path) # Initial sync processing

        if "error" in processed_info:
            print(f"Skipping indexing for {pdf_path} due to processing error.")
            return processed_info

        # Assuming processed_info contains 'full_text' or similar for indexing
        full_text = extract_text_from_pdf(pdf_path) # Re-extract if not in processed_info fully

        if full_text:
            try:
                # LightRAG's ainsert might take text directly.
                # It might also support inserting with metadata, check LightRAG docs.
                # Example: await self.lightrag_instance.ainsert(full_text, metadata=processed_info.get('metadata'))
                print(f"Attempting to index content from {pdf_path} into LightRAG...")
                # The actual call to ainsert will depend on LightRAG's API.
                # This is a placeholder for the actual LightRAG insertion.
                # await self.lightrag_instance.ainsert(full_text) 
                # For now, we'll simulate this by printing what would be indexed.
                print(f"SIMULATED: Content from {pdf_path} (first 100 chars: '{full_text[:100]}...') would be sent to LightRAG for indexing.")
                processed_info["indexing_status"] = "Simulated as successfully indexed by LightRAG"
            except Exception as e:
                print(f"Error during LightRAG ainsert for {pdf_path}: {e}")
                processed_info["indexing_status"] = f"Failed: {e}"
        else:
            print(f"No text extracted from {pdf_path}, skipping LightRAG indexing.")
            processed_info["indexing_status"] = "Skipped (no text)"
        
        return processed_info


async def main_async():
    print("Starting Asynchronous Indexing Agent Demo...")
    agent = IndexingAgent()
    agent.initialize_lightrag() # Initialize LightRAG instance

    if not agent.lightrag_instance:
        print("LightRAG failed to initialize. Aborting demo.")
        return

    # Create a dummy PDF for testing (requires reportlab)
    # This part is synchronous and might be better handled outside main_async or made async
    dummy_pdf_for_indexing = "dummy_indexing_test.pdf"
    # Check if pdf_processor.py has the main block to create its dummy PDF
    # For simplicity, we'll try to create one here directly if pdf_processor's main isn't callable easily
    try:
        from reportlab.pdfgen import canvas as reportlab_canvas
        c = reportlab_canvas.Canvas(dummy_pdf_for_indexing)
        c.drawString(100, 750, "This is a test PDF for the IndexingAgent and LightRAG.")
        c.drawString(100, 700, "It contains some sample text to be processed and indexed.")
        c.setTitle("Indexing Test Doc")
        c.setAuthor("Async Main")
        c.save()
        print(f"Created dummy PDF: {dummy_pdf_for_indexing}")
        
        # Test processing and "indexing" (simulated)
        result = await agent.aprocess_pdf_document_and_index(dummy_pdf_for_indexing)
        print("\n--- Async Processing and Indexing Result ---")
        if result:
            for key, value in result.items():
                print(f"  {key}: {value}")
        
        os.remove(dummy_pdf_for_indexing) # Clean up
        print(f"Removed dummy PDF: {dummy_pdf_for_indexing}")

    except ImportError:
        print("ReportLab is not installed. Skipping dummy PDF creation for async demo.")
    except Exception as e:
        print(f"Error in async main creating/processing dummy PDF: {e}")
    
    print("\nIf LightRAG was initialized and ainsert was real, the content would be in its vector store.")


if __name__ == '__main__':
    # Demonstrates synchronous processing part
    print("Starting Synchronous Indexing Agent Demo...")
    agent = IndexingAgent()
    # No need to call initialize_lightrag for just process_pdf_document if it doesn't use lightrag_instance directly
    
    # Path to the dummy PDF created by pdf_processor.py (if its __main__ ran)
    # For a more robust test, this script should also create its own dummy PDF.
    # Let's use the one from pdf_processor.py's main block if it runs and creates it.
    # For simplicity, we'll assume pdf_processor.py's __main__ created "dummy_test_document_for_processing.pdf"
    # This is a bit fragile as it depends on another script's test side effect.
    
    # A better approach for __main__ here:
    dummy_pdf_main = "dummy_indexing_agent_test.pdf"
    try:
        from reportlab.pdfgen import canvas as reportlab_canvas_main
        c_main = reportlab_canvas_main.Canvas(dummy_pdf_main)
        c_main.drawString(100, 750, "Main test document for IndexingAgent (sync).")
        c_main.save()
        print(f"Created dummy PDF for sync test: {dummy_pdf_main}")

        processed_result = agent.process_pdf_document(dummy_pdf_main)
        print("\n--- Synchronous Processing Result ---")
        if processed_result:
            for key, value in processed_result.items():
                print(f"  {key}: {value}")
        os.remove(dummy_pdf_main)
        print(f"Removed dummy PDF: {dummy_pdf_main}")

    except ImportError:
        print("ReportLab is not installed. Skipping dummy PDF creation for sync demo.")
        print("Please install reportlab: pip install reportlab")
    except Exception as e:
        print(f"Error in sync main creating/processing dummy PDF: {e}")

    print("\n--- Running Asynchronous Demo ---")
    # Running the async main function
    # This might require the script to be run with `python -m asyncio` if top-level await is used
    # or if LightRAG's internals heavily rely on an existing event loop.
    # For now, simple asyncio.run() is used.
    try:
        asyncio.run(main_async())
    except RuntimeError as re: # Handle cases where asyncio.run might conflict if already running
        print(f"RuntimeError with asyncio.run: {re}. This can happen in some environments (e.g. Jupyter).")

