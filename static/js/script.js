document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const micButton = document.getElementById('mic-button');
    const startupScreen = document.getElementById('startup-screen');
    
    // JARVIS startup sequence
    setTimeout(() => {
        document.querySelector('.startup-status').textContent = "SYSTEMS ONLINE";
        setTimeout(() => {
            startupScreen.style.opacity = '0';
            setTimeout(() => {
                startupScreen.style.display = 'none';
                // Focus on input after startup
                userInput.focus();
            }, 1000);
        }, 500);
    }, 3000);
    
    // Initialize speech recognition
    let recognition = null;
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.continuous = false;
        recognition.lang = 'en-US';
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            playActivationSound();
            sendMessage();
        };
        
        recognition.onend = function() {
            micButton.classList.remove('listening');
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error', event.error);
            micButton.classList.remove('listening');
            playErrorSound();
        };
    }
    
    // Sound effects
    function playActivationSound() {
        const audio = new Audio('/static/sounds/activate.mp3');
        audio.volume = 0.3;
        audio.play().catch(e => console.log('Audio play error:', e));
    }
    
    function playMessageSound() {
        const audio = new Audio('/static/sounds/message.mp3');
        audio.volume = 0.2;
        audio.play().catch(e => console.log('Audio play error:', e));
    }
    
    function playErrorSound() {
        const audio = new Audio('/static/sounds/error.mp3');
        audio.volume = 0.2;
        audio.play().catch(e => console.log('Audio play error:', e));
    }
    
    // Initial greeting from JARVIS with typing effect
    fetch('/get_initial_greeting')
        .then(response => response.json())
        .then(data => {
            setTimeout(() => {
                addTypingEffect(data.greeting);
            }, 3500); // Delay initial greeting to happen after startup
        });
    
    // Event listeners
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    sendButton.addEventListener('click', sendMessage);
    
    if (recognition) {
        micButton.addEventListener('click', function() {
            if (micButton.classList.contains('listening')) {
                recognition.stop();
            } else {
                playActivationSound();
                recognition.start();
                micButton.classList.add('listening');
            }
        });
    } else {
        micButton.style.display = 'none';
    }
    
    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        addMessage(message, 'user');
        playMessageSound();
        userInput.value = '';
        
        // Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = '<span></span><span></span><span></span>';
        chatContainer.appendChild(typingIndicator);
        scrollToBottom();
        
        // Simulate JARVIS "thinking"
        setTimeout(() => {
            // Send to backend
            fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            })
            .then(response => response.json())
            .then(data => {
                // Remove typing indicator
                typingIndicator.remove();
                
                // Add assistant response with typing effect
                addTypingEffect(data.response);
                
                // Speak the response if speech synthesis is available
                if ('speechSynthesis' in window) {
                    const speech = new SpeechSynthesisUtterance(data.response);
                    speech.lang = 'en-US';
                    // Get a slightly electronic female voice if available
                    const voices = window.speechSynthesis.getVoices();
                    for (let i = 0; i < voices.length; i++) {
                        if (voices[i].name.includes('Google UK English Female') || 
                            voices[i].name.includes('Microsoft Zira')) {
                            speech.voice = voices[i];
                            break;
                        }
                    }
                    speech.pitch = 1;
                    speech.rate = 1;
                    window.speechSynthesis.speak(speech);
                }
            })
            .catch(error => {
                typingIndicator.remove();
                console.error('Error:', error);
                addMessage('System error detected. Please try again.', 'assistant');
                playErrorSound();
            });
        }, 1000); // Simulate thinking time
    }
    
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.textContent = text;
        
        const timeSpan = document.createElement('div');
        timeSpan.className = 'message-time';
        const now = new Date();
        timeSpan.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.appendChild(timeSpan);
        chatContainer.appendChild(messageDiv);
        scrollToBottom();
    }
    
    function addTypingEffect(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message';
        chatContainer.appendChild(messageDiv);
        
        let i = 0;
        const typingSpeed = 30; // ms per character
        
        const typeWriter = () => {
            if (i < text.length) {
                messageDiv.textContent += text.charAt(i);
                i++;
                scrollToBottom();
                setTimeout(typeWriter, typingSpeed);
            } else {
                // Add timestamp after typing is complete
                const timeSpan = document.createElement('div');
                timeSpan.className = 'message-time';
                const now = new Date();
                timeSpan.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                messageDiv.appendChild(timeSpan);
            }
        };
        
        // Start typing
        typeWriter();
    }
    
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Add dynamic HUD elements
    function animateHudElements() {
        const hudElements = document.querySelectorAll('.hud-element');
        hudElements.forEach(element => {
            element.style.transform = `rotate(${Math.random() * 360}deg)`;
            setTimeout(() => {
                element.style.transition = 'transform 30s linear';
                element.style.transform = `rotate(${Math.random() * 360 + 720}deg)`;
            }, 100);
        });
        
        // Update power level randomly
        const powerLevel = document.querySelector('.power-level');
        setInterval(() => {
            const level = 70 + Math.random() * 30; // Between 70-100%
            powerLevel.style.width = `${level}%`;
        }, 5000);
    }
    
    // Start HUD animations
    setTimeout(animateHudElements, 4000);
});