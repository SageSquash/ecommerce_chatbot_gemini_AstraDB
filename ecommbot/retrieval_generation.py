from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from ecommbot.ingest import ingestdata

def generation(vstore):
    # Configure the retriever
    retriever = vstore.as_retriever(search_kwargs={"k": 3})
    
    # Define the prompt template
    PRODUCT_BOT_TEMPLATE = """
    Your ecommercebot bot is an expert in product recommendations and customer queries.
    It analyzes product titles and reviews to provide accurate and helpful responses.
    Ensure your answers are relevant to the product context and refrain from straying off-topic.
    Your responses should be concise and informative.
    CONTEXT:
    {context}
    QUESTION: {question}
    YOUR ANSWER:
    """
    prompt = ChatPromptTemplate.from_template(PRODUCT_BOT_TEMPLATE)
    
    # Initialize Gemini model
    # You'll need to set GOOGLE_API_KEY environment variable
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.7)
    
    # Create the chain
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain

if __name__ == '__main__':
    vstore = ingestdata("done")
    chain = generation(vstore)
    print(chain.invoke("can you tell me the best bluetooth buds?"))