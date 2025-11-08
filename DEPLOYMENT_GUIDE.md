# 🚀 Deployment Guide for English OCR App

## ✅ What's Been Done

Your repository has been fully prepared for deployment! Here's what was configured:

### 1. **Backend (Render) Configuration** ✅
- Created `render.yaml` for automatic Render deployment
- Created `backend/runtime.txt` to specify Python 3.11
- Updated CORS configuration to accept environment-based origins
- Created `backend/env.template` for environment variable reference

### 2. **Frontend (Vercel) Configuration** ✅
- Created `vercel.json` for Vercel deployment
- Updated frontend to use environment variables for API URL
- Created `frontend/env.template` for environment variable reference

### 3. **Git & GitHub** ✅
- Initialized git repository
- Added comprehensive `.gitignore` files
- Committed all code with proper structure
- Pushed to GitHub: https://github.com/abhijit-aiplanet/English_OCR

### 4. **Documentation** ✅
- Updated README.md with complete deployment instructions
- Created environment variable templates
- Added troubleshooting guides

---

## 📋 Next Steps: Deploy Your App

### Step 1: Deploy Backend on Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select repository: `abhijit-aiplanet/English_OCR`
   
3. **Configure Service**:
   ```
   Name: english-ocr-backend
   Runtime: Python 3
   Build Command: pip install -r backend/requirements.txt
   Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add Environment Variables**:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `ALLOWED_ORIGINS`: `http://localhost:3000,http://localhost:5173` (update after Vercel deployment)
   
5. **Deploy!** 
   - Click "Create Web Service"
   - Wait for deployment (takes ~2-3 minutes)
   - **Copy your backend URL**: e.g., `https://english-ocr-backend.onrender.com`

### Step 2: Deploy Frontend on Vercel

1. **Go to Vercel Dashboard**: https://vercel.com/new
2. **Import Repository**:
   - Click "Add New..." → "Project"
   - Import from GitHub: `abhijit-aiplanet/English_OCR`
   
3. **Configure Project**:
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   ```

4. **Add Environment Variable**:
   - Key: `VITE_API_URL`
   - Value: Your Render backend URL (from Step 1)
   - Example: `https://english-ocr-backend.onrender.com`
   
5. **Deploy!**
   - Click "Deploy"
   - Wait for deployment (takes ~1-2 minutes)
   - **Copy your frontend URL**: e.g., `https://your-app.vercel.app`

### Step 3: Update Backend CORS

1. **Go back to Render Dashboard**
2. **Update Environment Variable**:
   - Edit `ALLOWED_ORIGINS`
   - New value: `https://your-vercel-app.vercel.app,http://localhost:3000,http://localhost:5173`
   - Replace `your-vercel-app` with your actual Vercel domain
   
3. **Redeploy Backend**:
   - Render will automatically redeploy with new settings

---

## 🎉 Your App is Live!

- **Frontend URL**: `https://your-app.vercel.app`
- **Backend URL**: `https://english-ocr-backend.onrender.com`
- **GitHub Repo**: https://github.com/abhijit-aiplanet/English_OCR

---

## 📝 Important Notes

### Render Free Tier
- Spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds to wake up
- Consider upgrading for production use

### Vercel Free Tier
- Fast and reliable
- Automatically rebuilds on GitHub pushes
- Custom domains available even on free tier

### Environment Variables Needed

**Backend (Render)**:
```env
GEMINI_API_KEY=your_gemini_api_key_here
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
```

**Frontend (Vercel)**:
```env
VITE_API_URL=https://your-render-backend.onrender.com
```

---

## 🔧 Troubleshooting

### CORS Errors
- Make sure `ALLOWED_ORIGINS` in Render includes your Vercel URL
- Ensure no trailing slashes in URLs
- Redeploy backend after updating CORS settings

### API Not Responding
- Check if Render service is sleeping (first request takes longer)
- Verify environment variables are set correctly
- Check backend logs in Render dashboard

### Build Failures

**Backend (Render)**:
- Ensure `backend/requirements.txt` is present
- Check Python version in `backend/runtime.txt`
- Review build logs in Render dashboard

**Frontend (Vercel)**:
- Ensure `frontend/package.json` is present
- Verify root directory is set to `frontend`
- Check build logs in Vercel dashboard

---

## 🔄 Continuous Deployment

Both Render and Vercel are configured for automatic deployments:
- **Push to GitHub** → Both services automatically rebuild and deploy
- Backend and frontend stay in sync with your repository
- No manual deployment needed after initial setup

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)

---

## 🆘 Need Help?

1. Check the console logs (browser for frontend, Render dashboard for backend)
2. Review the environment variables
3. Ensure all dependencies are installed correctly
4. Check GitHub repository for latest code

---

**Happy Deploying! 🚀**

