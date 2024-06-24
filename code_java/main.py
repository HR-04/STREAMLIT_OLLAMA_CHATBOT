from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()



os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

llm = Ollama(model="codellama")

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = splitter.split_text(text)
    return chunks

def get_vector_store(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain_for_java():
    prompt_template = """
    You are a Java code trainer. Your task is to provide a solution in Java to the question or scenario asked. 
    Along with the solution, provide an explanation for each line of code. Make sure the code explanation is detailed line by line  
    and easy to understand as points line by line . If the answer is not in the provided context, just say, "answer is not available in the context". 
    Do not provide the wrong answer.

    Context:\n {context}\n
    Question: \n{question}\n

    Solution in Java:
    ```java
    {solution}
    ```
    
    Explanation:
    {explanation}
    """
    
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question", "solution", "explanation"])
    chain = load_qa_chain(llm=llm, chain_type="stuff", prompt=prompt)
    return chain

def clear_chat_history():
    st.session_state.messages = [
        {"role": "assistant", "content": "Upload some PDFs and ask me a question."}]

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question, k=3)  # Limit the number of returned documents

    context = " ".join([doc.page_content for doc in docs])
    if len(context) > 10000:  # Ensure context is within limit
        context = context[:10000]
    
    chain = get_conversational_chain_for_java()

    response = chain({
        "input_documents": docs, 
        "question": user_question,
        "solution": "",
        "explanation": ""
    }, return_only_outputs=True)
    
    return response

def app():
    with st.sidebar:
        st.title("Menu:")
        pdf_docs = st.file_uploader("Upload your PDF Files and click on the Submit & Process Button", accept_multiple_files=True)
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)
                st.success("Done")

    st.title("Java Code Trainer 🤖🌠")
    st.text("Introducing a Java code trainer powered by RAG! Ask any Java-related question,")
    st.text("and it will retrieve answers from your documents ")
    st.text("and provide detailed code explanations.")

    st.sidebar.button('Clear History', on_click=clear_chat_history)

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {"role": "assistant", "content": "Upload some PDFs and ask me a question."}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = user_input(prompt)
                placeholder = st.empty()
                full_response = ''
                for item in response['output_text']:
                    full_response += item
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
        if response is not None:
            message = {"role": "assistant", "content": full_response}
            st.session_state.messages.append(message)

if __name__ == "__main__":
    app()
