import asyncio
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models.base import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from src.mcp_agent import Agent, LLMProvider  # Import your Agent class


class InteractiveChat:
    """
    Interactive chat interface for the Agent class.
    Maintains conversation history and provides a clean chat experience.
    Supports interchangeable agents.
    """
    
    def __init__(self, agent: Agent, max_history: int = 50):
        """
        Initialize the interactive chat.
        
        Args:
            agent: Agent instance to use for conversations
            max_history: Maximum number of messages to keep in history
        """
        if not isinstance(agent, Agent):
            raise TypeError("Expected Agent instance, got {}".format(type(agent).__name__))
            
        self.agent = agent
        self.chat_history: List[BaseMessage] = []
        self.max_history = max_history
        self._agent_built = False
    
    async def set_agent(self, agent: Agent):
        """
        Switch to a different agent instance.
        
        Args:
            agent: New Agent instance to use
        """
        self.agent = agent
        self.model = None  # Model is managed by the agent
        self._agent_built = False
        print(f"🔄 Switched to new agent instance")
    
    async def set_model(self, model: BaseChatModel):
        """
        Switch to a different model by creating a new agent.
        
        Args:
            model: New language model to use
        """
        self.agent = Agent(model)
        self.model = model
        self._agent_built = False
        print(f"🔄 Switched to new model: {model.__class__.__name__}")
    
    async def _ensure_agent_built(self):
        """Ensure the agent is built before use."""
        if not self._agent_built:
            await self.agent.build_agent()
            self._agent_built = True
    
    async def send_message(self, message: str) -> str:
        """
        Send a message to the agent and get a response.
        
        Args:
            message: The user's message
            
        Returns:
            The agent's response as a string
        """
        await self._ensure_agent_built()
        
        # Add user message to history
        user_message = HumanMessage(content=message)
        self.chat_history.append(user_message)
        
        # Prepare messages for the agent (include history)
        messages_for_agent = self.chat_history.copy()
        
        try:
            # Get response from agent
            response = await self.agent.run(message)
            
            # Extract the AI response from the agent's output
            if response and "messages" in response:
                messages = response["messages"]
                if messages:
                    # Get the last AI message
                    ai_response = None
                    for msg in reversed(messages):
                        if hasattr(msg, 'content') and msg.content:
                            ai_response = msg
                            break
                    
                    if ai_response:
                        # Add AI response to history
                        self.chat_history.append(ai_response)
                        
                        # Trim history if needed
                        self._trim_history()
                        
                        return ai_response.content
            
            return "I apologize, but I couldn't generate a proper response."
            
        except Exception as e:
            error_msg = f"Error occurred: {str(e)}"
            # Add error as AI message to maintain conversation flow
            error_ai_msg = AIMessage(content=error_msg)
            self.chat_history.append(error_ai_msg)
            return error_msg
    
    def _trim_history(self):
        """Trim chat history to maintain max_history limit."""
        if len(self.chat_history) > self.max_history:
            # Keep the most recent messages
            self.chat_history = self.chat_history[-self.max_history:]
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """
        Get the chat history in a readable format.
        
        Returns:
            List of dictionaries with 'role' and 'content' keys
        """
        history = []
        for message in self.chat_history:
            if isinstance(message, HumanMessage):
                history.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                history.append({"role": "assistant", "content": message.content})
        return history
    
    def clear_history(self):
        """Clear the chat history."""
        self.chat_history = []
    
    def get_last_exchange(self) -> Optional[Dict[str, str]]:
        """
        Get the last user-assistant exchange.
        
        Returns:
            Dictionary with 'user' and 'assistant' messages, or None if not available
        """
        if len(self.chat_history) < 2:
            return None
        
        last_ai = None
        last_user = None
        
        # Find the last AI and user messages
        for message in reversed(self.chat_history):
            if isinstance(message, AIMessage) and last_ai is None:
                last_ai = message.content
            elif isinstance(message, HumanMessage) and last_user is None:
                last_user = message.content
            
            if last_ai and last_user:
                break
        
        if last_ai and last_user:
            return {"user": last_user, "assistant": last_ai}
        return None
    
    async def start_interactive_session(self):
        """
        Start an interactive chat session in the terminal.
        Type 'quit', 'exit', or 'bye' to end the session.
        """
        print("🤖 Interactive Chat Started!")
        print("Type 'quit', 'exit', or 'bye' to end the session.")
        print("Type 'history' to see chat history.")
        print("Type 'clear' to clear chat history.")
        print("Type 'info' to see current agent/model information.")
        print("-" * 50)
        
        await self._ensure_agent_built()
        
        while True:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'history':
                    self._print_history()
                    continue
                elif user_input.lower() == 'clear':
                    self.clear_history()
                    print("🧹 Chat history cleared!")
                    continue
                elif user_input.lower() == 'info':
                    self._print_agent_info()
                    continue
                elif not user_input:
                    print("Please enter a message.")
                    continue
                
                # Send message and get response
                print("🤖 Assistant: ", end="", flush=True)
                response = await self.send_message(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")
    
    def _print_history(self):
        """Print the chat history in a readable format."""
        history = self.get_chat_history()
        if not history:
            print("📭 No chat history available.")
            return
        
        print("\n📜 Chat History:")
        print("-" * 30)
    
    def _print_agent_info(self):
        """Print current agent information."""
        info = self.get_current_agent_info()
        print("\n🤖 Current Agent Information:")
        print("-" * 35)
        print(f"Agent Class: {info['agent_class']}")
        print(f"Agent ID: {info['agent_id']}")
        print(f"Agent Built: {info['agent_built']}")
        print(f"Model Class: {info['model_class']}")
        if info['model_id']:
            print(f"Model ID: {info['model_id']}")
        print("-" * 35)
        for i, exchange in enumerate(history, 1):
            role_emoji = "👤" if exchange["role"] == "user" else "🤖"
            role_name = "You" if exchange["role"] == "user" else "Assistant"
            print(f"{role_emoji} {role_name}: {exchange['content']}")
        print("-" * 30)


# Utility function to run the interactive chat with an agent
def run_interactive_chat(agent: Agent, max_history: int = 50):
    """
    Start an interactive chat session with a specific agent.
    
    Args:
        agent: The Agent instance to use
        max_history: Maximum number of messages to keep in history
    """
    async def _run():
        chat = InteractiveChat(agent, max_history)
        await chat.start_interactive_session()
    
    asyncio.run(_run())



if __name__ == "__main__":
    # Example usage
    llm = LLMProvider().model
    agent = Agent(llm)

    asyncio.run(run_interactive_chat(agent=agent))