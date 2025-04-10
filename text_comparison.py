import difflib
import re

def compare_texts(text1, text2):
    """
    Compare two text documents and identify differences.
    
    Args:
        text1 (str): Text from the first document
        text2 (str): Text from the second document
        
    Returns:
        list: A list of difference objects containing type and content
    """
    # Sanitize input text to prevent any HTML/CSS display
    def sanitize_for_display(text):
        # Replace HTML tags and CSS that might be in the PDF
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        # Replace other code-like patterns
        text = text.replace('{', '&#123;').replace('}', '&#125;')
        return text
        
    # Sanitize inputs before comparison
    text1 = sanitize_for_display(text1)
    text2 = sanitize_for_display(text2)
    # Split texts into paragraphs for better comparison
    paragraphs1 = text1.split('\n\n')
    paragraphs2 = text2.split('\n\n')
    
    # Create a SequenceMatcher object to compare the paragraphs
    matcher = difflib.SequenceMatcher(None, paragraphs1, paragraphs2)
    
    # Get the differences as opcodes
    opcodes = matcher.get_opcodes()
    
    # Process the opcodes to create a list of difference objects
    differences = []
    
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'equal':
            # Content is the same in both documents
            for i in range(i1, i2):
                differences.append({
                    'type': 'equal',
                    'old_content': paragraphs1[i],
                    'new_content': paragraphs1[i]
                })
        elif tag == 'replace':
            # Content is modified
            old_content = '\n\n'.join(paragraphs1[i1:i2])
            new_content = '\n\n'.join(paragraphs2[j1:j2])
            
            # For better granularity, compare the sentences within paragraphs
            old_sentences = re.split(r'(?<=[.!?])\s+', old_content)
            new_sentences = re.split(r'(?<=[.!?])\s+', new_content)
            
            sentence_matcher = difflib.SequenceMatcher(None, old_sentences, new_sentences)
            sentence_opcodes = sentence_matcher.get_opcodes()
            
            for s_tag, s_i1, s_i2, s_j1, s_j2 in sentence_opcodes:
                if s_tag == 'equal':
                    for s_i in range(s_i1, s_i2):
                        differences.append({
                            'type': 'equal',
                            'old_content': old_sentences[s_i],
                            'new_content': old_sentences[s_i]
                        })
                elif s_tag == 'replace':
                    differences.append({
                        'type': 'modified',
                        'old_content': ' '.join(old_sentences[s_i1:s_i2]),
                        'new_content': ' '.join(new_sentences[s_j1:s_j2])
                    })
                elif s_tag == 'delete':
                    differences.append({
                        'type': 'deleted',
                        'old_content': ' '.join(old_sentences[s_i1:s_i2]),
                        'new_content': ''
                    })
                elif s_tag == 'insert':
                    differences.append({
                        'type': 'added',
                        'old_content': '',
                        'new_content': ' '.join(new_sentences[s_j1:s_j2])
                    })
        elif tag == 'delete':
            # Content is deleted in the second document
            for i in range(i1, i2):
                differences.append({
                    'type': 'deleted',
                    'old_content': paragraphs1[i],
                    'new_content': ''
                })
        elif tag == 'insert':
            # Content is added in the second document
            for j in range(j1, j2):
                differences.append({
                    'type': 'added',
                    'old_content': '',
                    'new_content': paragraphs2[j]
                })
    
    return differences

def generate_summary(diffs):
    """
    Generate a summary of differences.
    
    Args:
        diffs (list): List of difference objects
        
    Returns:
        dict: Summary statistics
    """
    added = 0
    deleted = 0
    modified = 0
    unchanged = 0
    
    added_content = []
    deleted_content = []
    modified_content = []
    
    for diff in diffs:
        if diff['type'] == 'added':
            added += 1
            added_content.append(diff['new_content'])
        elif diff['type'] == 'deleted':
            deleted += 1
            deleted_content.append(diff['old_content'])
        elif diff['type'] == 'modified':
            modified += 1
            modified_content.append({
                'old': diff['old_content'],
                'new': diff['new_content']
            })
        elif diff['type'] == 'equal':
            unchanged += 1
    
    total_elements = added + deleted + modified + unchanged
    
    # Calculate total words for each type
    added_words = sum(len(content.split()) for content in added_content)
    deleted_words = sum(len(content.split()) for content in deleted_content)
    modified_words_old = sum(len(item['old'].split()) for item in modified_content)
    modified_words_new = sum(len(item['new'].split()) for item in modified_content)
    
    return {
        'total_elements': total_elements,
        'additions': {
            'count': added,
            'percentage': (added / total_elements * 100) if total_elements > 0 else 0,
            'words': added_words
        },
        'deletions': {
            'count': deleted,
            'percentage': (deleted / total_elements * 100) if total_elements > 0 else 0,
            'words': deleted_words
        },
        'modifications': {
            'count': modified,
            'percentage': (modified / total_elements * 100) if total_elements > 0 else 0,
            'words_old': modified_words_old,
            'words_new': modified_words_new
        },
        'unchanged': {
            'count': unchanged,
            'percentage': (unchanged / total_elements * 100) if total_elements > 0 else 0
        }
    }
