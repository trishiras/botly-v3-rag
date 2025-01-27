# **botly-v3**  


A Docker image for running [Ollama](https://ollama.com/) and [Streamlit](https://streamlit.io/) together, now enhanced with **FAISS**, **LangChain**, and **PDF processing** for advanced AI-powered interactions. This setup allows users to interact with an AI chatbot that can reference uploaded documents using **Retrieval-Augmented Generation (RAG)**, providing more context-aware and intelligent responses.



## **Features**  
✅ **PDF Integration** – Users can add a PDF document to the conversation  
✅ **Context-Aware AI** – Performs **RAG (Retrieval-Augmented Generation)** on provided documents  
✅ **Tag-Based Querying** – Using `@pdf` in a message triggers a **contextual response** based on the uploaded document  
✅ **Standard Chat Mode** – If no `@pdf` tag is used, the bot generates a normal response  
✅ **Streamlit-Based UI** – Interactive and user-friendly web interface  
✅ **FAISS-Powered Search** – Efficient similarity search for faster information retrieval  
✅ **Dockerized Deployment** – Easily deploy and run the bot with minimal setup  
   


## **Prerequisites**  
Ensure you have:  
- **Docker** installed: [Install Docker](https://docs.docker.com/get-docker/)  



## **Installation**  


### **1. Build the Docker Image**  
Run the following command to build the image without using cache:  
```sh
sudo docker build --no-cache . -f Dockerfile -t botly:latest
```  


### **2. Run the Container**  
Start `botly` using Docker:  
```sh
sudo docker run --dns 8.8.8.8 -p 8501:8501 -it botly:latest
```  

Once started, the application will be accessible at:  
👉 **http://localhost:8501**  



## **Stopping the Container**  
To stop the running container:  
```sh
sudo docker stop $(sudo docker ps -q --filter ancestor=botly:latest)
```  


## **Logs & Debugging**  
View live logs from the running container:  
```sh
sudo docker logs -f $(sudo docker ps -q --filter ancestor=botly:latest)
```  


## **Dependencies**  
This implementation includes the following libraries:  
- `faiss-cpu==1.10.0` → Fast similarity search  
- `streamlit==1.43.2` → Web-based UI framework  
- `pdfplumber==0.11.5` → PDF text extraction  
- `langchain-ollama==0.2.3` → LangChain support for Ollama models  
- `langchain-huggingface==0.1.2` → Integration with Hugging Face models  
- `langchain-experimental==0.3.4` → Experimental LangChain utilities  







## **License**  
This project is open-source and available under the [MIT License](LICENSE).  

---

### **🚀 HAPPY CODING! 🎉**  





