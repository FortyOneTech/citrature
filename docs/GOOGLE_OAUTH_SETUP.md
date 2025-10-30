# Google OAuth Setup Guide

## Current Issue
The error `[GSI_LOGGER]: The given origin is not allowed for the given client ID` indicates that `http://localhost:3000` is not configured as an authorized origin in your Google Cloud Console.

## Fix Steps

### 1. Update Google Cloud Console OAuth Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services > Credentials**
3. Find your OAuth 2.0 Client ID: `381142452923-tvltaefohd0numj6fo9nc300ghc4tof5.apps.googleusercontent.com`
4. Click on it to edit
5. In the **Authorized JavaScript origins** section, add:
   - `http://localhost:3000`
   - `http://localhost:3000/` (with trailing slash)
6. In the **Authorized redirect URIs** section, ensure you have:
   - `http://localhost:8000/auth/google/callback`
7. Click **Save**

### 2. Collection Limit Issue

The 403 Forbidden error for collections is because the free plan is limited to 1 collection. You can:

**Option A: Increase the limit temporarily**
Update your `.env` file:
```
MAX_COLLECTIONS_PER_USER=10
```

**Option B: Delete existing collections**
If you have existing collections, you can delete them through the API or database.

### 3. Test the Fix

1. Restart your Docker containers:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

2. Clear your browser cache and cookies for localhost:3000

3. Try logging in again

## Expected Results

After these fixes:
- ✅ Google Sign-In button should work without origin errors
- ✅ Login should complete successfully
- ✅ Collection creation should work (if under the limit)
- ✅ No more CORS errors

## GCS Credentials Setup

For PDF upload functionality, you need to create a `credentials.json` file:

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Navigate to IAM & Admin > Service Accounts**
3. **Create a new service account** (or use existing one)
4. **Download the JSON key file**
5. **Rename it to `credentials.json`** and place it in the project root
6. **Update your `.env` file** with:
   ```
   GCS_BUCKET_NAME=your-bucket-name
   GCS_PROJECT_ID=your-project-id
   ```

## Troubleshooting

If you still see CORS errors:
1. Check that the backend is running on port 8000
2. Verify the CORS configuration in `citrature/main.py`
3. Clear browser cache completely

### PDF Upload Issues:
- Ensure `credentials.json` exists in the project root
- Verify GCS bucket exists and service account has access
- Check that the file is not a directory (should be a JSON file)