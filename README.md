# Handwritten Form OCR Application

A powerful web application that performs OCR (Optical Character Recognition) on handwritten forms using Google's Gemini 2.5 Flash model. Specifically designed to extract text from filled forms with rough or poorly-written handwriting.

## Features

- 📄 **PDF Upload**: Upload multi-page PDF documents
- 🖼️ **Page-by-Page Processing**: Each PDF page is converted to an image and processed in a separate API call
- 🔄 **Individual API Calls**: Each page = one API call (10 pages = 10 API calls)
- 🤖 **AI-Powered OCR**: Uses Gemini 2.5 Flash for accurate handwriting recognition
- ✅ **Form Structure Preservation**: Maintains the exact layout and structure of forms
- ✓ **Checkbox Detection**: Recognizes ticked checkboxes and malformed tick marks
- ❌ **Slash Detection**: Intelligently excludes sections that are crossed out
- 🎨 **Beautiful UI**: Clean, modern, and responsive interface built with React and TypeScript

## Technology Stack

### Backend
- **Python 3.8+**
- **FastAPI**: Modern web framework for building APIs
- **pdf2image**: PDF to image conversion
- **Pillow**: Image processing
- **google-generativeai**: Gemini API integration

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **Axios**: HTTP client

## Prerequisites

1. **Python 3.8 or higher**
2. **Node.js 16 or higher**
3. **Poppler** (for PDF conversion):
   - **Windows**: Download from [here](https://github.com/oschwartz10612/poppler-windows/releases/) and add to PATH
   - **macOS**: `brew install poppler`
   - **Linux**: `sudo apt-get install poppler-utils`

## Installation

### 1. Clone the Repository

```bash
cd "C:\Users\Abhijit\OneDrive - iitkgp.ac.in\Desktop\AI_Planet\Engish_OCR"
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from root)
cd frontend

# Install dependencies
npm install
```

### 4. Environment Configuration

The `.env` file is already created in the root directory with your Gemini API key:
```
GEMINI_API_KEY=AIzaSyAkLJqQFeNxRcNYMQVUa4nAbSGXdefwrYI
```

## Running the Application

### Start Backend Server

```bash
# From backend directory
cd backend
python main.py
```

The backend will start at `http://localhost:8000`

### Start Frontend Development Server

```bash
# From frontend directory (in a new terminal)
cd frontend
npm run dev
```

The frontend will start at `http://localhost:3000` (or another port if 3000 is busy)

## Usage

1. **Open the application** in your browser (usually `http://localhost:3000`)
2. **Upload a PDF** by dragging and dropping or clicking to browse
3. **Click "Extract Text"** to start the OCR process
4. **View results** - each page's extracted text will be displayed in order

## How It Works

### OCR Prompt Engineering

The application uses a sophisticated prompt that instructs Gemini to:

1. **Handle Poor Handwriting**: Recognize rough, unclear handwriting from less-educated individuals
2. **Preserve Form Structure**: Maintain exact layout, spacing, and hierarchy
3. **Detect Tick Marks**: Identify checkboxes and tick marks (even malformed ones)
4. **Exclude Slashed Sections**: Skip content that's been crossed out
5. **Distinguish Ticks from Slashes**: Carefully differentiate between selection marks and exclusion marks

### Processing Pipeline

```
PDF Upload → PDF to Images → For Each Page: ONE API Call → Gemini 2.5 Flash → OCR Text → Display Results
```

**Important**: If your PDF has 10 pages, the system makes **10 separate API calls** to Gemini (one per page). This ensures optimal processing and error isolation.

## API Endpoints

### `POST /ocr`
Upload a PDF file for OCR processing. Each page is processed with a separate API call.

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF file

**Response:**
```json
{
  "total_pages": 10,
  "api_calls_made": 10,
  "results": [
    {
      "page_number": 1,
      "ocr_text": "Extracted text...",
      "status": "success"
    }
  ]
}
```

**Note**: For a 10-page PDF, this endpoint makes 10 individual API calls to Gemini (one per page).

### `GET /health`
Health check endpoint.

### `GET /`
API information.

## Project Structure

```
Engish_OCR/
├── backend/
│   ├── main.py              # FastAPI server
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Main React component
│   │   ├── App.css         # Styles
│   │   ├── main.tsx        # React entry point
│   │   └── index.css       # Global styles
│   ├── index.html          # HTML template
│   ├── package.json        # Node dependencies
│   ├── tsconfig.json       # TypeScript config
│   └── vite.config.ts      # Vite config
├── .env                    # Environment variables
└── README.md               # This file
```

## Troubleshooting

### Poppler Not Found
If you get an error about `poppler` not being installed:
- **Windows**: Download Poppler from [here](https://github.com/oschwartz10612/poppler-windows/releases/), extract it, and add the `bin` folder to your system PATH
- **macOS**: `brew install poppler`
- **Linux**: `sudo apt-get install poppler-utils`

### CORS Errors
Make sure both backend and frontend are running on the correct ports and the CORS middleware is properly configured.

### API Key Issues
Verify that the Gemini API key in `.env` is correct and has not expired.

## Important Notes

- The application uses **Gemini 2.5 Flash** model for optimal performance (latest version)
- **Each PDF page = ONE API call**: A 10-page PDF makes 10 separate Gemini API calls
- Large PDFs may take longer to process (approx. 2-5 seconds per page)
- The quality of OCR depends on image quality and handwriting clarity
- Make sure you have sufficient API quota for Gemini
- Monitor your API usage: Each page consumes one API call

## License

This project is for educational and development purposes.

## Deployment

### Recommended: Deploy to Vercel (Both Frontend & Backend)

The easiest way to deploy this application is to use Vercel for both the frontend and backend. This provides:
- ✅ Single platform deployment
- ✅ Automatic HTTPS and CDN
- ✅ Easy environment variable management
- ✅ Fast deployment and updates

**See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed instructions.**

**Quick Steps:**

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Deploy to Vercel"
   git push origin main
   ```

2. **Import to Vercel**
   - Go to https://vercel.com
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Vercel auto-detects configuration from `vercel.json`

3. **Add Environment Variable**
   - In Vercel project settings → Environment Variables
   - Add: `GEMINI_API_KEY` = your API key

4. **Deploy!**
   - Click Deploy
   - Your app will be live at `https://your-project.vercel.app`

### Alternative: Deploy Backend to Render (Legacy)

If you prefer to use Render for the backend, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

**Quick overview:**
- Backend on Render: Use the `backend/` directory with `render.yaml`
- Frontend on Vercel: Use the `frontend/` directory
- Set `VITE_API_URL` in Vercel to point to your Render backend URL

## Environment Variables

### For Vercel Deployment

**Backend (Vercel Environment Variables):**
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Frontend:**
No environment variables needed when deployed to Vercel (uses relative paths).

### For Local Development

**Backend (`backend/.env`):**
```env
GEMINI_API_KEY=your_gemini_api_key_here
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Frontend (`frontend/.env`):**
```env
VITE_API_URL=http://localhost:8000
```

**For local development:** Copy `backend/env.template` to `backend/.env` and `frontend/env.template` to `frontend/.env`, then fill in your values.

## Support

For issues or questions, please check the error messages in the console and ensure all dependencies are properly installed.

## GitHub Repository

https://github.com/abhijit-aiplanet/English_OCR

