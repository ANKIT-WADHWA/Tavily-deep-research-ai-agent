from transformers import pipeline

# Initialize the summarizer pipeline with the BART model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text):
    """
    Summarizes the input text using Hugging Face transformers' BART model.
    """
    input_length = len(text.split())

    # Define summarization length bounds
    max_length = min(input_length // 2, 400)  # Cap summary at 400 tokens
    min_length = max(input_length // 4, 100)  # Ensure minimum detail

    # Ensure valid lengths
    if min_length >= max_length:
        min_length = max_length - 1

    try:
        # Generate the summary
        summary = summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )
        return summary[0]['summary_text']
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return "Error during summarization."

def relevance_score(query, article_content):
    """
    Calculates the relevance score based on query matching with article content.
    """
    # Placeholder for calculating relevance score based on query and article
    # For simplicity, we can use a basic matching score (real implementations can use NLP models)
    query_terms = query.split()
    article_terms = article_content.split()

    common_terms = len(set(query_terms) & set(article_terms))
    return common_terms  # You can modify this to be a more sophisticated score
