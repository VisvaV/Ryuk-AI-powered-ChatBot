Ryuk Chatbot
Ryuk is an AI-powered chatbot built using Flask, Gemini AI, and Retrieval-Augmented Generation (RAG) techniques. It allows users to upload documents (PDF, DOCX, TXT) and ask questions based on the content of those documents, with the chatbot providing context-aware responses. The project features a sleek, futuristic UI with glowing animations, a responsive chat interface, and robust document processing capabilities.
Features

Document Upload and Processing: Upload PDF, DOCX, or TXT files, which are processed into chunks and embedded using Sentence Transformers for context-aware responses.
Context-Aware Chat: Ask questions based on uploaded documents, and the chatbot retrieves relevant context using cosine similarity and embeddings.
Gemini AI Integration: Leverages Google's Gemini AI for generating natural language responses.
Futuristic UI: A dark-themed interface with glowing stars, floating bubbles, and a minimal loading animation.
Responsive Design: Works seamlessly across devices with a flexible layout.
Clear Chat Functionality: Easily clear the chat history and uploaded documents.
Error Handling: Robust logging and error handling for file processing and API calls.

Technologies Used
Backend

Flask: A lightweight Python web framework for handling routes, file uploads, and API endpoints.
Google Generative AI (Gemini): For generating responses based on user queries and document context.
Sentence Transformers: Specifically the all-MiniLM-L6-v2 model for generating embeddings of document chunks and user queries.
PyPDF2: For extracting text from PDF files.
python-docx: For extracting text from DOCX files.
NumPy and scikit-learn: For computing cosine similarity between embeddings.
python-dotenv: For managing environment variables (e.g., Gemini API key).
Logging: Built-in Python logging for debugging and error tracking.

Frontend

HTML/CSS/JavaScript: For the user interface and client-side logic.
Quicksand Font: A clean, modern font from Google Fonts for typography.
Custom Animations: CSS animations for glowing stars, floating bubbles, and a minimal loading indicator (three-dot wave animation).

Other Tools

Git and GitHub: For version control and hosting the repository.
Python Virtual Environment: For dependency management.

Project Structure
Ryuk-Chatbot/
├── app.py                 # Main Flask application
├── requirements.txt       # List of Python dependencies
├── static/
│   ├── css/
│   │   └── style.css      # Stylesheet with animations and layout
│   └── js/
│       └── script.js      # Client-side JavaScript for chat functionality
├── templates/
│   └── index.html         # Main HTML template for the UI
└── README.md              # Project documentation

How It Works
1. Document Processing and Embedding

File Upload: Users upload documents via the /upload endpoint. Supported formats are PDF, DOCX, and TXT.
Text Extraction:
PDFs are processed using PyPDF2 to extract text.
DOCX files are processed using python-docx.
TXT files are read with UTF-8 encoding, with a fallback to Latin-1 if UTF-8 fails.


Chunking: Extracted text is split into chunks of 1000 characters to manage large documents efficiently.
Embedding: Each chunk is converted into a vector embedding using the all-MiniLM-L6-v2 Sentence Transformer model. These embeddings are stored in memory for retrieval.

2. Context Retrieval

User Query Embedding: When a user asks a question, it’s converted into an embedding using the same Sentence Transformer model.
Cosine Similarity: The query embedding is compared to document chunk embeddings using cosine similarity to find the top 3 most relevant chunks.
Context Selection: If the similarity score is above a threshold (0.1), the relevant chunks are used as context. For summary requests, all document content is used.

3. Response Generation

Prompt Engineering: A structured prompt is created with a system instruction, context, and user question.
Gemini AI: The prompt is sent to the Gemini API (gemini-1.5-flash model), which generates a response.
Response Display: The response is returned to the frontend and displayed in the chat interface.

4. Frontend Interaction

Chat Interface: Users type questions in an input field and press "Send" or Enter to submit.
Loading Animation: A minimal three-dot wave animation appears while waiting for the response.
Dynamic Updates: JavaScript dynamically appends user and bot messages to the chat box, scrolling to the bottom automatically.
Clear Chat: A "Clear" button resets the chat history and backend context.

Screenshots
![Alt text](screenshots/ss1.png)

Python 3.8 or higher
Git
A Gemini API key (sign up at Google Cloud to obtain one)

Steps

Clone the Repository:
git clone https://github.com/your-username/Ryuk-Chatbot.git
cd Ryuk-Chatbot


Set Up a Virtual Environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:
pip install -r requirements.txt


Configure Environment Variables:

Create a .env file in the project root:echo "GEMINI_API_KEY=your_api_key_here" > .env

Replace your_api_key_here with your actual Gemini API key.


Run the Application:
python app.py


The app will start on http://localhost:5000.


Access the App:

Open your browser and go to http://localhost:5000.
You’ll see the Ryuk Chatbot interface with the "Ryuk" title and logo at the top-left.



Usage

Upload a Document:

Click the upload button (paperclip icon) in the input section.
Select a PDF, DOCX, or TXT file.
A confirmation alert will appear if the file is processed successfully.


Ask a Question:

Type your question in the input field (e.g., "Summarize the uploaded document" or "What is the main topic?").
Press the "Send" button or hit Enter.
The chatbot will respond based on the document context or general knowledge if no relevant context is found.


Clear Chat:

Click the "Clear" button to reset the chat history and uploaded documents.



Implementation Details
Backend (app.py)

Flask Setup:
The Flask app is initialized with a 16MB file upload limit and an uploads directory for storing files temporarily.
Routes include / (renders the main page), /upload (handles file uploads), /chat (processes user questions), and /clear (resets chat history).


Document Processing:
Text is extracted using PyPDF2 (PDF), python-docx (DOCX), or file reading (TXT).
Text is split into 1000-character chunks to handle large documents.
The all-MiniLM-L6-v2 Sentence Transformer model generates embeddings for each chunk.


Context Retrieval:
User questions are embedded and compared to document embeddings using cosine similarity.
The top 3 chunks with similarity scores above 0.1 are used as context.


Gemini API:
A structured prompt with system instructions, context, and the user question is sent to the Gemini API.
Responses are returned in Markdown format for clarity.



Frontend (index.html, style.css, script.js)

HTML Structure:
The index.html file contains a header with the "Ryuk" title and logo, a chat container, an input section, and a footer.


CSS Styling:
A dark theme with a grid-patterned background and glowing animations (stars and bubbles).
Messages have gradient backgrounds and hover effects.
The loading animation is a minimal three-dot wave in teal (#48CFCB).


JavaScript:
Handles user input, file uploads, and chat updates.
Uses fetch API to communicate with Flask endpoints.
Dynamically appends messages and scrolls the chat box to the bottom.


Limitations

In-Memory Storage: Document chunks and embeddings are stored in memory, so they’re lost on server restart. A database could be added for persistence.
File Size Limit: Limited to 16MB due to Flask configuration.
Gemini API Dependency: Requires a valid Gemini API key and internet access.
No Authentication: The app doesn’t include user authentication or session management.

Future Improvements

Add a database (e.g., SQLite) to store documents and embeddings persistently.
Implement user authentication and session management.
Add support for more file formats (e.g., images with OCR).
Enhance the UI with theme customization options.
Improve error handling with user-friendly messages.

Contributing
Contributions are welcome! Please follow these steps:
Fork the repository.
Create a new branch: git checkout -b feature-name.
Make your changes and commit: git commit -m "Add feature-name".
Push to your branch: git push origin feature-name.
Open a pull request with a detailed description of your changes.

License
This project is licensed under the MIT License. See the LICENSE file for details.
