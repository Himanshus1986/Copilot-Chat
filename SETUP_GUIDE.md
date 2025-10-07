# 🚀 Fixed Enterprise Assistant Setup Guide

## 🔧 The Problem & Solution

**Problem:** You were getting "405 Method Not Allowed" error because:
1. Both APIs were trying to run on the same port (8000)
2. CORS (Cross-Origin Resource Sharing) wasn't configured
3. Browser was sending OPTIONS preflight requests

**Solution:** I've fixed all these issues:
✅ Separated APIs to different ports
✅ Added CORS middleware to both APIs  
✅ Enhanced error handling in frontend
✅ Proper API endpoint configuration

## 📂 Files Fixed

### Frontend Files:
- `copilot-index-fixed.html` - Main HTML file
- `copilot-script-fixed.js` - **FIXED JavaScript with proper API calls**
- `copilot-style.css` - CSS (unchanged, but use existing one)

### Backend Files:  
- `TimeSheet_api_fixed.py` - Timesheet API with CORS (Port 8000)
- `RAG_api_fixed.py` - HR Policy API with CORS (Port 8001)

## 🚀 Setup Instructions

### Step 1: Start the APIs

**Terminal 1 - Timesheet API:**
```bash
python TimeSheet_api_fixed.py
```
✅ Should start on: http://localhost:8000

**Terminal 2 - HR Policy API:**
```bash  
python RAG_api_fixed.py
```
✅ Should start on: http://localhost:8001

### Step 2: Upload HR Policy Documents
```bash
# Upload PDFs to HR Policy API first
curl -X POST "http://localhost:8001/upload_pdfs" \
     -F "files=@your_policy.pdf"
```

### Step 3: Start Frontend
```bash
# Open the fixed HTML file
python -m http.server 8080

# Then visit: http://localhost:8080/copilot-index-fixed.html
```

## 🔍 Key Fixes Made

### 1. API Configuration (JavaScript)
```javascript
// BEFORE (Wrong - both on 8000)
const API_CONFIG = {
    'hr-policy': {
        baseUrl: 'http://localhost:8000', // ❌ Wrong port
        endpoint: '/query'
    }
};

// AFTER (Fixed - separated ports)  
const API_CONFIG = {
    timesheet: {
        baseUrl: 'http://localhost:8000', // ✅ Timesheet API
        endpoint: '/chat'
    },
    'hr-policy': {
        baseUrl: 'http://localhost:8001', // ✅ HR Policy API  
        endpoint: '/query'
    }
};
```

### 2. CORS Headers (Backend APIs)
```python
# Added to both APIs:
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

### 3. Enhanced Error Handling (Frontend)
```javascript  
// Better error messages for different scenarios
if (error.message.includes('CORS')) {
    errorMsg = 'Connection issue - please ensure APIs are running with CORS configured.';
} else if (error.message.includes('405')) {
    errorMsg = 'Method not allowed - check API endpoint configuration.';
}
```

## 🧪 Testing the Fix

### Test Timesheet API:
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","user_prompt":"help with timesheet"}'
```

### Test HR Policy API:  
```bash
curl -X POST "http://localhost:8001/query" \
     -H "Content-Type: application/json" \
     -d '{"question":"What is the vacation policy?"}'
```

## 🔥 What's Different Now

### ✅ Fixed Issues:
1. **Port Separation**: Timesheet (8000) + HR Policy (8001)
2. **CORS Support**: Both APIs handle cross-origin requests
3. **Better Error Messages**: Clear feedback on connection issues
4. **Enhanced Logging**: Better debugging information
5. **Proper Payloads**: Correct JSON structure for each API

### 🎯 Key Features:
- **Email Validation**: Required before service access
- **Service Persistence**: Remembers your choice throughout session
- **Reset Function**: Easy return to welcome screen  
- **Error Recovery**: Handles API failures gracefully
- **Mobile Responsive**: Works on all devices

## 🐛 Troubleshooting

### If you still get errors:

1. **Check API Status:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8001/health  
   ```

2. **Verify CORS Headers:**
   - Open browser dev tools (F12)
   - Check Network tab for failed requests
   - Look for CORS errors in Console

3. **Test API Endpoints:**
   - Use the curl commands above
   - Check if APIs respond correctly

4. **Browser Cache:**
   - Clear browser cache
   - Hard refresh (Ctrl+Shift+R)

## 🎉 Ready to Use!

Once both APIs are running:
1. Open `copilot-index-fixed.html` in browser
2. Enter your email
3. Select Timesheet or HR Policy service  
4. Start chatting!

The "405 Method Not Allowed" error should be completely resolved now! 🚀
