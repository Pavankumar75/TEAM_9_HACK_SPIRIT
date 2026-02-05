from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import src.config as config
from src.retrieval import retriever

class RAGSystem:
    def __init__(self):
        print(f"Initializing RAGSystem with model {config.LLM_MODEL}...")
        self.llm = ChatOllama(model=config.LLM_MODEL, temperature=0.1)
        self.pandas_agent = retriever.get_structured_data_agent(self.llm)
        
        # Prompt for Vector RAG (Guardrailed)
        self.rag_prompt = PromptTemplate(
            template="""You are an expert HR Bot for Helix Corporation.
            
            GUIDELINES:
            1. Use ONLY the provided context to answer.
            2. If the answer contains specific policy details, cite the source section.
            3. CRITICAL: If the context does not contain enough information to answer the question, state: "I don't have enough information in the policy documents to answer this."
            4. Do not make up or hallucinate policies.
            
            Context: {context}
            
            Question: {question}
            
            Answer:""",
            input_variables=["context", "question"]
        )
        # LCEL Chain: Prompt -> LLM -> String Output
        self.rag_chain = self.rag_prompt | self.llm | StrOutputParser()

        # Router Prompt
        self.router_prompt = PromptTemplate(
            template="""Given the user question below, classify it into one of three categories:
            1. 'policy': Questions about rules, guidelines, maternity leave duration, code of conduct, etc. (General knowledge from documents)
            2. 'data': Questions about specific employees, attendance, leave balances, or statistics (Requires database lookup)
            3. 'hybrid': Questions that require both policy rules AND specific employee data (e.g., "Is John's leave valid according to policy?", "Who violated the attendance policy?")
            
            Do not answer the question. Just output 'policy', 'data', or 'hybrid'.
            
            Question: {question}
            Category:""",
            input_variables=["question"]
        )
        # LCEL Chain: Prompt -> LLM -> String Output
        self.router_chain = self.router_prompt | self.llm | StrOutputParser()

    def route_query(self, query: str) -> str:
        """Decides whether to use Vector Store or Pandas Agent."""
        response = self.router_chain.invoke({"question": query})
        return response.strip().lower().replace("'", "").replace('"', "")

    def refresh_agent(self):
        """Recreates the pandas agent to pick up new data."""
        self.pandas_agent = retriever.get_structured_data_agent(self.llm)

    def generate_response(self, query: str):
        """
        Main entry point for generating a response.
        """
        category = self.route_query(query)
        print(f"Routing Query: '{query}' -> Category: {category}")

        docs = []
        if "policy" in category:
            # use Vector Search
            docs = retriever.search_policy_documents(query)
            if isinstance(docs, str): # Error message
                return f"Error: {docs}", []
            
            context = "\n\n".join([d.page_content for d in docs])
            response = self.rag_chain.invoke({"context": context, "question": query})
            return response, docs

        elif "data" in category:
            # use Pandas Agent
            try:
                # Augment prompt to force readable output
                formatted_query = f"{query}\n\nIMPORTANT: Provide the final answer as a readable sentence or a markdown table. Do NOT return the raw DataFrame object or Python code."
                response = self.pandas_agent.invoke({"input": formatted_query})
                # Pandas agent output structure might vary, usually 'output' key
                if isinstance(response, dict) and 'output' in response:
                    return response['output'], []
                return str(response), []
            except Exception as e:
                return f"Data Query Error: {str(e)}", []

        elif "hybrid" in category or "both" in category:
            # 1. Get Policy Context
            docs = retriever.search_policy_documents(query)
            policy_context = ""
            if not isinstance(docs, str):
                 policy_context = "\n\n".join([d.page_content for d in docs])
            
            # 2. Augment Query for Pandas Agent
            # The Pandas Agent is smart (it uses LLM). We tell it the policy rules and ask it to check the data.
            augmented_query = f"""
            Context from Corporate Policy:
            {policy_context}
            
            User Question: {query}
            
            Task: Use the data (checking employee records, leave, etc.) to answer the User Question, considering the Policy Context provided above.
            """
            
            try:
                response = self.pandas_agent.invoke({"input": augmented_query})
                if isinstance(response, dict) and 'output' in response:
                    return response['output'], docs
                return str(response), docs
            except Exception as e:
                return f"Hybrid Query Error: {str(e)}", docs
        
        else:
            # Fallback
            return "I couldn't determine the best way to answer that. Defaulting to general knowledge.", []

_rag_system_instance = None

def get_rag_system():
    global _rag_system_instance
    if _rag_system_instance is None:
        _rag_system_instance = RAGSystem()
    return _rag_system_instance
