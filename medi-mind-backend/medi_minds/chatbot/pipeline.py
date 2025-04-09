from pymed import PubMed
from haystack import Pipeline, Document, component
from haystack.components.builders import PromptBuilder
from haystack.components.generators import HuggingFaceAPIGenerator
from haystack.utils.auth import Secret
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ['HUGGINGFACE_API_KEY'] = os.getenv('HUGGINGFACE_API_KEY')

def documentize(article):
    """Convert a PubMed article into a Haystack Document."""
    return Document(content=article.abstract or "No abstract available", 
                    meta={'title': article.title, 'keywords': article.keywords or []})

@component
class PubMedFetcher:
    """Custom component to fetch articles from PubMed."""
    @component.output_types(articles=List[Document])
    def run(self, queries: List[str]):
        """
        Fetch articles from PubMed based on queries.
        Input: queries (List[str]) - List of search queries.
        Output: Dict with 'articles' key containing a List[Document].
        """
        pubmed = PubMed(tool="HealthcareChatbot", email="your_email@example.com")
        articles = []
        for query in queries:
            try:
                response = pubmed.query(query.strip(), max_results=3)
                documents = [documentize(article) for article in response]
                articles.extend(documents)
            except Exception as e:
                print(f"Error fetching articles for query '{query}': {e}")
        return {"articles": articles}
    
# Prompt templates
keyword_prompt_template = """
Convert the question into 3-5 keywords for PubMed search.
Example:
Question: "What are the latest treatments for major depressive disorder?"
Keywords: Antidepressive Agents, Depressive Disorder, Major, Treatment-Resistant Depression
---
Question: {{ question }}
Keywords:
"""

answer_prompt_template = """
Answer the question based on the provided articles. If insufficient, use your knowledge.
Question: {{ question }}
Articles:
{% for article in articles %}
  Title: {{ article.meta['title'] }}
  Abstract: {{ article.content }}
  Keywords: {{ article.meta['keywords'] }}
{% endfor %}
Answer:
"""

def create_pipeline():
    """Create and configure a new Haystack pipeline with fresh component instances."""
    # Create separate LLM instances for each role
    llm_keywords = HuggingFaceAPIGenerator(
        api_type="serverless_inference_api",
        api_params={"model": "mistralai/Mixtral-8x7B-Instruct-v0.1"},
        token=Secret.from_token(os.getenv('HUGGINGFACE_API_KEY'))
    )
    llm_answer = HuggingFaceAPIGenerator(
        api_type="serverless_inference_api",
        api_params={"model": "mistralai/Mixtral-8x7B-Instruct-v0.1"},
        token=Secret.from_token(os.getenv('HUGGINGFACE_API_KEY'))
    )

    # Create fresh instances of components
    fetcher = PubMedFetcher()
    keyword_prompt_builder = PromptBuilder(template=keyword_prompt_template)
    answer_prompt_builder = PromptBuilder(template=answer_prompt_template)

    # Initialize a new pipeline
    pipe = Pipeline()

    # Add components to the pipeline
    pipe.add_component("keyword_prompt_builder", keyword_prompt_builder)
    pipe.add_component("llm_keywords", llm_keywords)  # Use separate instance
    pipe.add_component("pubmed_fetcher", fetcher)
    pipe.add_component("answer_prompt_builder", answer_prompt_builder)
    pipe.add_component("llm_answer", llm_answer)  # Use separate instance

    # Connect components
    pipe.connect("keyword_prompt_builder.prompt", "llm_keywords.prompt")
    pipe.connect("llm_keywords.replies", "pubmed_fetcher.queries")
    pipe.connect("pubmed_fetcher.articles", "answer_prompt_builder.articles")
    pipe.connect("answer_prompt_builder.prompt", "llm_answer.prompt")

    return pipe

def ask_question(question: str) -> str:
    """Run the pipeline to answer a question."""
    pipeline = create_pipeline()
    result = pipeline.run(data={
        "keyword_prompt_builder": {"question": question},
        "answer_prompt_builder": {"question": question},
        "llm_answer": {"generation_kwargs": {"max_new_tokens": 500}}
    })
    return result["llm_answer"]["replies"][0]

# Optional: Test the pipeline standalone
if __name__ == "__main__":
    test_question = "How are mRNA vaccines used for cancer treatment?"
    answer = ask_question(test_question)
    print(f"Question: {test_question}")
    print(f"Answer: {answer}")