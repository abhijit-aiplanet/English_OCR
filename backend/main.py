import os
import io
import base64
from typing import List
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import json
import asyncio
import fitz  # PyMuPDF
from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Get the directory where this script is located
BACKEND_DIR = Path(__file__).parent.absolute()
ROOT_DIR = BACKEND_DIR.parent

# Try to load .env from backend directory first, then root directory
env_path_backend = BACKEND_DIR / ".env"
env_path_root = ROOT_DIR / ".env"

if env_path_backend.exists():
    load_dotenv(dotenv_path=env_path_backend)
    print(f"✓ Loaded .env from: {env_path_backend}")
elif env_path_root.exists():
    load_dotenv(dotenv_path=env_path_root)
    print(f"✓ Loaded .env from: {env_path_root}")
else:
    print(f"⚠ Warning: No .env file found in {env_path_backend} or {env_path_root}")

app = FastAPI(title="Handwritten Form OCR API")

# Configure CORS - Allow both local and production origins
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API Key - ONLY from .env file, NOT from system environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    error_msg = (
        "GEMINI_API_KEY not found in .env file!\n"
        f"Please create a .env file in: {env_path_backend}\n"
        f"or in: {env_path_root}\n"
        "with the content: GEMINI_API_KEY=your_api_key_here"
    )
    raise ValueError(error_msg)

print(f"✓ Gemini API Key loaded from .env file (length: {len(GEMINI_API_KEY)} chars)")
print(f"✓ API Key preview: {GEMINI_API_KEY[:20]}...")

# Initialize Gemini Client with EXPLICIT API key (not relying on environment)
client = genai.Client(api_key=GEMINI_API_KEY)

def create_ocr_prompt() -> str:
    """
    Create a detailed prompt for Gemini to perform OCR on handwritten forms.
    Now outputs in MARKDOWN format for better rendering.
    Special emphasis on accurate number recognition and contextual understanding.
    """
    return """You are an expert OCR system specializing in handwritten text recognition from filled forms. Your task is to extract ALL text from this image with extreme precision and output it in MARKDOWN format.

CRITICAL INSTRUCTIONS:

0. CONTEXTUAL ANALYSIS (THINK FIRST - VERY IMPORTANT):
   **BEFORE starting OCR, take a moment to UNDERSTAND the document:**
   
   - **Step 1 - Document Type Identification:**
     * What TYPE of document is this? (Test report, application form, data sheet, survey, inspection form, etc.)
     * What INDUSTRY/DOMAIN? (Medical, textile, manufacturing, quality control, research, etc.)
     * What is the MAIN PURPOSE? (Recording data, certification, compliance, testing results, etc.)
   
   - **Step 2 - Document Structure Analysis:**
     * Look at the overall layout and sections
     * Identify key fields and their purposes (Sample numbers, dates, test results, etc.)
     * Note what kind of data is expected in each field (numbers, codes, names, measurements, etc.)
     * Observe any repeated patterns or standard formats
   
   - **Step 3 - Domain Knowledge Application:**
     * If it's a TEST REPORT → expect: test methods, sample numbers, measurements, pass/fail indicators
     * If it's a DATA SHEET → expect: technical specifications, standards (ISO, ASTM, etc.), numerical data
     * If it's a FORM → expect: applicant information, dates, signatures, checkboxes
     * Use your knowledge of the domain to understand what values are REASONABLE and EXPECTED
   
   - **Step 4 - Context-Aware Decision Making:**
     * When you encounter UNCLEAR handwriting, use the document context to decide
     * Ask yourself: "Given this is a [document type] in [domain], what makes sense here?"
     * Examples:
       - In a "Sample Number" field → must be a number (4231, not "four two three one")
       - In a "Test Method" field → likely a standard code (ISO 6330, not random letters)
       - In a "Date" field → must be a valid date format
       - In a "Temperature" field → must be a reasonable temperature value
       - In a "Buyer" field → must be a name or company code
     * If torn between "A" or "B", ask: "Which one fits the CONTEXT of this field/document?"
   
   - **Step 5 - Pattern Recognition:**
     * Notice if certain information repeats (same buyer, similar sample numbers, etc.)
     * Use patterns from clear text to help interpret unclear text
     * If you see "ISO 6330" written clearly once, and encounter unclear text that looks similar elsewhere, it's likely the same
   
   - **Step 6 - Reasonableness Check:**
     * After OCR-ing a value, ask: "Does this make sense given the document type?"
     * Temperature of "8 0°C" → should be "80°C" (reasonable washing temperature)
     * Sample number "4 231" → should be "4231" (continuous number makes sense)
     * Test method "IS O 6330" → should be "ISO 6330" (known standard)
   
   **USE THIS CONTEXTUAL UNDERSTANDING THROUGHOUT THE ENTIRE OCR PROCESS**
   - Don't just read characters blindly
   - Think about what SHOULD be there based on context
   - Use domain knowledge to resolve ambiguities
   - Make intelligent decisions based on document type

1. HANDWRITING RECOGNITION:
   - The form contains handwritten text by people with limited education
   - Handwriting may be VERY rough, unclear, or poorly formed
   - Make your BEST effort to decipher even the most difficult handwriting
   - Consider context clues from the form structure to help interpret unclear writing
   - If a word is partially legible, provide your best interpretation

2. NUMBER RECOGNITION (EXTREMELY IMPORTANT):
   - **CRITICAL**: Numbers are the MOST IMPORTANT data in these forms
   - Pay EXTREME attention to handwritten numbers - they MUST be accurate
   - When you see digits written together (like 45, 123, 4231), they form a SINGLE NUMBER
   - DO NOT separate digits with spaces or hyphens unless clearly intended
   - Examples:
     * If "45" is written (even if gap between 4 and 5), output: 45 (NOT "4 5" or "4-5")
     * If "123" is written, output: 123 (NOT "1 23" or "1-2-3")
     * If "4231" is written, output: 4231 (NOT "4 231" or "42 31")
   - Look at the CONTEXT:
     * In number fields (Sample Number, Date, measurements, codes), digits form complete numbers
     * In quantity fields, temperatures, weights - always complete numbers
     * Only separate if there's CLEAR punctuation (like "12.5" or "10-20")
   - Handwritten numbers may have:
     * Digits written close together → Still ONE number
     * Slight gaps between digits → Still ONE number
     * Connected digits → ONE number
     * Varying digit sizes → Still ONE number
   - **VERIFY**: After writing a number, ask yourself: "Should these digits be together?" 
     * If it's in a numbered field, the answer is almost always YES
   - Common mistakes to AVOID:
     * Writing "45" as "4 5" ❌
     * Writing "123" as "1 23" ❌  
     * Writing "4231" as "4 231" ❌
     * Adding hyphens where none exist ❌

3. MARKDOWN FORMATTING (Keep it Clean & Beautiful):
   
   Use markdown to make the output readable and structured:
   
   - **Headers:** Use # for main title, ## for sections, ### for subsections
   - **Bold labels:** **Field Name:** value (for form fields)
   - **Tables:** For any tabular data - always use markdown tables:
     ```
     | Column 1 | Column 2 |
     |----------|----------|
     | Value 1  | Value 2  |
     ```
   - **Lists:** Use - [x] for checked boxes, - [ ] for unchecked
   - **Spacing:** Add blank lines between sections for readability
   - **Structure:** Mirror the form's layout exactly

4. CHECKBOXES:
   - Checked: - [x] Option name
   - Unchecked: - [ ] Option name
   - Note: A tick might look like a slanted line - still a tick!

5. SLASHED OUT SECTIONS:
   - If crossed out (heavy lines through it), skip it entirely
   - Don't confuse with tick marks (single mark = tick, heavy cross = skip)

6. BLANK FIELDS:
   - If empty: Leave blank or use ______

7. NUMBER VALIDATION:
   - Scan all numbers before submitting
   - Multi-digit numbers must be continuous: 45 not "4 5"
   - No extra hyphens: 45 not "4-5"

8. AMBIGUOUS TEXT:
   - Use context to decide (refer to Step 0)
   - Only use [UNCLEAR] as last resort after trying context

9. FINAL CHECK:
   - Review: Numbers make sense? Technical terms correct?
   - Verify: Markdown properly formatted?
   - Confirm: Output matches form structure?

Begin OCR: Think about document type first (Step 0), then extract in clean MARKDOWN:"""

def convert_pdf_to_images(pdf_bytes: bytes) -> List[Image.Image]:
    """
    Convert PDF bytes to a list of PIL Images using PyMuPDF.
    PyMuPDF works better on serverless environments like Vercel.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        images = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Render page at 300 DPI (scale factor = 300/72 = 4.166...)
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        doc.close()
        return images
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error converting PDF to images: {str(e)}")

def process_uploaded_file(file_bytes: bytes, filename: str) -> List[Image.Image]:
    """
    Process uploaded file (PDF or image) and return a list of PIL Images.
    For PDFs: converts each page to an image
    For images: returns a single-item list with the image
    """
    file_ext = filename.lower().split('.')[-1]
    
    # Check if it's an image file
    if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']:
        try:
            image = Image.open(io.BytesIO(file_bytes))
            # Convert to RGB if necessary (some formats like PNG can have alpha channel)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return [image]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
    
    # Check if it's a PDF
    elif file_ext == 'pdf':
        return convert_pdf_to_images(file_bytes)
    
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: .{file_ext}. Please upload a PDF or image file (JPG, PNG, etc.)"
        )

def image_to_base64(image: Image.Image) -> str:
    """
    Convert PIL Image to base64 string.
    """
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

async def process_image_with_gemini(image: Image.Image, page_number: int) -> str:
    """
    Send a SINGLE image to Gemini for OCR processing.
    Each page is processed in a separate API call.
    
    Args:
        image: PIL Image object for a single PDF page
        page_number: The page number being processed (for logging/debugging)
    
    Returns:
        Extracted OCR text as string
    """
    try:
        prompt = create_ocr_prompt()
        
        # Configure generation for DETERMINISTIC output
        # Temperature=0 ensures no randomness, strict adherence to prompt
        generation_config = types.GenerateContentConfig(
            temperature=0.0,           # No randomness - completely deterministic
            max_output_tokens=8192,    # Reasonable limit for OCR output
            response_mime_type="text/plain"  # Plain text output
        )
        
        print(f"  ├─ Using deterministic settings: temp=0.0")
        
        # Make a SINGLE API call for this ONE page
        # Using the new Gemini API syntax with client.models.generate_content
        # PIL images can be directly passed as inputs (converted by SDK)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, image],  # Prompt first, then image
            config=generation_config   # Apply deterministic configuration
        )
        
        if not response.text:
            raise ValueError(f"Empty response from Gemini for page {page_number}")
        
        return response.text.strip()
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing page {page_number} with Gemini: {str(e)}"
        )

@app.get("/")
async def root():
    return {"message": "Handwritten Form OCR API", "status": "running"}

async def process_file_streaming(file_bytes: bytes, filename: str):
    """
    Generator function that processes file (PDF/image) and yields results in real-time.
    Each page result is sent immediately as it's processed WITH the page image.
    """
    try:
        # Convert file to images (PDF pages or single image)
        images = process_uploaded_file(file_bytes, filename)
        
        # Send initial metadata
        yield f"data: {json.dumps({'type': 'metadata', 'total_pages': len(images)})}\n\n"
        
        # Process each page individually with separate API calls
        for idx, image in enumerate(images, 1):
            try:
                # IMPORTANT: This makes ONE API call per page
                print(f"Processing page {idx}/{len(images)} with individual API call...")
                
                # Convert image to base64 for sending to frontend
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                # Send processing status WITH image
                processing_data = {
                    "type": "processing",
                    "page_number": idx,
                    "page_image": f"data:image/png;base64,{img_base64}"
                }
                yield f"data: {json.dumps(processing_data)}\n\n"
                
                ocr_text = await process_image_with_gemini(image, idx)
                
                # Send result immediately as it's ready WITH image
                result = {
                    "type": "result",
                    "page_number": idx,
                    "ocr_text": ocr_text,
                    "status": "success",
                    "page_image": f"data:image/png;base64,{img_base64}"
                }
                yield f"data: {json.dumps(result)}\n\n"
                print(f"Successfully processed page {idx}/{len(images)}")
                
            except Exception as e:
                print(f"Error processing page {idx}: {str(e)}")
                error_result = {
                    "type": "result",
                    "page_number": idx,
                    "ocr_text": "",
                    "status": "error",
                    "error": str(e),
                    "page_image": None
                }
                yield f"data: {json.dumps(error_result)}\n\n"
        
        # Send completion signal
        yield f"data: {json.dumps({'type': 'complete', 'api_calls_made': len(images)})}\n\n"
        
    except Exception as e:
        error_data = {
            "type": "error",
            "message": f"Error processing file: {str(e)}"
        }
        yield f"data: {json.dumps(error_data)}\n\n"

@app.post("/ocr/stream")
async def perform_ocr_streaming(file: UploadFile = File(...)):
    """
    Process uploaded file (PDF or image) and STREAM OCR results in real-time.
    Uses Server-Sent Events (SSE) to send results as they're processed.
    IMPORTANT: Each page/image is sent as a SEPARATE API call to Gemini.
    
    Supported formats: PDF, JPG, JPEG, PNG, GIF, BMP, TIFF, WEBP
    
    Event Types:
    - metadata: Initial data with total_pages
    - processing: When starting to process a page
    - result: OCR result for a page (sent immediately)
    - complete: All pages processed
    - error: If an error occurs
    """
    # Validate file type
    allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']
    file_ext = file.filename.lower().split('.')[-1]
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Read file bytes
    file_bytes = await file.read()
    
    return StreamingResponse(
        process_file_streaming(file_bytes, file.filename),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/ocr")
async def perform_ocr(file: UploadFile = File(...)):
    """
    Process uploaded file (PDF or image) and return OCR results (non-streaming version).
    IMPORTANT: Each page/image is sent as a SEPARATE API call to Gemini.
    
    Supported formats: PDF, JPG, JPEG, PNG, GIF, BMP, TIFF, WEBP
    
    Note: Use /ocr/stream for real-time results as pages are processed.
    """
    # Validate file type
    allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']
    file_ext = file.filename.lower().split('.')[-1]
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Read file bytes
        file_bytes = await file.read()
        
        # Convert file to images (PDF pages or single image)
        images = process_uploaded_file(file_bytes, file.filename)
        
        # Process each page individually with separate API calls
        results = []
        for idx, image in enumerate(images, 1):
            try:
                # IMPORTANT: This makes ONE API call per page/image
                print(f"Processing image {idx}/{len(images)} with individual API call...")
                ocr_text = await process_image_with_gemini(image, idx)
                results.append({
                    "page_number": idx,
                    "ocr_text": ocr_text,
                    "status": "success"
                })
                print(f"Successfully processed image {idx}/{len(images)}")
            except Exception as e:
                print(f"Error processing image {idx}: {str(e)}")
                results.append({
                    "page_number": idx,
                    "ocr_text": "",
                    "status": "error",
                    "error": str(e)
                })
        
        return JSONResponse(content={
            "total_pages": len(images),
            "results": results,
            "api_calls_made": len(images)  # Shows how many API calls were made
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "gemini_configured": bool(GEMINI_API_KEY)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

