document.addEventListener("DOMContentLoaded", () => {

    const chatbot = document.getElementById("chatbot");

    if (!chatbot) return;

    /* ==========================================================
       ELEMENTS
    ========================================================== */

    const chatButton = chatbot.querySelector("#chat-button");
    const chatWindow = chatbot.querySelector(".chat-window");
    const closeButton = chatbot.querySelector("#close-chat");
    const sendButton = chatbot.querySelector(".chat-send");
    const questionInput = chatbot.querySelector("#question");
    const chatBody = chatbot.querySelector(".chat-body");
    const welcomeSection = chatbot.querySelector("#welcome-section");

    /* ==========================================================
       OPEN CHAT
    ========================================================== */

    function openChat() {

        chatbot.classList.add("show");

        questionInput.focus();

    }

    /* ==========================================================
       CLOSE CHAT
    ========================================================== */

    function closeChat() {

        chatbot.classList.remove("show");

    }

    /* ==========================================================
       EVENTS
    ========================================================== */

    chatButton.addEventListener("click", openChat);

    closeButton.addEventListener("click", closeChat);

    /* ==========================================================
       SCROLL
    ========================================================== */

    function scrollBottom() {

        chatBody.scrollTop = chatBody.scrollHeight;

    }

    /* ==========================================================
       USER MESSAGE
    ========================================================== */

    function addUserMessage(message) {

        const div = document.createElement("div");

        div.className = "user-message";

        div.textContent = message;

        chatBody.appendChild(div);

        scrollBottom();

    }

    /* ==========================================================
       AI MESSAGE
    ========================================================== */

    function addAIMessage(html) {

        const div = document.createElement("div");

        div.className = "ai-message";

        div.innerHTML = marked.parse(html);

        chatBody.appendChild(div);

        scrollBottom();

    }

    /* ==========================================================
       TYPING
    ========================================================== */

    function showTyping() {

        const typing = document.createElement("div");

        typing.className = "ai-message";

        typing.id = "typing-indicator";

        typing.innerHTML = `
            <div class="typing">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;

        chatBody.appendChild(typing);

        scrollBottom();

    }

    function hideTyping() {

        const typing = chatbot.querySelector("#typing-indicator");

        if (typing) {

            typing.remove();

        }

    }

    /* ==========================================================
       TYPEWRITER
    ========================================================== */

    async function typeWriter(element, text, speed = 12) {

        let output = "";

        for (const char of text) {

            output += char;

            element.innerHTML = marked.parse(output);

            scrollBottom();

            await new Promise(resolve => setTimeout(resolve, speed));

        }

    }

    /* ==========================================================
       SEND
    ========================================================== */

    async function sendMessage() {

        const question = questionInput.value.trim();

        if (!question) return;

        if (welcomeSection) {

            welcomeSection.style.display = "none";

        }

        addUserMessage(question);

        questionInput.value = "";

        sendButton.disabled = true;

        sendButton.classList.add("loading");

        showTyping();

        try {

            const response = await fetch(

                `/ask_ai/?question=${encodeURIComponent(question)}`

            );

            const data = await response.json();

            hideTyping();

            const ai = document.createElement("div");

            ai.className = "ai-message";

            chatBody.appendChild(ai);

            await typeWriter(ai, data.response);

        }

        catch (error) {

            hideTyping();

            addAIMessage(

                "❌ Something went wrong. Please try again."

            );

            console.error(error);

        }

        finally {

            sendButton.disabled = false;

            sendButton.classList.remove("loading");

            questionInput.focus();

        }

    }

    /* ==========================================================
       BUTTON
    ========================================================== */

    sendButton.addEventListener("click", sendMessage);

    /* ==========================================================
       ENTER
    ========================================================== */

    questionInput.addEventListener("keydown", e => {

        if (e.key === "Enter") {

            e.preventDefault();

            sendMessage();

        }

    });

    /* ==========================================================
       ESC
    ========================================================== */

    document.addEventListener("keydown", e => {

        if (e.key === "Escape") {

            closeChat();

        }

    });

});