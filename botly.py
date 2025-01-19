from core.logging import logger
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.document_loaders import PDFPlumberLoader


class Botly:
    def __init__(self):
        """
        Initialize the Botly class.

        This method sets the following attributes:
        - llm: The Ollama model instance.
        - reply: The response to the user.
        - cache: Whether to cache the responses.
        - verbose: Whether to log responses.
        - keep_alive: The time in seconds to keep the Ollama model instance.
        - diverse_text: The diversity of the text.
        - diversety_index: The number of tokens to generate.
        - creativity_index: The creativity of the response.
        - tokens_to_generate: The number of tokens to generate.
        - llm_model: The name of the language model.
        - base_url: The base URL of the Ollama model.
        - vector_search_type: The type of vector search to use.
        - vector_search_kwargs: The keyword arguments for the vector search.
        - normal_messages: The list of user messages.
        - rag_messages: The list of RAG messages.
        - normal_prompt: The prompt template for normal messages.
        - rag_prompt: The prompt template for RAG messages.
        - normal_chain: The LangChain pipeline for normal messages.
        - rag_chain: The LangChain pipeline for RAG messages.
        - documents: The list of documents.
        - formated_context_documents: The formatted context documents.
        - vector_store: The FAISS vector store.
        - have_document: Whether there is a document to use for RAG.
        - embeddings: The HuggingFace embeddings.
        """
        self.llm = None
        self.reply = ""
        self.cache = False
        self.verbose = False
        self.keep_alive = 300
        self.diverse_text = 0.9
        self.diversety_index = 40
        self.creativity_index = 0.8
        self.tokens_to_generate = 256
        self.llm_model = "qwen2.5:3b"
        self.base_url = "http://localhost:11434"
        self.vector_search_type = "similarity"
        self.vector_search_kwargs = {
            "k": 3,  ## it will help fetch top 3 docs only
        }
        self.normal_messages = []
        self.rag_messages = []
        self.normal_prompt = None
        self.rag_prompt = None
        self.normal_chain = None
        self.rag_chain = None
        self.documents = None
        self.formated_context_documents = None
        self.vector_store = None
        self.have_document = False
        self.embeddings = HuggingFaceEmbeddings()
        self.run()

    def initialize_ollama(self):  #
        """
        Initialize the llm model.

        This method will create a new instance of the ChatOllama class
        and set it as the llm attribute of the class.

        """

        ## llm model initialization
        self.llm = ChatOllama(
            model=self.llm_model,
            top_k=self.diversety_index,
            top_p=self.diverse_text,
            cache=self.cache,
            verbose=self.verbose,
            keep_alive=self.keep_alive,
            temperature=self.creativity_index,
            num_predict=self.tokens_to_generate,
            base_url=self.base_url,
        )

    def prompt_generator(self):  #
        """
        Generate the prompt template for the language model.

        This method sets up the initial messages for the ChatPromptTemplate,
        which serves as the conversation context. The system message defines
        the assistant's behavior, while the user message is a placeholder for
        user input.

        """

        logger.info("Adding normal prompt template instructions...")
        self.normal_messages = [
            (
                "system",
                "You are a helpful assistant. Always answer as short as possible. You are a text-based AI assistant created by Sumit kumar to help with questions and tasks.",
            ),
            ("user", "{input_message}"),
        ]

        logger.info("Creating normal prompt template...")
        self.normal_prompt = ChatPromptTemplate.from_messages(self.normal_messages)

        logger.info("Adding rag prompt template instructions...")
        self.rag_messages = [
            (
                "system",
                """
                You are a text-based AI assistant created by Sumit kumar to help with questions and tasks.
                You are a specialized retrieval-augmented generation assistant trained to analyze documents and provide precise, evidence-based answers. 
                Your responses should:
                1. Be concise and directly address the question
                2. Reference specific sections or quotes from the provided document
                3. Indicate when information is uncertain or not found in the document
                4. Maintain proper context from the document even when fragments are provided
                5. Format responses for readability with key points highlighted
                6. Avoid hallucinating information not present in the context
                """,
            ),
            (
                "human",
                """Document Context:\n{context}\n\n
                Question: {question}\n\n
                Provide a focused answer based exclusively on the information in the document context. 
                If the context doesn't contain relevant information, acknowledge the limitation.""",
            ),
        ]
        ## rag prompt
        logger.info("Creating rag prompt template...")
        self.rag_prompt = ChatPromptTemplate.from_messages(self.rag_messages)

    def lang_chain_generator(self):  #
        """
        Initialize the LangChain chain.

        This method takes the prompt template and language model and chains
        them together to form the LangChain pipeline. The RunnablePassthrough
        node assigns the user's input to a variable called "input_message",
        which is then passed to the prompt template. The output of the
        prompt template is then passed to the language model, and the output
        of the language model is then passed to the StrOutputParser.

        """

        ## normal chain initialization
        self.normal_chain = (
            RunnablePassthrough.assign(
                input_message=lambda input_dict: input_dict["context"],
            )
            | self.normal_prompt
            | self.llm
            | StrOutputParser()
        )

        ## rag chain initialization
        self.rag_chain = (
            RunnablePassthrough.assign(
                context=lambda input_dict: input_dict["context"]
            ).assign(question=lambda input_dict: input_dict["question"])
            | self.rag_prompt
            | self.llm
            | StrOutputParser()
        )

    def format_documents(self, documents):  #
        """
        Format the documents into a single string.

        This method concatenates the page content of each document in the
        documents list, separating them with two newline characters, and assigns
        the result to the formated_documents attribute.
        """

        ##
        self.formated_context_documents = "\n\n".join(
            document.page_content for document in documents
        )

    def document_consumer(
        self,
        file_path: str,
    ):  #
        """
        Document consumer method.

        This method takes a file path as input and generates a semantically
        split document list. It first loads the document using the PDFPlumber
        loader, and then splits the document into chunks using the Semantic
        Chunker.

        Args:
            file_path (str): The path to the file to consume.

        Returns:
            None
        """

        ##
        logger.info("Consuming document...")
        loader = PDFPlumberLoader(
            file_path=file_path,
        )
        doc_list = loader.load()

        ##
        logger.info("Splitting document list semanticaly...")
        semantic_splitter = SemanticChunker(
            embeddings=self.embeddings,
        )
        self.documents = semantic_splitter.split_documents(
            documents=doc_list,
        )

    def vector_store_generator(self):
        """
        Initialize the vector store from the formatted documents.

        This method takes the documents list and uses the HuggingFace
        embeddings to generate a vector store. The vector store is then
        assigned to the vector_store attribute.

        Returns:
            None
        """

        ##
        logger.info("Creating vector store...")
        self.vector_store = FAISS.from_documents(
            documents=self.documents,
            embedding=self.embeddings,
        )

    def context_generator(self, query):
        """
        Generate the context for RAG.

        This method takes a query as input and uses the vector store to
        retrieve relevant documents. It then formats the retrieved documents
        into a single string and assigns the result to the formated_documents
        attribute.

        Args:
            query (str): The query to use for retrieval-augmented generation.

        Returns:
            None
        """

        ##
        logger.info("Adding retriever parameters")
        retriever = self.vector_store.as_retriever(
            search_type=self.vector_search_type,
            search_kwargs=self.vector_search_kwargs,
        )

        ##
        documents = retriever.invoke(query)
        self.format_documents(
            documents=documents,
        )

    def botly_reply(self, query):
        """
        Generate a response based on the user query.

        This method takes a query as input and checks if the query contains
        "@pdf". If it does, it uses the context_generator method to generate
        the context for RAG and uses the RAG chain to generate a response.
        Otherwise, it uses the normal chain to generate a response.

        Args:
            query (str): The query to use for response generation.

        Returns:
            str: The response generated by the bot.
        """

        ##
        query = query.lower()
        self.reply = ""

        logger.info("Generating response...")
        if "@pdf" in query:
            logger.info("Generating RAG response...")
            if not self.have_document:
                self.reply = (
                    "Sorry, I cannot find any attached PDF to this conversation."
                )
            else:
                self.context_generator(
                    query=query,
                )
                self.reply = self.rag_chain.invoke(
                    {
                        "context": self.formated_context_documents,
                        "question": query,
                    }
                )
        else:
            logger.info("Generating normal response...")
            self.reply = self.normal_chain.invoke(
                {
                    "context": query,
                }
            )

        return self.reply

    def run(self):
        """
        Initialize the Botly model.

        This method initializes the Botly model by first initializing the
        Ollama model, then generating the prompt template, and finally
        setting up the LangChain pipeline.

        Returns:
            None
        """

        ## initialize ollama
        logger.info("Botly V2 is initializing...")
        logger.info("Initializing Ollama...")
        self.initialize_ollama()

        ## prompt template
        logger.info("Initializing prompt template...")
        self.prompt_generator()

        ## langchain creation
        logger.info("Initializing LangChain...")
        self.lang_chain_generator()


if __name__ == "__main__":
    Botly()
    logger.info("Botly V2 is Stopping...")
