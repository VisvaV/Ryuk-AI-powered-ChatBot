document.addEventListener('DOMContentLoaded', () => {
    // Generate Stars
    for (let i = 0; i < 50; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        star.style.top = `${Math.random() * 100}%`;
        star.style.left = `${Math.random() * 100}%`;
        star.style.animationDelay = `${Math.random() * 10}s`;
        document.body.appendChild(star);
    }

    // Generate Glowing Bubbles
    for (let i = 0; i < 15; i++) {
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        bubble.style.width = `${Math.random() * 20 + 10}px`;
        bubble.style.height = bubble.style.width;
        bubble.style.left = `${Math.random() * 100}%`;
        bubble.style.animationDelay = `${Math.random() * 15}s`;
        document.body.appendChild(bubble);
    }

    // Add Enter key listener for sending messages
    const userInput = document.getElementById('user-input');
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });
});

// Function to upload a file
function uploadFile() {
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a file to upload.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
        } else {
            alert('File uploaded successfully!');
        }
    })
    .catch(error => {
        console.error('Error uploading file:', error);
        alert('An error occurred while uploading the file.');
    });
}

// Function to send a message
function sendMessage() {
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const message = userInput.value.trim();

    if (!message) {
        alert('Please enter a message.');
        return;
    }

    // Display user message
    const userMessage = document.createElement('div');
    userMessage.className = 'message user-message';
    userMessage.textContent = message;
    chatBox.appendChild(userMessage);

    // Clear input
    userInput.value = '';

    // Scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;

    // Add loading bubble
    const loadingBubble = document.createElement('div');
    loadingBubble.className = 'message bot-message loading';
    chatBox.appendChild(loadingBubble);

    // Send message to Flask backend
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: message })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(`HTTP error! Status: ${response.status}, Message: ${err.error || 'Unknown error'}`);
            });
        }
        return response.json();
    })
    .then(data => {
        // Remove loading bubble
        loadingBubble.remove();

        // Display bot response
        const botMessage = document.createElement('div');
        botMessage.className = 'message bot-message';
        botMessage.textContent = data.answer || 'Sorry, I could not process your request.'; // Changed 'data.response' to 'data.answer'
        chatBox.appendChild(botMessage);

        // Scroll to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        console.error('Error sending message:', error);
        loadingBubble.remove();
        const errorMessage = document.createElement('div');
        errorMessage.className = 'message bot-message';
        errorMessage.textContent = `An error occurred: ${error.message}`;
        chatBox.appendChild(errorMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
    });
}

// Function to clear the chat
function clearChat() {
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = '';
}