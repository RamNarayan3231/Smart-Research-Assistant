import re

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters except basic punctuation
    text = re.sub(r'[^\w\s.,;:!?\'"-]', '', text)
    return text.strip()

def count_words(text: str) -> int:
    """Count words in a string"""
    return len(text.split())

def extract_relevant_section(text: str, keywords: list) -> str:
    """
    Extract the most relevant section containing the keywords
    """
    sentences = re.split(r'(?<=[.!?]) +', text)
    relevant_sentences = []
    
    for sentence in sentences:
        if any(keyword.lower() in sentence.lower() for keyword in keywords):
            relevant_sentences.append(sentence)
    
    return ' '.join(relevant_sentences) if relevant_sentences else text[:500]