from smolagents import tool
from annotator.models import call_llm

@tool
def span_critique(span: str) -> str:
    """
    Critique a single span in agent execution traces.
    
    Args:
        span (str): The span to critique.
        
    Returns:
       str: The critique of the span.
    """
    
    
    # Call the LLM to critique the span
    response = call_llm(f"Critique the following span: {span}")
    return response
