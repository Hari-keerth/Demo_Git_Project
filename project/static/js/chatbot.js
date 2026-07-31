


/*==========================================
        CHAT WIDGET
==========================================*/

// Floating Chat Button
const chatButton = document.getElementById("chat-button");

// Chat Window
const chatWidget = document.getElementById("chat-widget");

// Close Button
const closeButton = document.getElementById("close-chat");

// Ask Button
const askButton = document.getElementById("askBtn");

// Input Box
const questionInput = document.getElementById("question");

// Chat Area
const chatArea = document.getElementById("chatArea");

// Welcome Section
const welcomeSection = document.getElementById("welcome-section");


/*==========================================
        OPEN CHAT
==========================================*/

chatButton.addEventListener("click", function () {

    chatWidget.style.display = "flex";

    // Automatically place cursor in input box
    questionInput.focus();

});


/*==========================================
        CLOSE CHAT
==========================================*/

closeButton.addEventListener("click", function () {

    chatWidget.style.display = "none";

});


/*==========================================
        SCROLL TO BOTTOM
==========================================*/

function scrollToBottom() {

    chatArea.scrollTo({

        top: chatArea.scrollHeight,

        behavior: "smooth"

    });

}

/*==========================================
        TYPEWRITER EFFECT
==========================================*/

function typeWriter(element, text, speed = 15) {

    let index = 0;
    let currentText = "";

    function type() {

        if (index < text.length) {

            currentText += text.charAt(index);

            element.innerHTML = marked.parse(currentText);

            index++;

            scrollToBottom();

            setTimeout(type, speed);

        }

    }

    type();

}


/*==========================================
        SEND MESSAGE
==========================================*/

function sendMessage() {

    const question = questionInput.value.trim();

    if (question === "") {

        return;

    }

    // Hide welcome section after first message
    if (welcomeSection) {

        welcomeSection.style.display = "none";

    }

    // Disable Send Button
    askButton.disabled = true;

    // User Message
    chatArea.innerHTML += `
        <div class="user-message">
            ${question}
        </div>
    `;

    // Loading Message
    chatArea.innerHTML += `
        <div class="ai-message" id="loading">
            <div class = 'typing'>
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;

    scrollToBottom();

    // Clear Input
    questionInput.value = "";

    fetch(`/ask_ai/?question=${encodeURIComponent(question)}`)

        .then(response => response.json())

        .then(data => {

            // Enable Button
            askButton.disabled = false;

            // Remove Loading
            const loading = document.getElementById("loading");

            if (loading) {

                loading.remove();

            }

            // create empty AI message
            const aiMessage = document.createElement("div");
            aiMessage.className = "ai-message";
            chatArea.appendChild(aiMessage);

            // Small delay before typing starst

            setTimeout(function(){

                typeWriter(aiMessage, data.response);
            }, 500);

            scrollToBottom();

            // Focus back to input
            questionInput.focus();

        })

        .catch(error => {

            askButton.disabled = false;

            const loading = document.getElementById("loading");

            if (loading) {

                loading.remove();

            }

            chatArea.innerHTML += `
                <div class="ai-message">
                    ❌ Something went wrong. Please try again.
                </div>
            `;

            scrollToBottom();

            questionInput.focus();

            console.error(error);

        });

}


/*==========================================
        SEND BUTTON
==========================================*/

askButton.addEventListener("click", sendMessage);


/*==========================================
        ENTER KEY
==========================================*/

questionInput.addEventListener("keydown", function (event) {

    if (event.key === "Enter") {

        event.preventDefault();
        sendMessage();

    }

});


/*==========================================
        ESC KEY CLOSES CHAT
==========================================*/

document.addEventListener("keydown", function(event){

    if(event.key === "Escape"){

        chatWidget.style.display = "none";

    }

});