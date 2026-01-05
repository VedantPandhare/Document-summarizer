import streamlit as st
import tempfile
import os
from datetime import datetime
from backend import summarize_text, evaluate_summary_quality
from utils.file_reader import extract_text_from_file, get_file_info, get_supported_formats

# Page configuration
st.set_page_config(
    page_title="AI Document Summarizer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, bold styling
st.markdown("""
<style>
    /* Modern color scheme */
    :root {
        --primary-color: #6366f1;
        --primary-dark: #4f46e5;
        --secondary-color: #f59e0b;
        --success-color: #10b981;
        --error-color: #ef4444;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --bg-primary: #ffffff;
        --bg-secondary: #f9fafb;
        --border-color: #e5e7eb;
    }
    
    /* Global styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Modern header */
    .main-header {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 500;
    }
    

    
    /* File info display */
    .file-info {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 2px solid var(--primary-color);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.15);
        transition: all 0.3s ease;
    }
    
    .file-info:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(99, 102, 241, 0.25);
    }
    
    .file-info::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    .file-info .file-icon {
        font-size: 2.5rem;
        color: var(--primary-color);
        flex-shrink: 0;
    }
    
    .file-info .file-details {
        flex: 1;
    }
    
    .file-info .file-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.4rem;
        display: block;
    }
    
    .file-info .file-meta {
        color: var(--text-secondary);
        font-size: 0.85rem;
        line-height: 1.4;
    }
    
    .file-info .file-meta span {
        display: inline-block;
        margin-right: 0.75rem;
        padding: 0.2rem 0.6rem;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.8rem;
    }
    

    
    /* Summary box */
    .summary-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 2px solid var(--primary-color);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        position: relative;
    }
    
    .summary-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--success-color), var(--primary-color));
    }
    
    /* Status boxes */
    .success-box {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 2px solid var(--success-color);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .error-box {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 2px solid var(--error-color);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    

    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
    }
    

    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
    }
    
    /* Progress indicators */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    

</style>
""", unsafe_allow_html=True)

def main():
    # Header with modern design
    st.markdown('<h1 class="main-header">🚀 AI Document Summarizer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform any document into intelligent summaries with cutting-edge AI</p>', unsafe_allow_html=True)
    
    # Initialize session state for user
    if 'username' not in st.session_state:
        st.session_state.username = "guest"
    
    # Initialize authenticated state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Sidebar for settings
    with st.sidebar:
        # Login section
        st.header("👤 Login")
        if not st.session_state.authenticated:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            # Simple authentication (in a real app, use secure authentication)
            if st.button("Login", key="login_button"):
                if username and password:  # Simple check - in real app use proper auth
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Please enter both username and password")
        else:
            st.success(f"Logged in as {st.session_state.username}")
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.username = "guest"
                st.rerun()
        
        st.markdown("---")
        st.header("📝 Input Method")
        input_method = st.radio(
            "Choose how to provide your document:",
            ["📁 Upload Document", "✏️ Paste Text"],
            index=0
        )
        
        st.markdown("---")
        st.markdown("### 🎯 Summary Style")
        summary_style = st.selectbox(
            "Select summary format:",
            ["Bullet Points", "Abstract", "Detailed"],
            help="Bullet Points: Key points in bullet format\nAbstract: 3-4 line summary\nDetailed: Comprehensive narrative summary"
        )
        
        # Style mapping
        style_mapping = {
            "Bullet Points": "bullet",
            "Abstract": "abstract", 
            "Detailed": "detailed"
        }
        
        st.markdown("---")
        st.markdown("### 📁 Supported Formats")
        supported_formats = get_supported_formats()
        for ext, desc in supported_formats.items():
            st.markdown(f"**{ext.upper()}** - {desc}")
        
    
    # Show main app
    show_main_app(input_method, summary_style, style_mapping)

# Login message function removed

def show_main_app(input_method, summary_style, style_mapping):
    """Show main application for authenticated users."""
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    # Initialize input_text variable
    input_text = ""
    
    with col1:
        st.header("📥 Input Document")
        
        if input_method == "📁 Upload Document":
            # Get supported file types
            supported_formats = get_supported_formats()
            file_types = list(supported_formats.keys())
            
            # Create a compact upload area
            st.markdown("""
                <div style="
                    border: 2px dashed #6366f1;
                    border-radius: 12px;
                    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                    padding: 1.5rem;
                    text-align: center;
                    margin: 1rem 0;
                    transition: all 0.3s ease;
                ">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📁</div>
                    <div style="font-size: 1rem; font-weight: 600; color: #1f2937; margin-bottom: 0.25rem;">
                        Drop your document here
                    </div>
                    <div style="color: #6b7280; font-size: 0.85rem;">
                        PDF, DOCX, TXT, HTML, Markdown
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Choose a document file",
                type=file_types,
                help=f"Upload a document to extract and summarize. Supported formats: {', '.join(file_types).upper()}",
                label_visibility="collapsed"  # Hide the default label
            )
            
            if uploaded_file is not None:
                # Check file size (limit to 50MB)
                file_size_bytes = len(uploaded_file.getvalue())
                file_size_mb = file_size_bytes / (1024 * 1024)
                if file_size_mb > 50:
                    st.error(f"❌ File too large! Maximum size is 50MB. Your file is {file_size_mb:.1f}MB")
                    return
                # Display file info with custom styling
                # Create a temporary file first to get proper file info
                file_ext = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Get file info from the temporary file
                file_info = get_file_info(tmp_path)
                if not file_info:
                    st.error("❌ Failed to read file information. Please try with a different file.")
                    os.unlink(tmp_path)
                    return
                
                # Check if file type is supported
                if not file_info.get('supported', False):
                    st.error(f"❌ File type '{file_info.get('file_type', 'unknown')}' is not supported. Please use PDF, DOCX, TXT, HTML, or Markdown files.")
                    os.unlink(tmp_path)
                    return
                
                # Get appropriate file icon
                file_icon = "📄"  # Default
                if file_info['file_type'] == 'pdf':
                    file_icon = "📄"
                elif file_info['file_type'] == 'docx':
                    file_icon = "📝"
                elif file_info['file_type'] == 'txt':
                    file_icon = "📜"
                elif file_info['file_type'] == 'html':
                    file_icon = "🌐"
                elif file_info['file_type'] == 'markdown':
                    file_icon = "📝"
                
                # Create beautiful file display
                st.markdown(f'''
                    <div class="file-info">
                        <div class="file-icon">{file_icon}</div>
                        <div class="file-details">
                            <span class="file-name">{file_info['file_name']}</span>
                                                            <div class="file-meta">
                                    <span>{file_info['file_type'].upper()}</span>
                                    <span>{file_info['file_size_mb'] if file_info['file_size_mb'] >= 0.01 else '< 0.01'} MB</span>
                                    {f'<span>{file_info["page_count"]} pages</span>' if 'page_count' in file_info and file_info["page_count"] else ''}
                                    {f'<span>{file_info["extractor"]}</span>' if 'extractor' in file_info and file_info["extractor"] else ''}
                                </div>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
                

                
                # Extract text from file with loading state
                try:
                    with st.spinner("🔍 Extracting text from your document..."):
                        extracted_text = extract_text_from_file(tmp_path)
                    
                    # Clean up temporary file
                    os.unlink(tmp_path)
                    
                    if extracted_text.startswith("Error") or extracted_text.startswith("Warning"):
                        st.markdown(f'''
                            <div class="error-box">
                                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                    <span style="font-size: 1.5rem;">⚠️</span>
                                    <span style="font-weight: 600; font-size: 1.1rem;">Document Processing Error</span>
                                </div>
                                <div style="color: #dc2626; font-size: 0.95rem;">{extracted_text}</div>
                            </div>
                        ''', unsafe_allow_html=True)
                        return
                except Exception as e:
                    # Clean up temporary file on error
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                    st.error(f"❌ An error occurred while processing the file: {str(e)}")
                    return
                
                # Show success message with animation
                st.markdown(f'''
                    <div class="success-box">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 1.5rem;">✅</span>
                            <span style="font-weight: 600; font-size: 1.1rem;">Text Extracted Successfully!</span>
                        </div>
                        <div style="color: #059669; font-size: 0.95rem;">
                            Extracted {len(extracted_text.split())} words from your document.
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
                
                # Store file information in session state for database storage
                st.session_state['document_name'] = file_info['file_name']
                st.session_state['document_type'] = file_info['file_type']
                st.session_state['file_size'] = file_size_bytes
                
                # Display extracted text in a text area for review
                st.markdown("### 📝 Extracted Text Preview")
                st.text_area(
                    "Review the extracted text before summarization",
                    value=extracted_text,
                    height=200,
                    help="This is the text that will be summarized. You can edit it if needed."
                )
                
                # Update the input text for summarization
                input_text = extracted_text
                
        else:  # Paste Text
            input_text = st.text_area(
                "Paste your text here:",
                height=300,
                placeholder="Enter or paste the text you want to summarize...",
                help="Paste any text content you want to summarize"
            )
        
            # Store document information for pasted text
            if input_text and input_text.strip():
                st.session_state['document_name'] = 'Pasted Text'
                st.session_state['document_type'] = 'text'
                st.session_state['file_size'] = len(input_text.encode('utf-8'))
        
        # Summarize button
        if input_text and input_text.strip():
            if st.button("🚀 Generate Summary", type="primary", use_container_width=True):
                # Check if user is authenticated
                if not st.session_state.authenticated:
                    st.error("⚠️ Please login to generate summaries")
                    st.info("👈 Use the login form in the sidebar")
                else:
                    with st.spinner("🤖 AI is analyzing your document..."):
                        try:
                            # Get user ID for database storage (use username)
                            user_id = st.session_state.username
                            document_name = st.session_state.get('document_name', 'Pasted Text')
                            document_type = st.session_state.get('document_type', 'text')
                            file_size = st.session_state.get('file_size', None)
                            
                            # Generate summary and save to database
                            from backend import summarize_text_with_db
                            result = summarize_text_with_db(
                                text=input_text,
                                style=style_mapping[summary_style],
                                user_id=user_id,
                                document_name=document_name,
                                document_type=document_type,
                                file_size=file_size
                            )
                            
                            if result['success']:
                                summary = result['summary']
                                # Store summary in session state for download
                                st.session_state['current_summary'] = summary
                                st.session_state['summary_style'] = summary_style
                                st.session_state['timestamp'] = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                                st.session_state['summary_id'] = result.get('summary_id')
                                
                                # Store quality metrics
                                st.session_state['quality_metrics'] = result.get('quality_metrics', {})
                                
                                # Show success message with database and file info
                                success_message = "✅ Summary generated successfully!"
                                
                                if result.get('summary_id'):
                                    success_message += f" Saved to database (ID: {result['summary_id']})."
                                
                                if result.get('file_path'):
                                    # Store file path in session state
                                    st.session_state['summary_file_path'] = result['file_path']
                                    file_dir = os.path.dirname(result['file_path'])
                                    success_message += f" Saved to folder: {file_dir}"
                                
                                st.success(success_message)
                                    
                                # Show warning if database save failed
                                if result.get('warning'):
                                    st.warning(f"⚠️ {result['warning']}")
                            else:
                                st.error(f"❌ {result.get('error', 'An error occurred')}")
                        except Exception as e:
                            st.error(f"❌ An error occurred: {str(e)}")
        elif input_method == "✏️ Paste Text":
            st.info("ℹ️ Please paste some text to summarize.")
    
    with col2:
        st.header("📋 Generated Summary")
        
        if 'current_summary' in st.session_state:
            # Display summary
            st.markdown(f'''
                <div class="summary-box">
                    <div style="margin-bottom: 1rem;">
                        <strong>Style:</strong> {st.session_state['summary_style']}<br>
                        <strong>Generated:</strong> {st.session_state['timestamp']}
                    </div>
                    <hr style="border: 1px solid #e0f2fe; margin: 1rem 0;">
                    <div style="line-height: 1.6; color: #1f2937;">
                        {st.session_state['current_summary']}
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            
            # Quality metrics section removed
            
            # Download button
            st.markdown("---")
            st.markdown("### 💾 Download Summary")
            
            # Create download filename
            filename = f"summary_{st.session_state['summary_style'].replace(' ', '_').lower()}_{st.session_state['timestamp']}.txt"
            
            # Download button
            st.download_button(
                label="📥 Download as TXT",
                data=st.session_state['current_summary'],
                file_name=filename,
                mime="text/plain",
                use_container_width=True
            )
            
            # Copy to clipboard button
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                st.write("📋 Summary copied to clipboard!")
                st.code(st.session_state['current_summary'])
                
            # Open file location button removed as requested
        else:
            st.info("ℹ️ Upload a document or paste text, then click 'Generate Summary' to see results here.")
    
    # User History Section - only show if authenticated
    if st.session_state.authenticated:
        st.markdown("---")
        st.markdown("### 📚 Your Summary History")
        
        # Use username from session state
        user_id = st.session_state.username
        
        # Load and display user history
        try:
            from backend import get_user_summary_history, get_user_statistics
            
            # Get user statistics
            stats = get_user_statistics(user_id)
            
            # Display statistics
            st.markdown("#### 📊 Your Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Summaries", stats['total_summaries'])
            with col2:
                st.metric("Documents Processed", stats['total_documents'])
            with col3:
                st.metric("Avg Quality Score", f"{stats['average_quality']}/100")
            with col4:
                st.metric("Total Words", f"{stats['total_words_processed']:,}")
            
            # Get recent summaries
            summaries = get_user_summary_history(user_id, limit=10)
            
            if summaries:
                st.markdown("#### 📝 Recent Summaries")
                
                for summary in summaries:
                    with st.expander(f"📄 {summary['document_name']} ({summary['document_type']}) - {summary['created_at'][:10]}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**Style:** {summary['summary_style']}")
                            if summary['quality_score']:
                                score_color = "#10b981" if summary['quality_score'] >= 80 else "#f59e0b" if summary['quality_score'] >= 60 else "#ef4444"
                                st.markdown(f"**Quality Score:** <span style='color: {score_color}; font-weight: bold;'>{summary['quality_score']}/100</span>", unsafe_allow_html=True)
                            
                            st.markdown("**Summary:**")
                            st.text_area("", value=summary['summary'], height=150, key=f"summary_{summary['id']}", disabled=True)
                            
                            if summary['word_count']:
                                st.caption(f"Original: {summary['word_count']} words | Summary: {summary['summary_word_count']} words")
                        
                        with col2:
                            if st.button("🗑️ Delete", key=f"delete_{summary['id']}"):
                                from backend import delete_user_summary
                                if delete_user_summary(summary['id'], user_id):
                                    st.success("Summary deleted!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete summary")
            else:
                st.info("📚 No summaries found. Start by generating your first summary!")
                
        except Exception as e:
            st.error(f"Error loading history: {str(e)}")
            st.info("Make sure the database is properly initialized and accessible.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: var(--text-secondary); font-weight: 500;'>"
        "🚀 Built with cutting-edge AI technology using Streamlit and Google Gemini"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
