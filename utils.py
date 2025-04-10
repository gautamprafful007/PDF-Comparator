import streamlit as st

def highlight_differences(diffs, version='new'):
    """
    Format the differences with HTML highlighting and add navigable anchors.
    
    Args:
        diffs (list): List of difference objects
        version (str): 'old' for first document, 'new' for second document
        
    Returns:
        str: HTML formatted text with highlighted differences and navigation anchors
    """
    highlighted_text = ""
    
    # Counters for unique IDs
    addition_count = 0
    deletion_count = 0
    modification_count = 0
    
    # Helper function to make text safe for HTML display
    # This will ensure code blocks are displayed as plain text
    def sanitize_content(content):
        # Replace < and > to prevent any HTML/code rendering
        content = content.replace('<', '&lt;').replace('>', '&gt;')
        return content
    
    if version == 'old':
        for diff in diffs:
            if diff['type'] == 'equal':
                highlighted_text += f"<p style='margin-bottom: 8px; line-height: 1.5;'>{sanitize_content(diff['old_content'])}</p>"
            elif diff['type'] == 'added':
                # Show an empty placeholder for content that's only in the new document
                highlighted_text += f"<p style='margin-bottom: 8px; line-height: 1.5; background-color: #F8F8F8; color: #888888; padding: 10px; border-radius: 5px; font-style: italic;'>[Content only in second document]</p>"
            elif diff['type'] == 'deleted':
                deletion_count += 1
                highlighted_text += f"<p id='{version}-deletion-{deletion_count}' style='margin-bottom: 8px; line-height: 1.5;'><span style='background-color: #FFCCCC; padding: 2px 0; border-radius: 3px;'>{sanitize_content(diff['old_content'])}</span></p>"
            elif diff['type'] == 'modified':
                modification_count += 1
                highlighted_text += f"<p id='{version}-modification-{modification_count}' style='margin-bottom: 8px; line-height: 1.5;'><span style='background-color: #FFFFCC; padding: 2px 0; border-radius: 3px;'>{sanitize_content(diff['old_content'])}</span></p>"
    else:  # version == 'new'
        for diff in diffs:
            if diff['type'] == 'equal':
                highlighted_text += f"<p style='margin-bottom: 8px; line-height: 1.5;'>{sanitize_content(diff['new_content'])}</p>"
            elif diff['type'] == 'added':
                addition_count += 1
                highlighted_text += f"<p id='{version}-addition-{addition_count}' style='margin-bottom: 8px; line-height: 1.5;'><span style='background-color: #CCFFCC; padding: 2px 0; border-radius: 3px;'>{sanitize_content(diff['new_content'])}</span></p>"
            elif diff['type'] == 'deleted':
                # Show an empty placeholder for content that's only in the old document
                highlighted_text += f"<p style='margin-bottom: 8px; line-height: 1.5; background-color: #F8F8F8; color: #888888; padding: 10px; border-radius: 5px; font-style: italic;'>[Content only in first document]</p>"
            elif diff['type'] == 'modified':
                modification_count += 1
                highlighted_text += f"<p id='{version}-modification-{modification_count}' style='margin-bottom: 8px; line-height: 1.5;'><span style='background-color: #FFFFCC; padding: 2px 0; border-radius: 3px;'>{sanitize_content(diff['new_content'])}</span></p>"
    
    return highlighted_text

def count_change_types(diffs):
    """
    Count the number of each type of change in the diffs
    
    Args:
        diffs (list): List of difference objects
    
    Returns:
        tuple: Counts of additions, deletions, and modifications
    """
    additions = sum(1 for diff in diffs if diff['type'] == 'added')
    deletions = sum(1 for diff in diffs if diff['type'] == 'deleted')
    modifications = sum(1 for diff in diffs if diff['type'] == 'modified')
    
    return additions, deletions, modifications

def create_navigation_buttons(diffs, container_id, version):
    """
    Create navigation buttons for different types of changes
    
    Args:
        diffs (list): List of difference objects
        container_id (str): ID of the container div
        version (str): 'old' or 'new' version
    
    Returns:
        str: HTML for navigation buttons
    """
    additions, deletions, modifications = count_change_types(diffs)
    
    # Skip creating buttons if there are no changes
    if version == 'old' and additions == 0 and deletions == 0 and modifications == 0:
        return ""
    
    if version == 'new' and additions == 0 and deletions == 0 and modifications == 0:
        return ""
    
    html = f"""
    <div style="margin: 10px 0; padding: 12px; background-color: #f9f9f9; border-radius: 8px; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;">
    """
    
    # Only show additions in 'new' version
    if version == 'new' and additions > 0:
        for i in range(1, additions + 1):
            html += f"""
            <button 
               style="display: inline-block; background-color: #CCFFCC; color: #333; padding: 8px 12px; border-radius: 20px; text-decoration: none; font-size: 14px; margin: 4px; font-weight: 500; box-shadow: 0px 2px 4px rgba(0,0,0,0.1); transition: all 0.2s ease; border: none; cursor: pointer;">
               ➕ Addition #{i}
            </button>
            """
    
    # Only show deletions in 'old' version
    if version == 'old' and deletions > 0:
        for i in range(1, deletions + 1):
            html += f"""
            <button 
               style="display: inline-block; background-color: #FFCCCC; color: #333; padding: 8px 12px; border-radius: 20px; text-decoration: none; font-size: 14px; margin: 4px; font-weight: 500; box-shadow: 0px 2px 4px rgba(0,0,0,0.1); transition: all 0.2s ease; border: none; cursor: pointer;">
               ➖ Deletion #{i}
            </button>
            """
    
    # Show modifications in both versions
    if modifications > 0:
        for i in range(1, modifications + 1):
            html += f"""
            <button 
               style="display: inline-block; background-color: #FFFFCC; color: #333; padding: 8px 12px; border-radius: 20px; text-decoration: none; font-size: 14px; margin: 4px; font-weight: 500; box-shadow: 0px 2px 4px rgba(0,0,0,0.1); transition: all 0.2s ease; border: none; cursor: pointer;">
               ✏️ Change #{i}
            </button>
            """
    
    html += "</div>"
    return html

def display_summary(summary):
    """
    Display a summary of the document comparison.
    
    Args:
        summary (dict): Summary statistics
    """
    st.markdown("<h2 style='color: #553BFF; text-align: center;'>Summary of Changes</h2>", unsafe_allow_html=True)
    
    # Create a colorful container for metrics
    st.markdown("""
    <div style="background-color: #f9f9f9; border-radius: 15px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); margin-bottom: 25px;">
    """, unsafe_allow_html=True)
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Additions", 
            value=summary['additions']['count'],
            delta=f"{summary['additions']['words']} words",
            delta_color="normal"
        )
        
    with col2:
        st.metric(
            label="Deletions", 
            value=summary['deletions']['count'],
            delta=f"{summary['deletions']['words']} words",
            delta_color="inverse"
        )
        
    with col3:
        st.metric(
            label="Modifications", 
            value=summary['modifications']['count'],
            delta=f"{summary['modifications']['words_new'] - summary['modifications']['words_old']} words"
        )
        
    with col4:
        st.metric(
            label="Unchanged", 
            value=summary['unchanged']['count']
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
        
    # Create a legend for the highlighting colors
    st.markdown("""
    <div style="display: flex; flex-direction: row; margin: 25px 0; justify-content: center;">
        <div style="margin-right: 20px; display: flex; align-items: center;">
            <span style="background-color: #CCFFCC; padding: 8px 15px; border-radius: 20px; font-weight: 500;">Added Content</span>
        </div>
        <div style="margin-right: 20px; display: flex; align-items: center;">
            <span style="background-color: #FFCCCC; padding: 8px 15px; border-radius: 20px; font-weight: 500;">Removed Content</span>
        </div>
        <div style="display: flex; align-items: center;">
            <span style="background-color: #FFFFCC; padding: 8px 15px; border-radius: 20px; font-weight: 500;">Modified Content</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
