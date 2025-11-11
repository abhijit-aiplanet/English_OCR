# Deploying to Vercel

This guide explains how to deploy both the frontend and backend of the Handwritten Form OCR application to Vercel.

## Overview

The application will be deployed as a single Vercel project with:
- **Backend**: Python serverless functions in the `/api` directory
- **Frontend**: React/Vite static site in the `/frontend` directory

## Prerequisites

1. GitHub account with your code pushed to a repository
2. Vercel account (sign up at https://vercel.com)
3. Gemini API key from Google AI Studio

## Deployment Steps

### 1. Push Code to GitHub

Make sure all your code is committed and pushed to GitHub:

```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 2. Import Project to Vercel

1. Go to https://vercel.com and log in
2. Click **"Add New..." → "Project"**
3. Import your GitHub repository
4. Vercel will automatically detect the configuration from `vercel.json`

### 3. Configure Environment Variables

In the Vercel project settings, add the following environment variable:

**Environment Variable:**
- **Key**: `GEMINI_API_KEY`
- **Value**: Your Gemini API key (e.g., `AIzaSy...`)
- **Scope**: Production, Preview, Development (all environments)

**How to add:**
1. Go to your Vercel project dashboard
2. Click **Settings → Environment Variables**
3. Add the variable
4. Click **Save**

### 4. Deploy

Click **"Deploy"** and Vercel will:
1. Install Python dependencies from `requirements.txt`
2. Build the FastAPI backend as serverless functions
3. Install Node.js dependencies and build the React frontend
4. Deploy everything to a global CDN

### 5. Access Your Application

After deployment completes:
- Your app will be live at: `https://your-project-name.vercel.app`
- Backend API endpoints: `https://your-project-name.vercel.app/api/...`
- Frontend: `https://your-project-name.vercel.app`

## API Endpoints

Once deployed, your API will be available at:

- `GET /` - Root endpoint
- `GET /api` - API root
- `POST /api/ocr` - OCR processing (non-streaming)
- `POST /api/ocr/stream` - OCR processing (streaming)
- `GET /api/health` - Health check

**Note**: Both `/api/ocr/stream` and `/ocr/stream` routes are supported for backward compatibility.

## Configuration Details

### vercel.json

The `vercel.json` file configures:
- **Builds**: Both Python backend and Node.js frontend
- **Routes**: API requests to `/api/*` go to Python functions, everything else to the frontend
- **Functions**: Increased memory (3GB) and timeout (5 minutes) for OCR processing

### Requirements

Python dependencies are listed in `requirements.txt`:
- `fastapi` - Web framework
- `mangum` - ASGI adapter for AWS Lambda/Vercel
- `python-multipart` - File upload handling
- `Pillow` - Image processing
- `pdf2image` - PDF conversion
- `google-genai` - Gemini API client
- `uvicorn` - ASGI server

## Environment Variables

### Backend (Vercel Environment Variables)

Required:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Optional:
```env
ALLOWED_ORIGINS=*
```

### Frontend

The frontend automatically uses relative paths when deployed on Vercel (same domain as backend), so no environment variables are needed in production. For local development, you can set:

```env
VITE_API_URL=http://localhost:8000
```

## Troubleshooting

### Build Failures

**Python Dependencies Issue:**
- Ensure all dependencies in `requirements.txt` are compatible with Vercel's Python runtime
- Vercel supports Python 3.9

**Frontend Build Issue:**
- Check that `package.json` has correct build scripts
- Ensure all Node.js dependencies are in `package.json`

### Runtime Errors

**API Key Not Found:**
- Verify `GEMINI_API_KEY` is set in Vercel Environment Variables
- Redeploy after adding environment variables

**Timeout Errors:**
- Large PDFs may hit the 300-second timeout limit
- Consider upgrading to Vercel Pro for longer timeouts
- Or process fewer pages at once

**Memory Issues:**
- Default is 3008MB (configured in `vercel.json`)
- For very large PDFs, you may need Vercel Pro for more memory

### CORS Issues

The backend is configured to accept requests from any origin (`*`) by default. If you need to restrict this:

1. Set `ALLOWED_ORIGINS` environment variable in Vercel
2. List allowed domains: `https://yourdomain.com,https://anotherdomain.com`

## Performance Considerations

### Cold Starts
- Serverless functions may have cold starts (~2-5 seconds)
- First request after inactivity will be slower
- Subsequent requests are fast

### Processing Time
- Each PDF page takes ~2-5 seconds to process
- Processing happens sequentially, page by page
- A 10-page PDF will take ~20-50 seconds total

### API Limits
- **Gemini API**: Monitor your quota (each page = 1 API call)
- **Vercel Function Timeout**: 300 seconds (5 minutes) max
- **Vercel Function Memory**: 3008 MB (configured)

## Cost Considerations

### Vercel Free Tier Includes:
- ✅ Unlimited deployments
- ✅ 100 GB-hours of function execution per month
- ✅ Automatic HTTPS
- ✅ Global CDN

### Gemini API:
- Check current pricing at https://ai.google.dev/pricing
- Free tier typically includes generous quotas
- Monitor usage to stay within limits

## Monitoring

### View Logs
1. Go to your Vercel project dashboard
2. Click **"Deployments"**
3. Select a deployment
4. Click **"Functions"** tab to see serverless function logs

### Performance
- Monitor function execution time in Vercel dashboard
- Track API usage in Google AI Studio console

## Updating Your Application

Vercel automatically redeploys when you push to your GitHub repository:

```bash
git add .
git commit -m "Update application"
git push origin main
```

Vercel will:
1. Detect the push
2. Automatically build and deploy
3. Update your live site (usually within 1-2 minutes)

## Custom Domain

To use a custom domain:

1. Go to **Settings → Domains** in Vercel
2. Add your domain
3. Configure DNS records as instructed
4. Vercel provides automatic HTTPS

## Support

- **Vercel Documentation**: https://vercel.com/docs
- **Vercel Support**: https://vercel.com/support
- **Gemini API Docs**: https://ai.google.dev/docs

## Migration from Render

If you were previously using Render for the backend:

1. ✅ No code changes needed - the app now works on Vercel
2. ✅ Update any frontend environment variables to point to Vercel
3. ✅ Transfer `GEMINI_API_KEY` to Vercel Environment Variables
4. ✅ Decommission your Render backend service (optional, to save resources)

The main advantages of Vercel over Render for this application:
- **Faster cold starts**: Vercel's Python functions start quicker
- **Better frontend integration**: Same platform, same domain
- **Simpler deployment**: One platform instead of two
- **Better reliability**: Global CDN and redundant infrastructure

## Differences from Render

| Aspect | Render | Vercel |
|--------|--------|--------|
| Architecture | Always-on server | Serverless functions |
| Cold starts | None (if paid) | Yes (~2-5s) |
| Scaling | Manual/Auto | Automatic |
| Timeout | 10+ minutes | 5 minutes (configurable) |
| Setup | Separate services | Single project |
| Domain | Separate domains | Single domain |

## Security

- Environment variables are encrypted and secure
- HTTPS is automatic for all deployments
- API keys are never exposed to the frontend
- CORS is configured to prevent unauthorized access

## Next Steps

After successful deployment:

1. ✅ Test the application thoroughly
2. ✅ Set up custom domain (optional)
3. ✅ Configure monitoring and alerts
4. ✅ Share your application URL

Your app is now live on Vercel! 🎉

