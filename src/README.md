<img src="https://cdn.prod.website-files.com/677c400686e724409a5a7409/6790ad949cf622dc8dcd9fe4_nextwork-logo-leather.svg" alt="NextWork" width="300" />

# Build a RAG API with FastAPI

**Project Link:** [View Project](http://learn.nextwork.org/projects/ai-devops-api)

**Author:** Akinpelu Shuaib  
**Email:** akinpelushuaib0@gmail.com

---

![Image](http://learn.nextwork.org/merry_lavender_calm_mango/uploads/ai-devops-api_g3h4i5j6)

---

## Introducing Today's Project!

In this project, I will demonstrate... I'm doing this project to learn about RAG and how API's work more

### Key services and concepts

Services I used were fastAPI Chromadb etc. Key concepts I learnt include HTTP and terminal commands

### Challenges and wins

This project took me approximately2 days The most challenging part was the ollama set up.It was most rewarding to grow and understand how RAG works

### Why I did this project

I did this project because i am trying to improve my skill and grow as a programmer 

---

## Setting Up Python and Ollama

In this step, I'm setting up Python and Ollama. Python is... Ollama is... I need these tools because these are the tools i will be using to create our RAG API 

### Python and Ollama setup

![Image](http://learn.nextwork.org/merry_lavender_calm_mango/uploads/ai-devops-api_i9j0k1l2)

### Verifying Python is working

### Ollama and tinyllama ready

Ollama is a tool that lets you run large language models locally on your own computer. Instead of sending requests to cloud services like OpenAI or Anthropic, Ollama runs the AI model directly on your machine. I downloaded the tinyllama model because it is a light weight LLM that can run on my laptop with no GPU and tinyllama is great for learning. The model will help my RAG API by being the brain for our RAG system.

---

## Setting Up a Python Workspace

In this step, I'm setting up our Python Workspace I need it because this where we will be writting out python script using fastAPI which we will be using to send request to ollama

### Python workspace setup

### Virtual environment

💡 What is a virtual environment?
A virtual environment is an isolated Python environment that keeps your project's dependencies separate from other Python projects on your computer.

Without a virtual environment, installing packages for one project could break another project that needs a different version. A virtual environment makes sure each project has its own set of packages, preventing conflicts.


💡 How does it work?
When you create a virtual environment, Python creates a folder (usually called venv) that contains its own copy of Python and a place to install packages. When you "activate" the virtual environment, your terminal uses the Python and packages from that folder instead of the system-wide Python.

### Dependencies

T

![Image](http://learn.nextwork.org/merry_lavender_calm_mango/uploads/ai-devops-api_u1v2w3x4)

---

## Setting Up a Knowledge Base

In this step, I'm creating a knowledge base. I need it because our model which tinyllama has limited training so we need the knowledge as a refrence for our LLM to give better answers.

### Knowledge base setup

![Image](http://learn.nextwork.org/merry_lavender_calm_mango/uploads/ai-devops-api_t1u2v3w4)

### Embeddings created

💡 What are embeddings?
Embeddings are numerical representations of text that capture meaning. Words with similar meanings are placed close together, while unrelated words are far apart. For example, "container" and "Docker" would have embeddings that are mathematically similar. This allows the computer to understand relationships between words based on their meaning, not just spelling.


💡 How do embeddings work in RAG?
When you ask "What is Kubernetes?", the system:





Converts your question into an embedding (a list of vectors)



Compares it to embeddings of all text in your knowledge base



Finds the text with the most similar embedding (meaning)



Uses that text as context for generating the answer

This is much more powerful than keyword matching - it understands meaning!

---

## Building the RAG API

In this step, I'm building a RAG API. An API is means Application Programming Interface which allow software to interact with one another. FastAPI is a python modern web framework used for building API"s I'm creating this because i want to make the tinyollama to interact with our Chromadb to get refrence in other to improve response.

### FastAPI setup

### How the RAG API works

💡 How does this RAG API work?
This FastAPI app creates a web server with one endpoint: /query. Here's how your API works, step by step:





Question arrives: Someone sends a question to your API at /query



Search your documents: Chroma searches through your knowledge base to find text that matches the question's meaning



Get matching text: Chroma returns the most relevant information from your documents (this is called "context")



Generate answer: The question and the matching text are sent together to tinyllama, which creates an answer



Send back the answer: The answer is sent back to whoever asked the question

![Image](http://learn.nextwork.org/merry_lavender_calm_mango/uploads/ai-devops-api_f3g4h5i6)

---

## Testing the RAG API

In this step, I'm testing my RAG API. I'll test it using Swagger UI is an automatically generated, interactive documentation page for your FastAPI server. It lets you visually explore your API's endpoints, see what parameters they accept, and even try them out right from your browser - no special tools or coding required.

### Testing the API

### API query breakdown

I queried my API through Swagger UI 

![Image](http://learn.nextwork.org/merry_lavender_calm_mango/uploads/ai-devops-api_g3h4i5j6)

### Swagger UI exploration

Swagger UI is an open-source tool that automatically generates interactive, browser-based documentation for RESTful APIs based on the OpenAPI Specification. It allows developers to visualize, document, and test API endpoints directly in a web browser without needing to write backend code or use external tools like Postman. 
Key features and benefits of Swagger UI include:
Interactive Documentation: Users can "try it out" by inputting parameters and seeing live, real-time responses from the API.
Automatic Generation: It renders API specifications (JSON or YAML) into a clean, easy-to-read web interface.
Dependency-Free & Flexible: It runs in any environment (local or browser) and works with any API that has an OpenAPI definition.
Improved Collaboration: Bridges the gap between backend developers and consumers, reducing support tickets and simplifying integration. 

---

## Adding Dynamic Content

### Adding the /add endpoint

### Dynamic content endpoint working

---

---
