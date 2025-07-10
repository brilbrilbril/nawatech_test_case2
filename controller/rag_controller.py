from config.setting import env
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from utils.RAG_prompt import prompt_template
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.chat_history import InMemoryChatMessageHistory
import os 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class RAGController:
    def __init__(self):
        self.file_path = os.path.join(BASE_DIR, "dataset", "FAQ_Nawa.xlsx")
        self.faiss_index = os.path.join(BASE_DIR, "dataset_embedded", "faq_index")
        self.llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', temperature=0.1, google_api_key=env.google_api_key)
        self.prompt = prompt_template
        self.vectorstore = None
        self.retriever = None
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        self.rag_chain = None
        self.pipeline(faiss_index_path=self.faiss_index)
        self.history = {}
    
    # read documents using UnstructuredExcelLoader   
    def load_documents(self):
        try:
            loader = UnstructuredExcelLoader(file_path=self.file_path)
            documents = loader.load()
            return documents
        except Exception as e:
            raise Exception("Error occured in document loading")
    
    # split the documents into small chunks    
    def chunk_documents(self, docs):
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=100)
            chunks = text_splitter.split_documents(docs)
            return chunks
        except:
            raise Exception("Error occured in documents splitting")
    
    # create vector representation of the chunked documents, then store it
    def embed_chunks(self, chunks, faiss_index_path):
        try:
            self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
            self.vectorstore.save_local(faiss_index_path)
                
            self.retriever = self.vectorstore.as_retriever(search_kwargs={'k':3})
        except Exception as e:
            print(f"Error occured: {e}")

    # if the chunked document embedding already exists, then load it
    def load_index(self, path):
        try:
            self.vectorstore = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
            self.retriever = self.vectorstore.as_retriever(search_kwargs={'k':5})
        except Exception as e:
            print(f"Error occured: {e}")
    
    # create session for past chat conversation
    def _get_session_history(self, session_id: str=''):
        if session_id not in self.history:
            self.history[session_id] = InMemoryChatMessageHistory()
        return self.history[session_id]
    
    # full pipeline
    def pipeline(self, faiss_index_path):
        try:
            # process the documents
            if os.path.exists(faiss_index_path):
                print("embedding model exists")
                self.load_index(faiss_index_path)
            else:
                print("embedding model does not exist")
                docs = self.load_documents()
                split_docs = self.chunk_documents(docs)
                self.embed_chunks(split_docs, faiss_index_path)
        except:
            raise Exception("An error occured in pipeline building")
        
        # build chain (retriever, LLM, and its configuration)
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        # wrap the question, context retrieval, and chat history to dictionary
        def build_inputs(x):
            return {
                "question": x["question"],
                "chat_history": x["chat_history"],
                "context": format_docs(self.retriever.invoke(x["question"]))
            }
        
        chain = (
            RunnableLambda(build_inputs)
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        # final chain (add the chat history as additional context)
        self.rag_chain = RunnableWithMessageHistory(
            chain,
            self._get_session_history,
            input_messages_key="question",
            history_messages_key="chat_history",
        )
    
    # execute the chain
    def run(self, question:str, session_id:str):
        try:
            for chunk in  self.rag_chain.stream({'question':question},
                                            config={'configurable': {"session_id":session_id}}):
                yield chunk
        except:
            raise Exception("An error occured in invoking response")
    
    # delete whole chat history for certain session_id
    def _clear_session(self, session_id:str=''):
        if session_id in self.history:
            del self.history[session_id]
        else:
            raise Exception("Error occured: session_id does not exist")
        
