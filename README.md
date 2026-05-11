[![Views](https://visitor-badge.laobi.icu/badge?page_id=piyushdhoka.drdo_docxsummarizer)](https://visitor-badge.laobi.icu/badge?page_id=piyushdhoka.drdo_docxsummarizer)
# AI Document Summarizer with Database Integration

A powerful AI-powered document summarization system built with Streamlit, FastAPI, and Google Gemini AI. Now with **SQLite database integration** for storing and managing user summaries!

##  Features

- ** AI-Powered Summarization**: Uses Google Gemini AI for intelligent document analysis
- ** Multi-Format Support**: PDF, DOCX, TXT, HTML, and Markdown files
- ** Multiple Summary Styles**: Bullet points, Abstract, and Detailed summaries
- ** Database Storage**: SQLite database to save and retrieve user summaries
- ** Quality Analysis**: Automatic summary quality assessment and feedback
- ** Search & History**: Search through previous summaries and view history
- ** User Statistics**: Track your summarization usage and performance
- ** REST API**: FastAPI backend for programmatic access

## Quick Start (Windows PowerShell)

### Prerequisites
- Python 3.8+
- Google Gemini API key

### Setup

1. **Clone and navigate to the project**
   ```powershell
   cd drdo_docxsummarizer
   ```

2. **Create and activate virtual environment**
   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set up your API key**
   Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

5. **Start the services**
   ```powershell
   .\start_services.bat
   ```

## Database Features

### What Gets Stored
- **Summary content** and metadata
- **Document information** (name, type, size)
- **Processing metrics** (time, word counts)
- **Quality scores** and feedback
- **User identification** for history tracking

### Key Functions
- **Save summaries** automatically when generated
- **Retrieve user history** with pagination
- **Search summaries** by content or document name
- **User statistics** and analytics
- **Delete summaries** when no longer needed

## Usage

### Web Interface (Streamlit)
1. Open http://localhost:8501
2. Set your **User ID** in the sidebar
3. Upload a document or paste text
4. Choose summary style and generate
5. View your summary history and statistics

### API Endpoints (FastAPI)
- **POST** `/summarize-with-db` - Generate and save summary
- **GET** `/user/{user_id}/summaries` - Get user history
- **GET** `/user/{user_id}/statistics` - Get user stats
- **GET** `/user/{user_id}/search` - Search summaries
- **DELETE** `/user/{user_id}/summary/{id}` - Delete summary

##  Testing

Test the database functionality:
```powershell
python test_database.py
```
##  Project Structure

```
drdo_docxsummarizer/
├── app.py                 # Streamlit frontend
├── backend.py            # Core AI logic + database integration
├── database.py           # Database operations
├── fastapi_app.py        # REST API endpoints
├── requirements.txt      # Python dependencies
├── start_services.bat    # Service startup script
├── test_database.py      # Database testing
├── .env                  # API key configuration
└── utils/                # File processing utilities
    ├── file_reader.py    # Document text extraction
    └── pdf_reader.py     # PDF-specific processing
```

##  Configuration

### Environment Variables
- `GEMINI_API_KEY` - Your Google Gemini API key (required)

### Database Settings
- Database file: `summaries.db` (auto-created)
- Location: Project root directory
- Backup: Copy the `.db` file to preserve data

##  Manual Service Startup

If you prefer to start services manually:

**Streamlit UI:**
```powershell
venv\Scripts\Activate.ps1
streamlit run app.py
```

**FastAPI Server:**
```powershell
venv\Scripts\Activate.ps1
uvicorn fastapi_app:app --reload --host 0.0.0.0 --port 8000
```

##  API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## What's New

### Database Integration
- ✅ Automatic summary storage
- ✅ User history and search
- ✅ Quality metrics tracking
- ✅ Performance analytics
- ✅ Summary management (view/delete)

### Enhanced API
- ✅ Database-aware endpoints
- ✅ User-specific operations
- ✅ Comprehensive metadata
- ✅ Error handling and validation

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

##  License

This project is open source and available under the MIT License.

---

