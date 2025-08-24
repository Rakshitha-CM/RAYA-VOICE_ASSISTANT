let recognition;
let isListening = false;

// Initialize Speech Recognition
try {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.continuous = true; // Allows continuous listening
} catch (error) {
    console.error("Speech Recognition API not supported in this browser.");
    alert("Speech Recognition is not supported in your browser.");
}

// Add event listeners to buttons
document.getElementById('submitBtn').addEventListener('click', () => {
    const commandInput = document.getElementById('commandInput').value.trim();
    if (commandInput) {
        sendCommand(commandInput);
    } else {
        alert("Please enter a command.");
    }
});

document.getElementById('startListening').addEventListener('click', startListening);
document.getElementById('stopListening').addEventListener('click', stopListening);

// Function to send command to the backend
function sendCommand(command) {
    fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command }),
    })
        .then(response => response.json())
        .then(data => {
            // Display the response from the backend
            document.getElementById('responseOutput').textContent = data.response;
        })
        .catch(error => {
            console.error("Error sending command:", error);
            document.getElementById('responseOutput').textContent = "Failed to send command.";
        });
}

// Function to start listening
function startListening() {
    if (recognition && !isListening) {
        isListening = true;
        recognition.start();
        document.getElementById('responseOutput').textContent = "Listening...";

        recognition.onresult = (event) => {
            const command = event.results[event.results.length - 1][0].transcript;
            document.getElementById('commandInput').value = command; // Autofill the command input
            sendCommand(command); // Send command automatically
        };

        recognition.onend = () => {
            if (isListening) {
                recognition.start(); // Restart listening automatically
            }
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
        };
    }
}

// Function to stop listening
function stopListening() {
    if (recognition && isListening) {
        isListening = false;
        recognition.stop();
        document.getElementById('responseOutput').textContent = "Stopped listening.";
    }
}
