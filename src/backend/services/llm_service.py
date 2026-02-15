import ollama
from src.backend.config import settings
from typing import Dict, Any, List

class LLMService:
    def __init__(self):
        self.model = "mistral" # Default model, can be configurable
        # Ensure ollama client is configured if needed, usually it connects to localhost:11434 by default

    def generate_slo_recommendation(self, service_data: Dict[str, Any], dependencies: List[Dict[str, Any]], runbooks: List[str], metrics: List[Dict[str, Any]]) -> str:
        
        # Construct the prompt
        prompt = f"""
        You are an expert Site Reliability Engineer (SRE). Your task is to recommend Service Level Objectives (SLOs) for a microservice based on its topology, historical metrics, and operational runbooks.

        **Service Context**:
        - Name: {service_data.get('name')}
        - Type: {service_data.get('type')}
        - Tier: {service_data.get('tier')}

        **Dependencies**:
        {dependencies}

        **Historical Metrics (Last 24h Summary)**:
        {metrics[:5]} ... (truncated for brevity)
        
        **Relevant Runbooks**:
        {self._format_runbooks(runbooks)}

        **Task**:
        1. Analyze the service's criticality based on its tier and dependencies.
        2. Evaluate its recent performance (latency, error rates) from the metrics.
        3. Recommend specific SLOs for:
           - Availability (e.g., 99.9%, 99.99%)
           - Latency (e.g., P99 < 200ms)
        4. Provide a "Strategy" or "Reasoning" section explaining WHY you chose these targets, citing specific runbooks or metric trends if relevant.

        **Output Format**:
        Return the response in Markdown format.
        """

        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']
        except Exception as e:
            return f"Error generating recommendation: {str(e)}. Ensure Ollama is running."

    def chat_with_context(self, service_data: Dict[str, Any], dependencies: List[Dict[str, Any]], runbooks: List[str], metrics: List[Dict[str, Any]], messages: List[Dict[str, str]]) -> str:
        
        # System context
        system_context = f"""
        You are an expert SRE assistant helping a user with SLO recommendations.
        
        **Service Context**:
        - Name: {service_data.get('name')}
        - Type: {service_data.get('type')}
        - Tier: {service_data.get('tier')}

        **Dependencies**:
        {dependencies}

        **Historical Metrics (Last 24h Summary)**:
        {metrics[:5]} ... (truncated)
        
        **Relevant Runbooks**:
        {self._format_runbooks(runbooks)}
        
        **Instructions**:
        - Answer the user's follow-up questions based on the provided context.
        - If the user asks to adjust the SLO, analyze the impact based on metrics.
        - Be concise and helpful.
        """

        # Construct message history for Ollama
        # Ollama expects [{'role': 'system', 'content': ...}, {'role': 'user', ...}]
        # Some models handle system prompt differently, but usually 'system' role works or prepending to first user message.
        # Let's prepend system context to the message history list or just use it as the first message.
        
        ollama_messages = [{'role': 'system', 'content': system_context}] + messages

        try:
            response = ollama.chat(model=self.model, messages=ollama_messages)
            return response['message']['content']
        except Exception as e:
            return f"Error responding to chat: {str(e)}"

    def _format_runbooks(self, runbooks: List[str]) -> str:
        return "\n".join([f"- {r}" for r in runbooks])

llm_service = LLMService()
