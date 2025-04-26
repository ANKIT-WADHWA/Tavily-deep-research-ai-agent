import os
from dotenv import load_dotenv
from fetch_data import search_web
from summarize import summarize_text, relevance_score
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()

# Define state schema
state = (
    ("query", str),
    ("articles", list),
)

# Research Agent node
def research_node(state):
    query = state.get("query", "")
    if not query:
        raise ValueError("Query not found in state.")
    
    raw_data = search_web(query)
    articles = raw_data.get("results", []) if raw_data else []
    return {"query": query, "articles": articles}

# Answer Agent node (Expanded summary and drafted answer)
def answer_node(state):
    articles = state.get("articles", [])
    summaries = []

    if not articles:
        print("❌ No articles found.")
        return {"summaries": []}

    ranked_articles = []

    for idx, article in enumerate(articles, 1):
        content = article.get("content") or article.get("raw_content") or ""
        article_link = article.get("url", "No link available")  # Assuming the article has a URL key
        if content:
            summary = summarize_text(content)
            score = relevance_score(state["query"], content)

            ranked_articles.append({
                "index": idx,
                "original": content,
                "summary": summary,
                "relevance_score": score,
                "link": article_link  # Add link to article
            })
        else:
            print(f"⚠️ Article {idx} has no content.")

    # Sort the articles by relevance score (descending)
    ranked_articles.sort(key=lambda x: x["relevance_score"], reverse=True)

    # Print the ranked articles with full summaries (no truncation)
    print("\n📊 Ranked Articles Based on Relevance Score:")
    for idx, article in enumerate(ranked_articles, 1):
        print(f"\nRank: {idx}")
        print(f"Article Index: {article['index']}")
        print(f"Relevance Score: {article['relevance_score']}")
        print(f"Summary: {article['summary']}")
        print(f"Link: {article['link']}")

    # Answer Drafting: Combine the summaries into one detailed answer
    combined_summary = "\n".join([article["summary"] for article in ranked_articles])

    # Draft a comprehensive answer from the combined summary
    drafted_answer = f"Answer based on research:\n\n{combined_summary}"

    print("\n📝 Drafted Answer Based on Articles:")
    print(drafted_answer)

    return {"summaries": ranked_articles, "drafted_answer": drafted_answer}

# Build the graph
graph_builder = StateGraph(state)
graph_builder.add_node("ResearchAgent", research_node)
graph_builder.add_node("AnswerAgent", answer_node)

graph_builder.set_entry_point("ResearchAgent")
graph_builder.add_edge("ResearchAgent", "AnswerAgent")
graph_builder.add_edge("AnswerAgent", END)

graph = graph_builder.compile()

if __name__ == "__main__":
    query = input("Enter your research query: ")
    final_state = graph.invoke({"query": query})
