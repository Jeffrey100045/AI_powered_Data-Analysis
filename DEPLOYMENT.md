# Step-by-Step Deployment Guide - Kavi AI Analytics

This guide will walk you through deploying your application from scratch.

## Option 1: Local Deployment with Docker (Recommended)

This is the fastest way to get everything running in a controlled environment.

### Step 1: Install Docker
1. Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/).
2. Start Docker Desktop and wait for it to be "Running".

### Step 2: Prepare your Environment
1. Ensure you have a `.env` file in the `backend/` folder.
2. It must contain your API key:
   ```env
   GEMINI_API_KEY=your_actual_key_here
   ```

### Step 3: Launch the App
1. Open a terminal (PowerShell or Command Prompt) in the `kavi` folder.
2. Run the following command:
   ```bash
   docker compose up --build
   ```
3. Wait for the build to finish. Once you see logs like `Uvicorn running on http://0.0.0.0:8000`, the app is ready!

### Step 4: Access the App
- **Frontend**: Open `http://localhost` in your browser.
- **Backend API**: Accessible at `http://localhost:8000`.

---

## Option 2: Deploy to GitHub (Version Control)

**IMPORTANT**: I detected that `git` is currently NOT installed on your computer. You must install it first to run these commands.

1. **Install Git**: Download and install from [git-scm.com](https://git-scm.com/download/win).
2. **Open a New Terminal**: After installing, close your current terminal and open a new one (PowerShell) for the changes to take effect.
3. **Initialize and Push**:
   Run these commands one by one in the `kavi` folder:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: AI Analytics Platform with Docker"
   git branch -M main
   git remote add origin https://github.com/Jeffrey100045/AI_powered_Data-Analysis.git
   git push -u origin main
   ```

---

## Option 3: Deploy to Cloud (Render.com)

Render is great for hosting both your backend and frontend for free/cheap.

### Step 1: Deploy Backend
1. Sign up at [Render.com](https://render.com/).
2. Click **New +** > **Web Service**.
3. Connect your GitHub repository.
4. Settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 8000`
5. Add **Environment Variables**:
   - `GEMINI_API_KEY`: (Your key)
6. Click **Deploy**.

### Step 2: Deploy Frontend
1. Click **New +** > **Static Site**.
2. Connect the same GitHub repository.
3. Settings:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Publish Directory**: `dist`
4. Click **Deploy**.

---

## Troubleshooting
- **Port 80 is taken**: If `docker compose` fails because port 80 is in use, edit `docker-compose.yml` and change `"80:80"` to `"3000:80"`. Then visit `http://localhost:3000`.
- **API Connection Errors**: Ensure your frontend points to the correct backend URL.
