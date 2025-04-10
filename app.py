import streamlit as st
import os
import tempfile
import base64
from pdf_processor import extract_text_from_pdf
from text_comparison import compare_texts, generate_summary
from utils import highlight_differences, display_summary, create_navigation_buttons
from export_utils import export_as_html, export_as_pdf

# Set page configuration
st.set_page_config(
    page_title="PDF Comparison Tool",
    page_icon="📑",
    layout="wide"
)

# Custom CSS to enhance UI
def apply_custom_css():
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        position: relative;
    }
    h1 {
        color: #FF4081;
        font-size: 3.5rem !important;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    h2 {
        color: #553BFF;
        font-size: 2.2rem !important;
        margin-top: 2rem;
        border-bottom: 2px solid #FFECFD;
        padding-bottom: 0.5rem;
    }
    h3 {
        color: #0CA4A5;
        font-size: 1.5rem !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0px 0px;
        font-weight: 500;
        background-color: #f9f9f9;
        border-left: 1px solid #ccc;
        border-right: 1px solid #ccc;
        border-top: 1px solid #ccc;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4081 !important;
        color: white !important;
    }
    .stButton button {
        background-color: #FF4081;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        border: none;
        box-shadow: 0px 3px 5px rgba(0,0,0,0.1);
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: #E5004E;
        box-shadow: 0px 5px 8px rgba(0,0,0,0.2);
    }
    div.stFileUploader > div[data-baseweb="file-uploader"] {
        border: 2px dashed #FF4081;
        border-radius: 10px;
        background-color: #FFECFD;
        padding: 20px;
    }
    div.stFileUploader [data-testid="stMarkdownContainer"] p {
        color: #777;
        font-size: 1rem;
    }
    .company-logo {
        position: absolute;
        top: 10px;
        right: 20px;
        font-size: 16px;
        z-index: 1000;
        display: flex;
        align-items: center;
        background: linear-gradient(45deg, #FF4081, #553BFF);
        padding: 8px 16px;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .company-logo::before {
        content: "🧠";
        margin-right: 8px;
        font-size: 22px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Add the company logo at the top right
    st.markdown("""
    <div class="company-logo">Ideasouq Technologies</div>
    """, unsafe_allow_html=True)

def main():
    apply_custom_css()
    
    # Header with animated title
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1><span style="color:#FF4081">📑</span> PDF Comparison Tool <span style="color:#FF4081">📑</span></h1>
        <p style="font-size: 1.2rem; color: #666; max-width: 600px; margin: 0 auto;">
            An interactive tool to visualize differences between PDF documents with colorful highlighting.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a colorful info box
    st.markdown("""
    <div style="background-color: #f0f7ff; padding: 20px; border-radius: 10px; border-left: 5px solid #553BFF; margin-bottom: 30px;">
        <h3 style="color: #553BFF; margin-top: 0;">How It Works</h3>
        <p>Upload two PDF documents to compare them and see the differences highlighted:</p>
        <div style="display: flex; margin-top: 15px;">
            <div style="background-color: #CCFFCC; padding: 5px 10px; margin-right: 15px; border-radius: 5px;">
                <strong>Added content</strong>
            </div>
            <div style="background-color: #FFCCCC; padding: 5px 10px; margin-right: 15px; border-radius: 5px;">
                <strong>Removed content</strong>
            </div>
            <div style="background-color: #FFFFCC; padding: 5px 10px; border-radius: 5px;">
                <strong>Modified content</strong>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload section with better styling
    st.markdown("<h2>Upload Your Documents</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("First PDF")
        pdf1 = st.file_uploader("Upload the first PDF", type=['pdf'], key="pdf1")
        
    with col2:
        st.subheader("Second PDF")
        pdf2 = st.file_uploader("Upload the second PDF", type=['pdf'], key="pdf2")
    
    # Process the PDFs when both are uploaded
    if pdf1 and pdf2:
        with st.spinner("🔄 Processing PDFs... Please wait"):
            # Save uploaded files to temp directory
            temp_dir = tempfile.TemporaryDirectory()
            pdf1_path = os.path.join(temp_dir.name, "pdf1.pdf")
            pdf2_path = os.path.join(temp_dir.name, "pdf2.pdf")
            
            with open(pdf1_path, "wb") as f:
                f.write(pdf1.getvalue())
            
            with open(pdf2_path, "wb") as f:
                f.write(pdf2.getvalue())
            
            # Extract text from PDFs
            try:
                text1 = extract_text_from_pdf(pdf1_path)
                text2 = extract_text_from_pdf(pdf2_path)
                
                if not text1.strip():
                    st.error("Could not extract text from the first PDF. It might be a scanned document or protected.")
                    return
                
                if not text2.strip():
                    st.error("Could not extract text from the second PDF. It might be a scanned document or protected.")
                    return
                
                # Compare texts
                diffs = compare_texts(text1, text2)
                
                # Generate summary
                summary = generate_summary(diffs)
                
                # Display results
                st.header("Comparison Results")
                
                # Display summary statistics
                display_summary(summary)
                
                # Add export buttons
                st.markdown("<h3 style='color: #553BFF;'>Export Results</h3>", unsafe_allow_html=True)
                
                export_col1, export_col2 = st.columns(2)
                
                with export_col1:
                    try:
                        # Export as HTML
                        html_content, html_filename = export_as_html(pdf1.name, pdf2.name, diffs, summary)
                        
                        # Create download button with Streamlit component
                        b64_html = base64.b64encode(html_content.encode()).decode()
                        download_link = f'data:text/html;base64,{b64_html}'
                        
                        # Use Streamlit button instead of HTML
                        with st.container():
                            download_col1, download_col2 = st.columns([1, 10])
                            with download_col1:
                                st.markdown("📄", unsafe_allow_html=True)
                            with download_col2:
                                st.download_button(
                                    label="Download as HTML",
                                    data=html_content,
                                    file_name=html_filename,
                                    mime="text/html",
                                    use_container_width=True
                                )
                    except Exception as e:
                        st.error(f"Error generating HTML export: {str(e)}")
                
                with export_col2:
                    try:
                        # Export as PDF
                        pdf_bytes, pdf_filename = export_as_pdf(pdf1.name, pdf2.name, diffs, summary)
                        
                        # Use Streamlit button for PDF download
                        with st.container():
                            download_col1, download_col2 = st.columns([1, 10])
                            with download_col1:
                                st.markdown("📊", unsafe_allow_html=True)
                            with download_col2:
                                st.download_button(
                                    label="Download as PDF",
                                    data=pdf_bytes,
                                    file_name=pdf_filename,
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                    except Exception as e:
                        st.error(f"Error generating PDF export: {str(e)}")
                
                # Display text differences
                st.markdown("<h2 style='color: #553BFF; text-align: center; margin-top: 30px;'>Detailed Differences</h2>", unsafe_allow_html=True)
                
                # Create tabs for different views with custom styling
                tab1, tab2, tab3 = st.tabs(["✨ Side by Side", "📄 First PDF", "📄 Second PDF"])
                
                with tab1:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("<h3 style='color: #0CA4A5; text-align: center; margin-bottom: 15px;'>First PDF</h3>", unsafe_allow_html=True)
                        
                        # Add navigation buttons for first PDF
                        nav_buttons_old = create_navigation_buttons(diffs, "pdf1-container", "old")
                        st.markdown(nav_buttons_old, unsafe_allow_html=True)
                        
                        st.markdown(
                            f"""<div id="pdf1-container" style='border: 1px solid #ddd; border-radius: 8px; padding: 15px; height: 500px; overflow-y: auto; background-color: #fcfcfc;'>
                            {highlight_differences(diffs, 'old')}
                            </div>""", 
                            unsafe_allow_html=True
                        )
                    
                    with col2:
                        st.markdown("<h3 style='color: #0CA4A5; text-align: center; margin-bottom: 15px;'>Second PDF</h3>", unsafe_allow_html=True)
                        
                        # Add navigation buttons for second PDF
                        nav_buttons_new = create_navigation_buttons(diffs, "pdf2-container", "new")
                        st.markdown(nav_buttons_new, unsafe_allow_html=True)
                        
                        st.markdown(
                            f"""<div id="pdf2-container" style='border: 1px solid #ddd; border-radius: 8px; padding: 15px; height: 500px; overflow-y: auto; background-color: #fcfcfc;'>
                            {highlight_differences(diffs, 'new')}
                            </div>""", 
                            unsafe_allow_html=True
                        )
                
                with tab2:
                    st.markdown("<h3 style='color: #0CA4A5; text-align: center; margin-bottom: 15px;'>First PDF</h3>", unsafe_allow_html=True)
                    
                    # Add navigation buttons for first PDF (single view)
                    nav_buttons_old_single = create_navigation_buttons(diffs, "pdf1-single-container", "old")
                    st.markdown(nav_buttons_old_single, unsafe_allow_html=True)
                    
                    st.markdown(
                        f"""<div id="pdf1-single-container" style='border: 1px solid #ddd; border-radius: 8px; padding: 15px; max-width: 800px; margin: 0 auto; height: 500px; overflow-y: auto; background-color: #fcfcfc;'>
                        {highlight_differences(diffs, 'old')}
                        </div>""", 
                        unsafe_allow_html=True
                    )
                
                with tab3:
                    st.markdown("<h3 style='color: #0CA4A5; text-align: center; margin-bottom: 15px;'>Second PDF</h3>", unsafe_allow_html=True)
                    
                    # Add navigation buttons for second PDF (single view)
                    nav_buttons_new_single = create_navigation_buttons(diffs, "pdf2-single-container", "new")
                    st.markdown(nav_buttons_new_single, unsafe_allow_html=True)
                    
                    st.markdown(
                        f"""<div id="pdf2-single-container" style='border: 1px solid #ddd; border-radius: 8px; padding: 15px; max-width: 800px; margin: 0 auto; height: 500px; overflow-y: auto; background-color: #fcfcfc;'>
                        {highlight_differences(diffs, 'new')}
                        </div>""", 
                        unsafe_allow_html=True
                    )
                
            except Exception as e:
                st.error(f"An error occurred during processing: {str(e)}")
            finally:
                # Clean up temp files
                temp_dir.cleanup()
    else:
        # Display attractive instructions with illustrations when files are not yet uploaded
        st.markdown("""
        <div style="text-align: center; margin: 50px 0;">
            <img src="https://img.icons8.com/color/150/000000/upload-to-cloud.png" style="max-width: 150px;">
            <h3 style="color: #553BFF; margin-top: 20px;">Ready to Compare Documents?</h3>
            <p style="color: #555; max-width: 600px; margin: 10px auto 30px auto; font-size: 16px;">
                Please upload both PDF documents using the upload fields above to start comparing.
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
