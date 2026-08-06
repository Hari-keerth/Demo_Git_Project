/*=========================================================
 CareerGrowza AI Mock Interview
 interview.js
 Reorganized into modules. Same IDs, same endpoints, same
 payload shapes, same behavior as before -- only the file
 layout changed, plus a new Module 3 (role search) to match
 the #jobRole input that replaced the old <select>.
=========================================================*/

"use strict";

/*=========================================================
    MODULE 1 — DOM
=========================================================*/

const setupSection = document.getElementById("setupSection");
const interviewSection = document.getElementById("interviewSection");
const reportSection = document.getElementById("reportSection");

const questionNo = document.getElementById("questionNo");
const questionText = document.getElementById("question");

const answerBox = document.getElementById("answer");

const timer = document.getElementById("timer");

const progressFill = document.getElementById("progressFill");
const progressPercent = document.getElementById("progressPercent");
const progressText = document.getElementById("progressText");

const difficultyBadge = document.getElementById("difficultyBadge");
const difficultyText = document.getElementById("difficultyText");

const roleText = document.getElementById("roleText");
const sidebarDifficulty = document.getElementById("sidebarDifficulty");
const sidebarQuestions = document.getElementById("sidebarQuestions");

const wordCount = document.getElementById("wordCount");

const jobRoleInput = document.getElementById("jobRole");
const roleSearchBox = document.getElementById("roleSearchBox");
const roleSearchResults = document.getElementById("roleSearchResults");


/*=========================================================
    MODULE 2 — INTERVIEW STATE
=========================================================*/

let currentQuestion = 0;
let totalQuestions = 0;

let role = "";
let difficulty = "";

let questions = [];
let answers = [];

let timerInterval = null;
let remainingSeconds = 1800; // 30 minutes


/*=========================================================
    MODULE 3 — ROLE SEARCH (search + autocomplete)
    New: #jobRole is now a text input instead of a <select>,
    backed by this searchable suggestion list. startInterview()
    still just reads jobRoleInput.value, so nothing downstream
    changed.
=========================================================*/

const ROLE_SUGGESTIONS = [];

let roleActiveIndex = -1;

function renderRoleSuggestions(matches) {

    roleSearchResults.innerHTML = "";

    if (!matches.length) {

        const customRole = jobRoleInput.value.trim();

        if (customRole !== "") {

            const item = document.createElement("div");

            item.className = "search-item";

            item.innerHTML = `
                <strong>Use custom role:</strong><br>
                ${customRole}
            `;

            item.addEventListener("mousedown", (e) => {
                e.preventDefault();
                selectRole(customRole);
            });

            roleSearchResults.innerHTML = "";
            roleSearchResults.appendChild(item);
            roleSearchResults.classList.remove("hidden");

        } else {

            roleSearchResults.classList.add("hidden");

        }

        return;
    }

    matches.forEach((role, index) => {

        const item = document.createElement("div");

        item.className = "search-item";
        item.textContent = role;
        item.dataset.index = index;

        item.addEventListener("mousedown", (e) => {
            // mousedown (not click) so it fires before the input's blur
            e.preventDefault();
            selectRole(role);
        });

        roleSearchResults.appendChild(item);

    });

    roleActiveIndex = -1;
    roleSearchResults.classList.remove("hidden");

}

function getFilteredRoles() {

    const query = jobRoleInput.value.trim().toLowerCase();

    if (!query) return ROLE_SUGGESTIONS;

    return ROLE_SUGGESTIONS.filter(role =>
        role.toLowerCase().includes(query)
    );

}

function selectRole(role) {
    jobRoleInput.value = role;
    roleSearchResults.classList.add("hidden");
    roleActiveIndex = -1;
}

function highlightRole(index) {

    const items = roleSearchResults.querySelectorAll(".search-item");

    items.forEach(item => item.classList.remove("active"));

    if (index >= 0 && index < items.length) {
        items[index].classList.add("active");
        items[index].scrollIntoView({ block: "nearest" });
    }

}

if (jobRoleInput && roleSearchResults) {

    jobRoleInput.addEventListener("focus", () => {
        renderRoleSuggestions(getFilteredRoles());
    });

    jobRoleInput.addEventListener("input", () => {
        renderRoleSuggestions(getFilteredRoles());
    });

    jobRoleInput.addEventListener("keydown", (e) => {

        const items = roleSearchResults.querySelectorAll(".search-item");

        if (!items.length) return;

        if (e.key === "ArrowDown") {
            e.preventDefault();
            roleActiveIndex = Math.min(roleActiveIndex + 1, items.length - 1);
            highlightRole(roleActiveIndex);
        }

        else if (e.key === "ArrowUp") {
            e.preventDefault();
            roleActiveIndex = Math.max(roleActiveIndex - 1, 0);
            highlightRole(roleActiveIndex);
        }

        else if (e.key === "Enter") {
            if (roleActiveIndex >= 0) {
                e.preventDefault();
                selectRole(items[roleActiveIndex].textContent);
            } else {
                roleSearchResults.classList.add("hidden");
            }
        }

        else if (e.key === "Escape") {
            roleSearchResults.classList.add("hidden");
        }

    });

    document.addEventListener("click", (e) => {
        if (roleSearchBox && !roleSearchBox.contains(e.target)) {
            roleSearchResults.classList.add("hidden");
        }
    });

}


/*=========================================================
    CSRF
=========================================================*/

function getCSRFToken(){

    return document.querySelector(
        "[name=csrfmiddlewaretoken]"
    )?.value || "";

}


/*=========================================================
    MODULE 4 — TIMER
=========================================================*/

function startTimer(){

    clearInterval(timerInterval);

    remainingSeconds = 30 * 60;

    updateTimer();

    timerInterval = setInterval(()=>{

        remainingSeconds--;

        updateTimer();

        if(remainingSeconds<=0){

            clearInterval(timerInterval);

            evaluateInterview();

        }

    },1000);

}

function updateTimer(){

    const minutes =
        Math.floor(remainingSeconds/60);

    const seconds =
        remainingSeconds%60;

    timer.innerHTML =
        `${String(minutes).padStart(2,"0")}:${String(seconds).padStart(2,"0")}`;

}


/*=========================================================
    MODULE 5 — PROGRESS
=========================================================*/

function updateProgress(){

    const percent =
        (currentQuestion/totalQuestions)*100;

    progressFill.style.width =
        percent+"%";

    progressPercent.innerHTML =
        Math.round(percent)+"%";

    progressText.innerHTML =
        `${currentQuestion}/${totalQuestions}`;

    sidebarQuestions.innerHTML =
        `${currentQuestion}/${totalQuestions}`;

}


/*=========================================================
    MODULE 6 — SIDEBAR
=========================================================*/

function updateSidebar(){

    roleText.innerHTML =
        role;

    difficultyText.innerHTML =
        difficulty;

    sidebarDifficulty.innerHTML =
        difficulty;

    difficultyBadge.innerHTML =
        difficulty;

}


/*=========================================================
    MODULE 11 — WORD COUNTER
=========================================================*/

answerBox.addEventListener("input",()=>{

    const words =
        answerBox.value
        .trim()
        .split(/\s+/)
        .filter(Boolean);

    wordCount.innerHTML =
        `${words.length} Words`;

});


/*=========================================================
    Start Interview
=========================================================*/

document
.getElementById("startInterview")
.addEventListener("click", startInterview);

function startInterview(){

    role =
        document.getElementById("jobRole").value;

    difficulty =
        document.getElementById("difficulty").value;

    totalQuestions =
        parseInt(
            document.getElementById("totalQuestions").value
        );

    currentQuestion = 0;

    questions = [];

    answers = [];

    updateSidebar();

    updateProgress();

    startTimer();

    setupSection.style.display = "none";

    interviewSection.style.display = "grid";

    reportSection.style.display = "none";

    loadQuestion();

}


/*=========================================================
    MODULE 7 — QUESTION GENERATION
=========================================================*/

let isLoadingQuestion = false;

function loadQuestion() {

    // Guard against a double-fire (e.g. rapid double-click on
    // Submit/Skip) causing two overlapping requests, which was how
    // the question count could overshoot totalQuestions.
    if (isLoadingQuestion) return;
    isLoadingQuestion = true;

    document.getElementById("nextBtn").disabled = true;
    document.getElementById("skipBtn").disabled = true;

    questionText.innerHTML =
        "Generating AI Question...";

    answerBox.value = "";

    fetch("/interview/question/", {

        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },

        body: JSON.stringify({

            role: role,

            difficulty: difficulty,

            total_questions: totalQuestions,

            asked_questions: questions

        })

    })

    .then(response => response.json())

    .then(data => {

        console.log("Question API:", data);

        if (!data.success) {

            alert(data.error || "Unable to generate question.");

            // Server enforced the question cap -- wrap up the
            // interview instead of leaving the user stuck.
            if (data.error && data.error.includes("limit reached")) {
                clearInterval(timerInterval);
                evaluateInterview();
            }

            return;

        }

        if (!data.question) {

            alert("Question not received.");

            console.log(data);

            return;

        }

        /*-------------------------------
            Increase Question Count
        -------------------------------*/

        currentQuestion++;

        /*-------------------------------
            Store Question
        -------------------------------*/

        questions.push(data.question);

        /*-------------------------------
            Update UI
        -------------------------------*/

        questionNo.innerHTML =
            `Question ${currentQuestion} of ${totalQuestions}`;

        questionText.innerHTML =
            data.question;

        updateProgress();

        updateQuestionTracker();

        answerBox.value = "";

        wordCount.innerHTML = "0 Words";

    })

    .catch(error => {

        console.error(error);

        alert("Unable to connect to server.");

    })

    .finally(() => {

        isLoadingQuestion = false;

        document.getElementById("nextBtn").disabled = false;
        document.getElementById("skipBtn").disabled = false;

    });

}


/*=========================================================
    MODULE 12 — SUBMIT ANSWER
=========================================================*/

document
.getElementById("nextBtn")
.addEventListener("click", submitAnswer);

function submitAnswer() {

    const answer =
        answerBox.value.trim();

    answers.push({

        question:
            questions[currentQuestion - 1],

        answer:
            answer

    });

    if (currentQuestion >= totalQuestions) {

        clearInterval(timerInterval);

        evaluateInterview();

        return;

    }

    loadQuestion();

}


/*=========================================================
    MODULE 13 — SKIP QUESTION
=========================================================*/

document
.getElementById("skipBtn")
.addEventListener("click", skipQuestion);

function skipQuestion() {

    answers.push({

        question:
            questions[currentQuestion - 1],

        answer:
            ""

    });

    if (currentQuestion >= totalQuestions) {

        clearInterval(timerInterval);

        evaluateInterview();

        return;

    }

    loadQuestion();

}


/*=========================================================
    MODULE 8 — QUESTION TRACKER
=========================================================*/

function updateQuestionTracker() {

    const tracker =
        document.getElementById("questionTracker");

    if (!tracker) return;

    tracker.innerHTML = "";

    for (let i = 1; i <= totalQuestions; i++) {

        let status = "";

        if (i < currentQuestion) {

            status = "completed";

        }

        else if (i === currentQuestion) {

            status = "active";

        }

        else {

            status = "";

        }

        tracker.innerHTML += `

            <div class="tracker-item ${status}">

                <span>

                    Question ${i}

                </span>

            </div>

        `;

    }

}


/*=========================================================
    MODULE 9 — SPEECH (Read Question)
=========================================================*/

const readButton =
    document.getElementById("readQuestion");

if (readButton) {

    readButton.addEventListener("click", () => {

        speechSynthesis.cancel();

        const speech =
            new SpeechSynthesisUtterance(
                questionText.innerText
            );

        speech.rate = 1;

        speech.pitch = 1;

        speech.lang = "en-US";

        speechSynthesis.speak(speech);

    });

}


/*=========================================================
    MODULE 10 — VOICE RECOGNITION
=========================================================*/

let recognition = null;

if ("webkitSpeechRecognition" in window) {

    recognition =
        new webkitSpeechRecognition();

    recognition.continuous = true;

    recognition.interimResults = true;

    recognition.lang = "en-US";

    recognition.onresult = function(event) {

        let transcript = "";

        for (
            let i = event.resultIndex;
            i < event.results.length;
            i++
        ) {

            transcript +=
                event.results[i][0].transcript;

        }

        answerBox.value = transcript;

        answerBox.dispatchEvent(
            new Event("input")
        );

    };

}

const startRecording =
    document.getElementById("startRecording");

const stopRecording =
    document.getElementById("stopRecording");

if (startRecording && recognition) {

    startRecording.addEventListener("click", () => {

        recognition.start();

    });

}

if (stopRecording && recognition) {

    stopRecording.addEventListener("click", () => {

        recognition.stop();

    });

}


/*=========================================================
    MODULE 14 — EVALUATION
=========================================================*/

async function evaluateInterview() {

    try {

        const payload = {
            role: role,
            difficulty: difficulty,
            interview_data: answers
        };

        console.log("Evaluation Payload:", payload);

        const response = await fetch("/interview/evaluate/", {

            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },

            body: JSON.stringify(payload)

        });

        console.log("HTTP Status:", response.status);

        const text = await response.text();

        console.log("Raw Server Response:");
        console.log(text);

        let data;

        try {

            data = JSON.parse(text);

        } catch (e) {

            throw new Error(
                "Server returned invalid JSON.\n\n" + text
            );

        }

        console.log("Evaluation API:", data);

        // Only treat HTTP errors as failures
        if (!response.ok) {
            throw new Error(
                data.error || "Interview evaluation failed."
            );
        }

        // If the backend explicitly returns success:false
        if (data.success === false) {
            throw new Error(
                data.error || "Interview evaluation failed."
            );
        }

        interviewSection.style.display = "none";
        reportSection.style.display = "block";

        renderReport(data);

    }

    catch (error) {

        console.error("Evaluation Error:", error);

        alert(error.message);

    }

}

/*=========================================================
    MODULE 15 — REPORT RENDERING
=========================================================*/

function renderReport(data){

    if(!data){
        alert("No report received.");
        return;
    }

    console.log("Rendering Report:", data);

    /*-------------------------------
        Score
    -------------------------------*/

    const score =
        Number(
            data.overall_score ??
            data.score ??
            0
        );

    animateScore(score);

    /*-------------------------------
        Strengths
    -------------------------------*/

    const strengths =
        document.getElementById("strengthList");

    strengths.innerHTML = "";

    (data.strengths || []).forEach(item=>{

        strengths.innerHTML +=
        `<li>${item}</li>`;

    });

    /*-------------------------------
        Improvements
    -------------------------------*/

    const improvements =
        document.getElementById("improvementList");

    improvements.innerHTML = "";

    (data.improvements || []).forEach(item=>{

        improvements.innerHTML +=
        `<li>${item}</li>`;

    });

    /*-------------------------------
        Review Table
    -------------------------------*/

    const table =
        document.getElementById("reviewTable");

    table.innerHTML = "";

    (data.reviews || []).forEach((review,index)=>{

        table.innerHTML += `

            <tr>

                <td>${index+1}</td>

                <td>${review.score ?? "-"}</td>

                <td>${review.feedback ?? "-"}</td>

            </tr>

        `;

    });

    /*-------------------------------
        Study Plan
    -------------------------------*/

    const study =
        document.getElementById("recommendationList");

    study.innerHTML = "";

    (data.study_plan || []).forEach(item=>{

        study.innerHTML +=
        `<li>${item}</li>`;

    });

}


/*=========================================================
    MODULE 16 — ANIMATIONS (Score)
=========================================================*/

function animateScore(score){

    const circle =
        document.getElementById("overallScore");

    let current = 0;

    const interval = setInterval(()=>{

        current++;

        circle.innerHTML = current;

        if(current>=score){

            clearInterval(interval);

        }

    },20);

}


/*=========================================================
    MODULE 17 — DOWNLOAD REPORT
=========================================================*/

const downloadButton =
    document.getElementById("downloadReport");

if(downloadButton){

    downloadButton.addEventListener("click",()=>{

        window.print();

    });

}


/*=========================================================
    MODULE 18 — RETRY / RETAKE
=========================================================*/

const retryButton =
    document.getElementById("retakeInterview");

if(retryButton){

    retryButton.addEventListener("click",()=>{

        clearInterval(timerInterval);

        currentQuestion = 0;

        questions = [];

        answers = [];

        answerBox.value = "";

        wordCount.innerHTML = "0 Words";

        progressFill.style.width = "0%";

        progressPercent.innerHTML = "0%";

        progressText.innerHTML = "0/0";

        reportSection.style.display = "none";

        setupSection.style.display = "block";

    });

}


/*=========================================================
    Optional: Speak Result
=========================================================*/

function speakResult(score){

    if(!("speechSynthesis" in window))
        return;

    const speech =
        new SpeechSynthesisUtterance(

            `Interview completed.
             Your score is ${score} percent.`

        );

    speech.rate = 1;

    speech.pitch = 1;

    speech.lang = "en-US";

    speechSynthesis.speak(speech);

}


/*=========================================================
    Escape HTML
=========================================================*/

function escapeHTML(text){

    const div =
        document.createElement("div");

    div.innerText = text;

    return div.innerHTML;

}


/*=========================================================
    MODULE 19 — CLEANUP
=========================================================*/

window.addEventListener("beforeunload",()=>{

    clearInterval(timerInterval);

    speechSynthesis.cancel();

});


/*=========================================================
    Debug
=========================================================*/

console.log(
    "CareerGrowza Interview Loaded Successfully"
);