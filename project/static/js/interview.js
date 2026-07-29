/*=========================================================
 CareerGrowza AI Mock Interview
 interview.js
 Part 1
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
    DOM
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

/*=========================================================
    Buttons
=========================================================*/

document
.getElementById("startInterview")
.addEventListener("click", startInterview);

document
.getElementById("nextBtn")
.addEventListener("click", submitAnswer);

document
.getElementById("skipBtn")
.addEventListener("click", skipQuestion);

/*=========================================================
    CSRF
=========================================================*/

function getCSRFToken(){

    return document.querySelector(
        "[name=csrfmiddlewaretoken]"
    )?.value || "";

}

/*=========================================================
    Timer
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
    Progress
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
    Sidebar
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
    Word Counter
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
    Load Question
=========================================================*/

function loadQuestion() {

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

            asked_questions: questions

        })

    })

    .then(response => response.json())

    .then(data => {

        console.log("Question API:", data);

        if (!data.success) {

            alert(data.error || "Unable to generate question.");

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

    });

}

/*=========================================================
    Submit Answer
=========================================================*/

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
    Skip Question
=========================================================*/

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
    Question Tracker
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
    Read Question
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
    Voice Recording
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
    Evaluate Interview
=========================================================*/

function evaluateInterview() {

    fetch("/interview/evaluate/", {

        method: "POST",

        headers: {

            "Content-Type": "application/json",

            "X-CSRFToken": getCSRFToken()

        },

        body: JSON.stringify({

            role: role,

            interview_data: answers

        })

    })

    .then(response => response.json())

    .then(data => {

        console.log("Evaluation API:", data);

        interviewSection.style.display = "none";

        reportSection.style.display = "block";

        renderReport(data);

    })

    .catch(error => {

        console.error(error);

        alert("Unable to evaluate interview.");

    });

}

/*=========================================================
    Render Report
=========================================================*/

function renderReport(data){

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
    Score Animation
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
    Download Report
=========================================================*/

const downloadButton =
    document.getElementById("downloadReport");

if(downloadButton){

    downloadButton.addEventListener("click",()=>{

        window.print();

    });

}

/*=========================================================
    Retake Interview
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
    Optional:
    Speak Result
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
    Window Cleanup
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


