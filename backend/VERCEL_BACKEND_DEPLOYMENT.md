# Backend Deployment Guide for Vercel

This guide explains how to deploy the English OCR backend to Vercel separately from the frontend.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI** (optional but recommended):
   ```bash
   npm install -g vercel
   ```
3. **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Deployment Steps

### Option 1: Deploy via Vercel CLI (Recommended)

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel
   ```

4. **Add Environment Variables**:
   During deployment or after in the Vercel dashboard, add:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `ALLOWED_ORIGINS`: Comma-separated list of allowed origins (e.g., `https://your-frontend.vercel.app,http://localhost:5173`)

5. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via Vercel Dashboard (GitHub Integration)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Configure backend for Vercel deployment"
   git push origin main
   ```

2. **Import to Vercel**:
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your GitHub repository
   - **Important**: Set the **Root Directory** to `backend`
   - Click "Deploy"

3. **Configure Environment Variables** in Vercel Dashboard:
   - Go to Project Settings → Environment Variables
   - Add:
     - `GEMINI_API_KEY`: Your Gemini API key
     - `ALLOWED_ORIGINS`: Your frontend URLs (comma-separated)

4. **Redeploy**:
   - After adding environment variables, redeploy from the Deployments tab

## Project Structure

```
backend/
├── api/
│   └── index.py          # Vercel serverless handler
├── main.py               # FastAPI application
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
├── .vercelignore        # Files to ignore during deployment
└── .env.template        # Template for local development
```

## Configuration Details

### vercel.json
- Configures Vercel to use Python runtime
- Sets function memory to 3008 MB (maximum for better performance)
- Sets max duration to 60 seconds
- Routes all requests to the FastAPI app

### api/index.py
- Acts as the entry point for Vercel serverless functions
- Imports and exposes the FastAPI app from `main.py`

## Environment Variables

Set these in Vercel Dashboard or via CLI:

```bash
vercel env add GEMINI_API_KEY
vercel env add ALLOWED_ORIGINS
```

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Your Gemini API key | `AIza...` |
| `ALLOWED_ORIGINS` | Allowed CORS origins | `https://your-app.vercel.app,http://localhost:5173` |

## Testing Deployment

After deployment, test your endpoints:

1. **Health Check**:
   ```bash
   curl https://your-backend.vercel.app/health
   ```

2. **Root Endpoint**:
   ```bash
   curl https://your-backend.vercel.app/
   ```

3. **OCR Endpoint** (with a PDF file):
   ```bash
   curl -X POST https://your-backend.vercel.app/ocr \
     -F "file=@test.pdf"
   ```

## Important Notes

### Vercel Limitations

1. **Function Timeout**: Maximum 60 seconds for Hobby plan, 300 seconds for Pro
   - If processing takes longer, consider upgrading to Pro plan
   - Or split large PDFs into smaller batches

2. **Memory Limits**: Maximum 3008 MB
   - Configured to use max memory for PDF processing

3. **Cold Starts**: First request may be slower
   - Subsequent requests are faster
   - Consider keeping the function warm for production

### Poppler for pdf2image

Vercel doesn't have Poppler pre-installed, which is required for `pdf2image`. To fix this:

**Option A**: Use a custom build with poppler (requires vercel.json modification)
**Option B**: Switch to PyMuPDF (fitz) which works better on serverless:

```python
# Replace pdf2image with PyMuPDF in requirements.txt
PyMuPDF==1.23.8

# Update main.py:
import fitz  # PyMuPDF

def convert_pdf_to_images(pdf_bytes: bytes) -> List[Image.Image]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    doc.close()
    return images
```

## Updating Frontend to Use New Backend

Update your frontend's API URL to point to the Vercel backend:

```typescript
// In your frontend config
const API_URL = 'https://your-backend.vercel.app';
```

Or use environment variables:
```bash
# .env in frontend
VITE_API_URL=https://your-backend.vercel.app
```

## Troubleshooting

### Issue: "Module not found"
- Ensure all dependencies are in `requirements.txt`
- Check that `api/index.py` correctly imports from `main.py`

### Issue: "Function timeout"
- Increase `maxDuration` in `vercel.json` (requires Pro plan for > 60s)
- Or optimize your processing logic

### Issue: "CORS errors"
- Check `ALLOWED_ORIGINS` environment variable
- Ensure it includes your frontend URL

### Issue: "Poppler not found"
- Switch to PyMuPDF as described above

## Local Testing

Test the Vercel setup locally:

```bash
# Install Vercel CLI
npm install -g vercel

# Run locally
cd backend
vercel dev
```

This simulates the Vercel environment on your local machine.

## Monitoring

Monitor your deployment:
- **Logs**: Vercel Dashboard → Your Project → Logs
- **Analytics**: Vercel Dashboard → Your Project → Analytics
- **Health**: Regularly check `/health` endpoint

## Cost Considerations

**Vercel Hobby Plan (Free)**:
- 100 GB bandwidth/month
- 60 second function timeout
- Serverless function executions: 100 GB-hours

**Vercel Pro Plan ($20/month)**:
- 1 TB bandwidth/month
- 300 second function timeout
- More generous function execution limits

For production use with heavy OCR processing, consider the Pro plan.

## Next Steps

1. Deploy backend to Vercel
2. Update frontend API URL
3. Test all endpoints
4. Monitor performance
5. Set up custom domain (optional)

## Support

For issues:
- Check Vercel logs
- Review this documentation
- Consult [Vercel Python documentation](https://vercel.com/docs/functions/runtimes/python)

