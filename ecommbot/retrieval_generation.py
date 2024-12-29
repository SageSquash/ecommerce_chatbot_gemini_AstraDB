import os
os.environ['GRPC_ENABLE_FORK_SUPPORT'] = '0'

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import HumanMessage, AIMessage
from ecommbot.ingest import ingestdata
import json
import os
from datetime import datetime

class ConversationManager:
    def __init__(self, conversation_dir="conversations"):
        self.conversation_dir = conversation_dir
        if not os.path.exists(conversation_dir):
            os.makedirs(conversation_dir)
    
    def save_conversation(self, conversation_id, messages):
        try:
            # Convert messages to serializable format
            serializable_messages = []
            for message in messages:
                serializable_messages.append({
                    'type': message.__class__.__name__,
                    'content': message.content,
                    'additional_kwargs': message.additional_kwargs
                })
            
            filename = os.path.join(self.conversation_dir, f"conversation_{conversation_id}.json")
            with open(filename, 'w') as f:
                json.dump(serializable_messages, f)
            return True
        except Exception as e:
            print(f"Error saving conversation: {str(e)}")
            return False
    
    def load_conversation(self, conversation_id):
        try:
            filename = os.path.join(self.conversation_dir, f"conversation_{conversation_id}.json")
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    serialized_messages = json.load(f)
                    
                messages = []
                for msg in serialized_messages:
                    if msg['type'] == 'HumanMessage':
                        messages.append(HumanMessage(
                            content=msg['content'],
                            additional_kwargs=msg['additional_kwargs']
                        ))
                    elif msg['type'] == 'AIMessage':
                        messages.append(AIMessage(
                            content=msg['content'],
                            additional_kwargs=msg['additional_kwargs']
                        ))
                return messages
            return []
        except Exception as e:
            print(f"Error loading conversation: {str(e)}")
            return []
    
    def list_conversations(self):
        try:
            conversations = []
            for filename in os.listdir(self.conversation_dir):
                if filename.endswith('.json'):
                    conversation_id = filename.replace('conversation_', '').replace('.json', '')
                    conversations.append(conversation_id)
            return conversations
        except Exception as e:
            print(f"Error listing conversations: {str(e)}")
            return []

    def clear(self):
        """Clear all conversation history"""
        try:
            for filename in os.listdir(self.conversation_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.conversation_dir, filename))
            return True
        except Exception as e:
            print(f"Error clearing conversations: {str(e)}")
            return False

def generation(vstore):
    # Configure the retriever
    retriever = vstore.as_retriever(search_kwargs={"k": 3})
    
    # Initialize memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Define the prompt template
    PRODUCT_BOT_TEMPLATE = """
    Your ecommercebot bot is an expert in product recommendations and customer queries.
    It analyzes product titles and reviews to provide accurate and helpful responses.
    Ensure your answers are relevant to the product context and refrain from straying off-topic.
    Your responses should be concise and informative.

    Previous conversation:
    {chat_history}

    CONTEXT:
    {context}
    
    CURRENT QUESTION: {question}
    YOUR ANSWER:
    """
    
    # Initialize Gemini model
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.7)
    
    # Create the conversational chain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={
            "prompt": ChatPromptTemplate.from_template(PRODUCT_BOT_TEMPLATE)
        }
    )
    
    return qa_chain, memory

def chat_loop(chain, memory, conversation_manager):
    print("\nWelcome to the E-commerce Bot!")
    print("Do you want to: ")
    print("1. Start a new conversation")
    print("2. Continue previous conversation")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        memory.clear()
        print(f"Starting new conversation (ID: {conversation_id})")
    elif choice == "2":
        conversations = conversation_manager.list_conversations()
        if not conversations:
            print("No previous conversations found. Starting new conversation.")
            conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            memory.clear()
        else:
            print("\nAvailable conversations:")
            for i, conv_id in enumerate(conversations, 1):
                print(f"{i}. {conv_id}")
            try:
                selection = int(input("Select conversation number (or 0 for new): "))
                if selection == 0:
                    conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                    memory.clear()
                else:
                    conversation_id = conversations[selection-1]
                    previous_messages = conversation_manager.load_conversation(conversation_id)
                    memory.clear()
                    for message in previous_messages:
                        memory.chat_memory.add_message(message)
            except (ValueError, IndexError):
                print("Invalid selection. Starting new conversation.")
                conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                memory.clear()
    else:
        print("Invalid choice. Starting new conversation.")
        conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        memory.clear()

    print("\nBot: Hello! How can I help you today?")
    print("Commands:")
    print("- Type 'quit' to exit")
    print("- Type 'save' to save conversation")
    print("- Type 'clear' to start a new conversation")
    
    try:
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                if conversation_manager.save_conversation(
                    conversation_id,
                    memory.chat_memory.messages
                ):
                    print("Bot: Conversation saved. Goodbye!")
                break
                
            elif user_input.lower() == 'save':
                if conversation_manager.save_conversation(
                    conversation_id,
                    memory.chat_memory.messages
                ):
                    print("Bot: Conversation saved!")
                continue
            
            elif user_input.lower() == 'clear':
                memory.clear()
                conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                print("Bot: Started a new conversation!")
                continue
            
            try:
                response = chain.invoke({"question": user_input})
                print("Bot:", response['answer'])
                
                conversation_manager.save_conversation(
                    conversation_id,
                    memory.chat_memory.messages
                )
            except Exception as e:
                print(f"An error occurred while processing your request: {str(e)}")
    
    except KeyboardInterrupt:
        print("\nBot: Saving conversation before exit...")
        conversation_manager.save_conversation(
            conversation_id,
            memory.chat_memory.messages
        )
        print("Bot: Conversation saved. Goodbye!")

def list_saved_conversations(conversation_manager):
    conversations = conversation_manager.list_conversations()
    if conversations:
        print("Saved conversations:")
        for conv_id in conversations:
            print(f"- {conv_id}")
    else:
        print("No saved conversations found.")

if __name__ == '__main__':
    vstore = ingestdata("done")
    chain, memory = generation(vstore)
    conversation_manager = ConversationManager()
    
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            list_saved_conversations(conversation_manager)
        elif sys.argv[1] == '--new':
            memory.clear()
            chat_loop(chain, memory, conversation_manager)
        elif sys.argv[1] == '--clear':
            if conversation_manager.clear():
                print("All conversations cleared.")
            else:
                print("Failed to clear conversations.")
    else:
        chat_loop(chain, memory, conversation_manager)