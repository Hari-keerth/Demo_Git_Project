/*=====================================================================
 CareerGrowza AI Email Agent
 Production Rewrite - ai_agent.js

 Same HTML IDs, CSS classes, Django endpoints, and Langflow integration
 as before. Everything else has been consolidated: one state manager,
 one response normalizer, one DOMContentLoaded entry point, one set of
 reset/copy/download helpers instead of three overlapping versions.
=======================================================================*/

"use strict";

const Agent = (() => {

    /*=================================================================
        CONFIG
    =================================================================*/

    const CONFIG = Object.freeze({
        REQUEST_TIMEOUT: 60000,
        MAX_RETRIES: 2,
        AUTO_SCROLL: true,
        AUTOSAVE_INTERVAL: 30000,
        DEBUG: true
    });

    const API = Object.freeze({
        generate: "/generate/",
        send: "/send-application/",
        downloadEmail: "/download-email/",
        downloadCoverLetter: "/download-cover-letter/"
    });

    const STORAGE_KEYS = Object.freeze({
        draft: "careergrowza_email_draft",
        autosave: "cg_ai_autosave"
    });

    const VALIDATION = Object.freeze({
        MAX_FILE_SIZE: 5 * 1024 * 1024, // 5 MB
        ALLOWED_TYPES: ["application/pdf"],
        EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/i,
        MIN_JD_LENGTH: 50
    });

    const ICONS = Object.freeze({
        success: "fa-circle-check",
        warning: "fa-triangle-exclamation",
        error: "fa-circle-xmark",
        info: "fa-circle-info",
        loading: "fa-spinner fa-spin"
    });

    const STEPS = Object.freeze([
        { id: 0, title: "Resume Parsing", icon: "fa-file-lines" },
        { id: 1, title: "Job Analysis", icon: "fa-magnifying-glass" },
        { id: 2, title: "Company Research", icon: "fa-building" },
        { id: 3, title: "Skill Matching", icon: "fa-list-check" },
        { id: 4, title: "Email Generation", icon: "fa-envelope" },
        { id: 5, title: "Cover Letter", icon: "fa-file-signature" },
        { id: 6, title: "Quality Review", icon: "fa-shield-halved" },
        { id: 7, title: "Completed", icon: "fa-circle-check" }
    ]);

    const DEFAULTS = Object.freeze({
        progressText: "0%",
        currentAgent: "Waiting...",
        decision: "Waiting",
        status: "Idle"
    });

    const APP = Object.freeze({
        NAME: "CareerGrowza AI Email Agent",
        VERSION: "2.0.0",
        AUTHOR: "CareerGrowza",
        BUILD: "Production"
    });

    /*=================================================================
        DOM CACHE
    =================================================================*/

    const DOM = {
        // Form
        form: document.getElementById("agentForm"),
        resume: document.getElementById("resume"),
        recruiterEmail: document.getElementById("email"),
        jobDescription: document.getElementById("jobDescription"),
        generateBtn: document.getElementById("generateBtn"),
        sendBtn: document.getElementById("sendBtn"),
        generateSendBtn: document.getElementById("generateSendBtn"),

        // Progress
        progressList: document.getElementById("progressList"),
        progressBar: document.querySelector(".progress-fill"),
        progressText: document.getElementById("progressText"),
        currentAgent: document.getElementById("currentAgent"),
        reflectionCount: document.getElementById("reflectionCount"),
        decision: document.getElementById("decision"),
        qualityScore: document.getElementById("qualityScore"),
        atsMatch: document.getElementById("atsMatch"),
        companySummary: document.getElementById("companySummary"),
        strategy: document.getElementById("strategy"),
        agentStatus: document.getElementById("agentStatus"),
        agentLog: document.getElementById("agentLog"),

        // Summary
        atsPercentage: document.getElementById("atsPercentage"),
        atsProgress: document.getElementById("atsProgress"),
        matchedSkills: document.getElementById("matchedSkills"),
        missingSkills: document.getElementById("missingSkills"),
        applicationStatus: document.getElementById("application_status"),
        rawJson: document.getElementById("rawJson"),

        // Output (editable)
        subject: document.getElementById("subject"),
        emailBody: document.getElementById("emailBody"),
        coverLetter: document.getElementById("coverLetter"),

        // Copy buttons
        copySubjectBtn: document.getElementById("copySubject"),
        copyEmailBtn: document.getElementById("copyEmail"),
        copyCoverBtn: document.getElementById("copyCover"),

        // Download buttons
        downloadEmailBtn: document.getElementById("downloadEmail"),
        downloadCoverBtn: document.getElementById("downloadCover"),

        // JSON
        toggleJsonBtn: document.getElementById("toggleJson"),
        exportJsonBtn: document.getElementById("exportJson"),

        // Optional overlay (present in some templates)
        loadingOverlay: document.getElementById("loadingOverlay"),
        executionTime: document.getElementById("executionTime")
    };

    /*=================================================================
        STATE MANAGER  (single source of truth)
    =================================================================*/

    const state = {
        generated: false,
        sending: false,
        loading: false,
        rawResponse: null,
        currentStep: 0,
        reflectionCount: 0,
        atsScore: 0,
        qualityScore: 0,
        matchedSkills: [],
        missingSkills: [],
        companySummary: "",
        strategy: "",
        decision: "",
        status: "",
        logs: []
    };

    function resetState() {
        state.generated = false;
        state.sending = false;
        state.loading = false;
        state.rawResponse = null;
        state.currentStep = 0;
        state.reflectionCount = 0;
        state.atsScore = 0;
        state.qualityScore = 0;
        state.matchedSkills = [];
        state.missingSkills = [];
        state.companySummary = "";
        state.strategy = "";
        state.decision = "";
        state.status = "";
        state.logs = [];
    }

    /*=================================================================
        UTILITIES
    =================================================================*/

    function debug(...args) {
        if (!CONFIG.DEBUG) return;
        console.log("[AI Agent]", ...args);
    }

    function safeArray(value) {
        return Array.isArray(value) ? value : [];
    }

    function safeString(value) {
        return value ?? "";
    }

    function safeNumber(value) {
        return Number(value || 0);
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    function getCSRFToken() {
        return (
            document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
            document.querySelector('meta[name="csrf-token"]')?.content ||
            ""
        );
    }

    function setButtonLoading(button, loading, text = "") {
        if (!button) return;
        if (loading) {
            button.dataset.originalText = button.dataset.originalText || button.innerHTML;
            button.disabled = true;
            button.innerHTML = `<span class="spinner"></span> ${text || "Loading..."}`;
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || text || button.innerHTML;
        }
    }

    function notify(message, type = "info") {
        console.log(`[${type.toUpperCase()}] ${message}`);
        // Hook point for a real toast library (Toastify/SweetAlert) if introduced later.
    }

    function wordCount(text) {
        if (!text) return 0;
        return text.trim().split(/\s+/).filter(Boolean).length;
    }

    function estimateTokens(text) {
        if (!text) return 0;
        return Math.ceil(text.length / 4);
    }

    function readingTime(text) {
        return Math.max(1, Math.ceil(wordCount(text) / 200));
    }

    function downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    }

    function openInNewTab(url) {
        window.open(url, "_blank");
    }

    async function copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.error(err);
            notify("Copy failed", "error");
            return false;
        }
    }

    function flashButton(button, label = "Copied") {
        if (!button) return;
        const original = button.innerHTML;
        button.classList.add("success");
        button.innerHTML = `<i class="fa-solid fa-check"></i> ${label}`;
        setTimeout(() => {
            button.classList.remove("success");
            button.innerHTML = original;
        }, 1500);
    }

    /*=================================================================
        LOGGER
    =================================================================*/

    function addLog(message, type = "info") {
        const time = new Date().toLocaleTimeString();
        state.logs.push({ message, type, time });

        if (!DOM.agentLog) return;
        const div = document.createElement("div");
        div.className = `log-${type}`;
        div.textContent = `[${time}] ${message}`;
        DOM.agentLog.appendChild(div);
        DOM.agentLog.scrollTop = DOM.agentLog.scrollHeight;
    }

    /*=================================================================
        TIMELINE ENGINE
    =================================================================*/

    function buildTimeline() {
        if (!DOM.progressList) return;
        DOM.progressList.innerHTML = "";
        STEPS.forEach(step => {
            const li = document.createElement("li");
            li.className = "agent-step waiting";
            li.dataset.step = step.id;
            li.innerHTML = `<i class="fa-solid ${step.icon}"></i><span>${step.title}</span>`;
            DOM.progressList.appendChild(li);
        });
    }

    function getStepEl(index) {
        return document.querySelector(`.agent-step[data-step="${index}"]`);
    }

    function clearActiveStep() {
        document.querySelectorAll(".agent-step.active")
            .forEach(el => el.classList.remove("active"));
    }

    function setStepState(index, status) {
        const step = getStepEl(index);
        if (!step) return;
        step.classList.remove("waiting", "active", "completed", "failed");
        step.classList.add(status);
    }

    function updateProgress(percent) {
        percent = Math.max(0, Math.min(100, percent));
        if (DOM.progressBar) DOM.progressBar.style.width = `${percent}%`;
        if (DOM.progressText) DOM.progressText.textContent = `${percent}%`;
    }

    function gotoStep(index) {
        state.currentStep = index;
        clearActiveStep();
        setStepState(index, "active");
        if (DOM.currentAgent) DOM.currentAgent.textContent = STEPS[index].title;
    }

    async function runStep(index, delay = 400) {
        gotoStep(index);
        updateProgress(Math.round(((index + 1) / STEPS.length) * 100));
        addLog(`Running: ${STEPS[index].title}`, "info");
        await sleep(delay);
        setStepState(index, "completed");
    }

    function timelineFailed(message = "Generation Failed") {
        setStepState(state.currentStep, "failed");
        setDecision(message, "failed");
    }

    function completeTimeline() {
        updateProgress(100);
        STEPS.forEach((_, i) => setStepState(i, "completed"));
    }

    function resetTimeline() {
        state.currentStep = 0;
        state.reflectionCount = 0;
        updateProgress(0);
        if (DOM.currentAgent) DOM.currentAgent.textContent = DEFAULTS.currentAgent;
        if (DOM.reflectionCount) DOM.reflectionCount.textContent = "0";
        if (DOM.decision) setDecision(DEFAULTS.decision, "waiting");
        if (DOM.agentStatus) DOM.agentStatus.textContent = DEFAULTS.status;
        if (DOM.agentLog) DOM.agentLog.innerHTML = "";
        buildTimeline();
    }

    /*=================================================================
        STATUS / METRIC SETTERS
    =================================================================*/

    function setDecision(text, type = "waiting") {
        if (!DOM.decision) return;
        DOM.decision.textContent = text;
        DOM.decision.className = `decision ${type}`;
    }

    function setApplicationStatus(text, type = "waiting") {
        if (!DOM.applicationStatus) return;
        DOM.applicationStatus.textContent = text;
        DOM.applicationStatus.className = `status-${type}`;
    }

    function setQualityScore(score) {
        score = safeNumber(score);
        state.qualityScore = score;
        if (DOM.qualityScore) DOM.qualityScore.textContent = `${score}%`;
    }

    function setATS(score) {
        score = safeNumber(score);
        state.atsScore = score;
        if (DOM.atsMatch) DOM.atsMatch.textContent = `${score}%`;
        if (DOM.atsPercentage) DOM.atsPercentage.textContent = `${score}%`;
        if (DOM.atsProgress) DOM.atsProgress.style.width = `${score}%`;
    }

    /*=================================================================
        FORM VALIDATION
    =================================================================*/

    function showInputError(input, message) {
        if (!input) return;
        input.classList.remove("input-success");
        input.classList.add("input-error");
        let error = input.parentElement.querySelector(".validation-message");
        if (!error) {
            error = document.createElement("div");
            error.className = "validation-message";
            input.parentElement.appendChild(error);
        }
        error.textContent = message;
    }

    function clearInputError(input) {
        if (!input) return;
        input.classList.remove("input-error");
        input.classList.add("input-success");
        input.parentElement.querySelector(".validation-message")?.remove();
    }

    function clearValidation() {
        [DOM.resume, DOM.recruiterEmail, DOM.jobDescription].forEach(clearInputError);
    }

    function validateResume() {
        const file = DOM.resume?.files?.[0];
        if (!file) {
            showInputError(DOM.resume, "Resume is required.");
            return false;
        }
        if (!VALIDATION.ALLOWED_TYPES.includes(file.type)) {
            showInputError(DOM.resume, "Only PDF resumes are allowed.");
            return false;
        }
        if (file.size > VALIDATION.MAX_FILE_SIZE) {
            showInputError(DOM.resume, "Maximum file size is 5 MB.");
            return false;
        }
        clearInputError(DOM.resume);
        return true;
    }

    function validateRecruiterEmail() {
        const value = DOM.recruiterEmail?.value.trim() || "";
        if (!value) {
            showInputError(DOM.recruiterEmail, "Recruiter email is required.");
            return false;
        }
        if (!VALIDATION.EMAIL_REGEX.test(value)) {
            showInputError(DOM.recruiterEmail, "Enter a valid email address.");
            return false;
        }
        clearInputError(DOM.recruiterEmail);
        return true;
    }

    function validateJobDescription() {
        const text = DOM.jobDescription?.value.trim() || "";
        if (!text) {
            showInputError(DOM.jobDescription, "Job description is required.");
            return false;
        }
        if (text.length < VALIDATION.MIN_JD_LENGTH) {
            showInputError(DOM.jobDescription, "Job description is too short.");
            return false;
        }
        clearInputError(DOM.jobDescription);
        return true;
    }

    function validateForm() {
        clearValidation();
        const resumeValid = validateResume();
        const emailValid = validateRecruiterEmail();
        const jdValid = validateJobDescription();
        return resumeValid && emailValid && jdValid;
    }

    function validateSendData() {
        if (!DOM.subject.value.trim()) {
            notify("Email subject is empty.", "warning");
            return false;
        }
        if (!DOM.emailBody.value.trim()) {
            notify("Email body is empty.", "warning");
            return false;
        }
        if (!DOM.coverLetter.value.trim()) {
            notify("Cover letter is empty.", "warning");
            return false;
        }
        return true;
    }

    function attachValidationEvents() {
        DOM.resume?.addEventListener("change", validateResume);
        DOM.recruiterEmail?.addEventListener("input", validateRecruiterEmail);
        DOM.jobDescription?.addEventListener("input", validateJobDescription);
    }

    function buildFormData() {
        const formData = new FormData();
        formData.append("resume", DOM.resume.files[0]);
        formData.append("email", DOM.recruiterEmail.value.trim());
        formData.append("job_description", DOM.jobDescription.value.trim());
        return formData;
    }

    function canSubmit() {
        if (state.loading) {
            notify("Please wait...", "warning");
            return false;
        }
        return validateForm();
    }

    function ensureGenerated() {
        if (!state.generated) {
            notify("Generate documents first.", "warning");
            return false;
        }
        return true;
    }

    /*=================================================================
        API SERVICE  (fetch + timeout + retry, single implementation)
    =================================================================*/

    async function fetchWithTimeout(resource, options = {}) {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), CONFIG.REQUEST_TIMEOUT);
        try {
            return await fetch(resource, { ...options, signal: controller.signal });
        } finally {
            clearTimeout(timer);
        }
    }

    async function retry(fn, retries = CONFIG.MAX_RETRIES) {
        let lastError;
        for (let attempt = 0; attempt <= retries; attempt++) {
            try {
                return await fn();
            } catch (error) {
                lastError = error;
                if (error.name === "AbortError") break; // don't retry timeouts
                if (attempt < retries) {
                    addLog(`Retry ${attempt + 1}/${retries}`, "warning");
                    await sleep(1000 * (attempt + 1));
                }
            }
        }
        throw lastError;
    }

    async function parseResponse(response) {
        let data = null;
        try {
            data = await response.json();
        } catch {
            throw new Error("Server returned an invalid JSON response.");
        }
        if (!response.ok) {
            throw new Error(data.error || data.message || "Request failed.");
        }
        return data;
    }

    const APIService = {
        async post(url, body, isFormData = false) {
            const options = {
                method: "POST",
                headers: { "X-CSRFToken": getCSRFToken() }
            };
            if (isFormData) {
                options.body = body;
            } else {
                options.headers["Content-Type"] = "application/json";
                options.body = JSON.stringify(body);
            }
            const response = await retry(() => fetchWithTimeout(url, options));
            return await parseResponse(response);
        }
    };

    /*=================================================================
        RESPONSE NORMALIZER  (the one and only source of truth for
        translating whatever shape the Django/Langflow backend sends
        into the shape the UI renders)
    =================================================================*/

    function normalizeResponse(data = {}) {
        return {
            success: Boolean(data.success ?? true),
            subject: safeString(data.subject || data.email_subject),
            email: safeString(data.email || data.email_body),
            coverLetter: safeString(data.cover_letter || data.coverLetter),
            ats: safeNumber(data.ats ?? data.ats_match),
            quality: safeNumber(data.quality ?? data.quality_score ?? data.score),
            reflectionCount: safeNumber(data.reflection_count),
            matchedSkills: safeArray(data.matched_skills || data.skills),
            missingSkills: safeArray(data.missing_skills),
            companySummary: safeString(data.company_summary),
            strategy: safeString(data.strategy),
            decision: safeString(data.decision || "Completed"),
            status: safeString(data.status || "Completed"),
            recruiter: safeString(data.recruiter),
            message: safeString(data.message),
            raw: data
        };
    }

    async function requestGeneration(formData) {
        addLog("Sending generation request...", "info");
        const data = await APIService.post(API.generate, formData, true);
        return normalizeResponse(data);
    }

    async function requestSend(body) {
        addLog("Sending application...", "info");
        const data = await APIService.post(API.send, body, false);
        return normalizeResponse(data);
    }

    function downloadEmailPDF() {
        openInNewTab(API.downloadEmail);
    }

    function downloadCoverLetterPDF() {
        openInNewTab(API.downloadCoverLetter);
    }

    /*=================================================================
        RENDERING
    =================================================================*/

    function renderSkills(matched, missing) {
        if (DOM.matchedSkills) {
            DOM.matchedSkills.innerHTML = matched.map(skill => `<li>${skill}</li>`).join("");
        }
        if (DOM.missingSkills) {
            DOM.missingSkills.innerHTML = missing.map(skill => `<li>${skill}</li>`).join("");
        }
    }

    function renderResponse(result) {
        // Documents
        if (DOM.subject) DOM.subject.value = result.subject;
        if (DOM.emailBody) DOM.emailBody.value = result.email;
        if (DOM.coverLetter) DOM.coverLetter.value = result.coverLetter;

        // Scores
        setQualityScore(result.quality);
        setATS(result.ats);

        // Reflection
        if (DOM.reflectionCount) DOM.reflectionCount.textContent = result.reflectionCount;

        // Decision
        setDecision(result.decision || "READY", "success");

        // Company / strategy
        if (DOM.companySummary) DOM.companySummary.textContent = result.companySummary;
        if (DOM.strategy) DOM.strategy.textContent = result.strategy;

        // Skills
        renderSkills(result.matchedSkills, result.missingSkills);

        // Application status
        setApplicationStatus("Generated Successfully", "success");

        // Raw JSON viewer
        if (DOM.rawJson) DOM.rawJson.textContent = JSON.stringify(result.raw, null, 2);
    }

    function updateStateFromResult(result) {
        state.atsScore = result.ats;
        state.qualityScore = result.quality;
        state.companySummary = result.companySummary;
        state.strategy = result.strategy;
        state.decision = result.decision;
        state.status = result.status;
        state.matchedSkills = result.matchedSkills;
        state.missingSkills = result.missingSkills;
        state.reflectionCount = result.reflectionCount;
    }

    function saveResponse(result) {
        state.rawResponse = result.raw;
        state.generated = true;
    }

    function clearResponse() {
        state.rawResponse = null;
        state.generated = false;
    }

    /*=================================================================
        UI RESET HELPERS
    =================================================================*/

    function resetOutput() {
        if (DOM.subject) DOM.subject.value = "";
        if (DOM.emailBody) DOM.emailBody.value = "";
        if (DOM.coverLetter) DOM.coverLetter.value = "";
        if (DOM.companySummary) DOM.companySummary.textContent = "";
        if (DOM.strategy) DOM.strategy.textContent = "";
        if (DOM.rawJson) DOM.rawJson.textContent = "";
    }

    function resetSummary() {
        if (DOM.atsPercentage) DOM.atsPercentage.textContent = "0%";
        if (DOM.atsProgress) DOM.atsProgress.style.width = "0%";
        if (DOM.matchedSkills) DOM.matchedSkills.innerHTML = "";
        if (DOM.missingSkills) DOM.missingSkills.innerHTML = "";
        setApplicationStatus("Waiting", "waiting");
    }

    function resetUI() {
        resetOutput();
        resetSummary();
        resetTimeline();
        clearValidation();
    }

    function resetApplication() {
        resetUI();
        clearResponse();
        resetState();
        addLog("Application Reset.", "warning");
    }

    /*=================================================================
        ERROR HANDLING
    =================================================================*/

    function generationError(error) {
        console.error(error);
        timelineFailed();
        addLog(error.message || "Unexpected Error", "error");
    }

    function handleRequestError(error) {
        console.error(error);
        const message = error.name === "AbortError"
            ? "Request timed out. Please try again."
            : (error.message || "Unexpected server error.");
        notify(message, "error");
        addLog(message, "error");
        generationError(error);
    }

    function handleRequestSuccess() {
        notify("Request completed successfully.", "success");
    }

    /*=================================================================
        EXECUTION TIMER
    =================================================================*/

    let generationStart = 0;

    function startTimer() {
        generationStart = performance.now();
    }

    function stopTimer() {
        const seconds = (performance.now() - generationStart) / 1000;
        if (DOM.executionTime) DOM.executionTime.textContent = `${seconds.toFixed(1)} s`;
        debug(`Completed in ${seconds.toFixed(2)} seconds`);
    }

    /*=================================================================
        GENERATE DOCUMENTS WORKFLOW
    =================================================================*/

    async function startGenerationUI() {
        clearActiveStep();
        buildTimeline();
        setDecision("Analyzing...", "waiting");
        if (DOM.agentStatus) DOM.agentStatus.textContent = "Running";
        addLog("AI Agent started", "info");
    }

    function finishGenerationUI() {
        completeTimeline();
        addLog("AI Agent finished successfully", "success");
    }

    async function generateDocuments() {
        if (!canSubmit()) return;

        state.loading = true;
        clearResponse();
        await startGenerationUI();
        setButtonLoading(DOM.generateBtn, true, "Generating...");
        startTimer();

        try {
            const formData = buildFormData();
            addLog("Preparing request...", "info");

            await runStep(0);
            await runStep(1);
            await runStep(2);

            const result = await requestGeneration(formData);
            saveResponse(result);

            await runStep(3);
            await runStep(4);
            await runStep(5);
            await runStep(6);
            await runStep(7);

            updateStateFromResult(result);
            renderResponse(result);
            finishGenerationUI();
            handleRequestSuccess();
            addLog("Documents generated successfully.", "success");

            if (CONFIG.AUTO_SCROLL) {
                DOM.subject?.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        } catch (error) {
            handleRequestError(error);
        } finally {
            stopTimer();
            state.loading = false;
            setButtonLoading(DOM.generateBtn, false);
        }
    }

    async function handleGenerate() {
        await generateDocuments();
    }

    /*=================================================================
        SEND / GENERATE & SEND WORKFLOW
    =================================================================*/

    function buildSendPayload() {
        return {
            recruiter_email: DOM.recruiterEmail.value.trim(),
            email_subject: DOM.subject.value,
            email_body: DOM.emailBody.value,
            cover_letter: DOM.coverLetter.value
        };
    }

    function handleSendSuccess(response) {
        addLog("Application sent successfully.", "success");
        setDecision("Application Sent", "success");
        setApplicationStatus("Sent", "success");
        if (DOM.agentStatus) DOM.agentStatus.textContent = "Completed";
        notify(response.message || "Application sent successfully.", "success");
        clearDraft();
    }

    function handleSendFailure(error) {
        console.error(error);
        const message = error.message || "Application sending failed.";
        addLog(message, "error");
        setDecision("Sending Failed", "failed");
        setApplicationStatus("Failed", "failed");
        notify(message, "error");
    }

    async function sendApplication() {
        if (!ensureGenerated()) {
            notify("Generate the documents before sending.", "warning");
            return;
        }
        if (!validateSendData()) return;

        state.sending = true;
        setButtonLoading(DOM.sendBtn, true, "Sending...");
        addLog("Preparing application...", "info");
        setApplicationStatus("Sending...", "waiting");

        try {
            const payload = buildSendPayload();
            const response = await requestSend(payload);
            handleSendSuccess(response);
        } catch (error) {
            handleSendFailure(error);
        } finally {
            state.sending = false;
            setButtonLoading(DOM.sendBtn, false);
        }
    }

    async function generateAndSend() {
        if (!state.generated) {
            await generateDocuments();
        }
        if (!state.generated) return;
        await sendApplication();
    }

    async function resendApplication() {
        addLog("Retrying application...", "warning");
        await sendApplication();
    }

    /*=================================================================
        USER ACTIONS: COPY / DOWNLOAD / EXPORT
    =================================================================*/

    async function copySubject() {
        if (!ensureGenerated()) return;
        if (await copyToClipboard(DOM.subject.value)) flashButton(DOM.copySubjectBtn);
    }

    async function copyEmailBody() {
        if (!ensureGenerated()) return;
        if (await copyToClipboard(DOM.emailBody.value)) flashButton(DOM.copyEmailBtn);
    }

    async function copyCoverLetter() {
        if (!ensureGenerated()) return;
        if (await copyToClipboard(DOM.coverLetter.value)) flashButton(DOM.copyCoverBtn);
    }

    function buildCombinedText() {
        return [
            "Subject:", DOM.subject.value,
            "\n" + "=".repeat(50) + "\n",
            "Email:", DOM.emailBody.value,
            "\n" + "=".repeat(50) + "\n",
            "Cover Letter:", DOM.coverLetter.value
        ].join("\n");
    }

    async function copyAll() {
        if (!ensureGenerated()) return;
        if (await copyToClipboard(buildCombinedText())) {
            notify("Everything copied.", "success");
        }
    }

    function handleDownloadEmail() {
        if (!ensureGenerated()) return;
        addLog("Downloading Email PDF...", "info");
        downloadEmailPDF();
    }

    function handleDownloadCoverLetter() {
        if (!ensureGenerated()) return;
        addLog("Downloading Cover Letter PDF...", "info");
        downloadCoverLetterPDF();
    }

    async function downloadAllDocuments() {
        if (!ensureGenerated()) return;
        handleDownloadEmail();
        await sleep(500);
        handleDownloadCoverLetter();
    }

    function exportRawJSON() {
        if (!ensureGenerated()) return;
        downloadFile(
            JSON.stringify(state.rawResponse, null, 2),
            "ai_agent_output.json",
            "application/json"
        );
        addLog("JSON exported.", "success");
    }

    function exportTXT() {
        if (!ensureGenerated()) return;
        downloadFile(buildCombinedText(), "application.txt", "text/plain");
    }

    function toggleRawJSON() {
        if (!ensureGenerated()) return;
        if (!DOM.rawJson || !DOM.toggleJsonBtn) return;
        DOM.rawJson.classList.toggle("hidden");
        const hidden = DOM.rawJson.classList.contains("hidden");
        DOM.toggleJsonBtn.innerHTML = hidden
            ? `<i class="fa-solid fa-code"></i> Show JSON`
            : `<i class="fa-solid fa-code"></i> Hide JSON`;
    }

    function printDocuments() {
        if (!ensureGenerated()) return;
        window.print();
    }

    async function shareJSON() {
        if (!ensureGenerated()) return;
        if (!navigator.share) {
            notify("Sharing is not supported.", "warning");
            return;
        }
        try {
            await navigator.share({
                title: "CareerGrowza AI Output",
                text: JSON.stringify(state.rawResponse, null, 2)
            });
        } catch (err) {
            console.error(err);
        }
    }

    /*=================================================================
        DRAFT / AUTOSAVE  (single localStorage-backed implementation)
    =================================================================*/

    function saveDraft() {
        if (!state.generated) return;
        try {
            localStorage.setItem(STORAGE_KEYS.draft, JSON.stringify({
                subject: DOM.subject.value,
                email: DOM.emailBody.value,
                cover: DOM.coverLetter.value
            }));
        } catch (err) {
            console.error(err);
        }
    }

    function loadDraft() {
        const draft = localStorage.getItem(STORAGE_KEYS.draft);
        if (!draft) return;
        try {
            const data = JSON.parse(draft);
            if (DOM.subject) DOM.subject.value = data.subject || "";
            if (DOM.emailBody) DOM.emailBody.value = data.email || "";
            if (DOM.coverLetter) DOM.coverLetter.value = data.cover || "";
        } catch (err) {
            console.error(err);
            localStorage.removeItem(STORAGE_KEYS.draft);
        }
    }

    function clearDraft() {
        localStorage.removeItem(STORAGE_KEYS.draft);
    }

    function autoSave() {
        if (!state.generated) return;
        try {
            localStorage.setItem(STORAGE_KEYS.autosave, JSON.stringify({
                subject: DOM.subject.value,
                email: DOM.emailBody.value,
                cover: DOM.coverLetter.value,
                ats: state.atsScore
            }));
        } catch (err) {
            console.error(err);
        }
    }

    /*=================================================================
        STATISTICS / CONFIDENCE
    =================================================================*/

    function showStatistics() {
        const emailWords = wordCount(DOM.emailBody.value);
        const coverWords = wordCount(DOM.coverLetter.value);
        const tokens = estimateTokens(DOM.emailBody.value + DOM.coverLetter.value);

        addLog(`Email: ${emailWords} words`, "info");
        addLog(`Cover Letter: ${coverWords} words`, "info");
        addLog(`Estimated Tokens: ${tokens}`, "info");
    }

    function calculateConfidence() {
        let score = 50;
        score += state.atsScore * 0.30;
        score += state.qualityScore * 0.20;
        return Math.min(100, Math.round(score));
    }

    function showConfidence() {
        addLog(`AI Confidence: ${calculateConfidence()}%`, "success");
    }

    function sessionSummary() {
        console.table({
            Generated: state.generated,
            ATS: state.atsScore,
            Quality: state.qualityScore,
            Reflections: state.reflectionCount,
            Steps: STEPS.length,
            Status: state.status
        });
    }

    /*=================================================================
        SYSTEM CHECKS
    =================================================================*/

    function systemHealthCheck() {
        const required = {
            form: DOM.form, resume: DOM.resume, email: DOM.recruiterEmail,
            jobDescription: DOM.jobDescription, subject: DOM.subject,
            emailBody: DOM.emailBody, coverLetter: DOM.coverLetter,
            progress: DOM.progressList
        };
        const missing = Object.entries(required)
            .filter(([, el]) => !el)
            .map(([name]) => name);

        if (missing.length) {
            console.error("Missing DOM Elements:", missing);
            return false;
        }
        return true;
    }

    function browserSupport() {
        const supported = window.fetch && window.Promise && window.localStorage && window.FormData;
        if (!supported) {
            alert("Your browser is not supported.");
            return false;
        }
        return true;
    }

    function showVersion() {
        console.group(APP.NAME);
        console.log("Version :", APP.VERSION);
        console.log("Build   :", APP.BUILD);
        console.log("Author  :", APP.AUTHOR);
        console.groupEnd();
    }

    /*=================================================================
        EVENT WIRING  (single place all listeners are attached)
    =================================================================*/

    function registerEvents() {
        DOM.generateBtn?.addEventListener("click", async (e) => {
            e.preventDefault();
            await handleGenerate();
        });

        DOM.sendBtn?.addEventListener("click", async (e) => {
            e.preventDefault();
            await sendApplication();
        });

        DOM.generateSendBtn?.addEventListener("click", async (e) => {
            e.preventDefault();
            await generateAndSend();
        });

        DOM.copySubjectBtn?.addEventListener("click", copySubject);
        DOM.copyEmailBtn?.addEventListener("click", copyEmailBody);
        DOM.copyCoverBtn?.addEventListener("click", copyCoverLetter);

        DOM.downloadEmailBtn?.addEventListener("click", handleDownloadEmail);
        DOM.downloadCoverBtn?.addEventListener("click", handleDownloadCoverLetter);

        DOM.toggleJsonBtn?.addEventListener("click", toggleRawJSON);
        DOM.exportJsonBtn?.addEventListener("click", exportRawJSON);

        DOM.form?.addEventListener("submit", (e) => e.preventDefault());

        document.addEventListener("keydown", async (e) => {
            // Ctrl + Enter -> Generate
            if (e.ctrlKey && !e.shiftKey && e.key === "Enter") {
                e.preventDefault();
                if (!state.loading) await handleGenerate();
                return;
            }
            // Ctrl + Shift + Enter -> Generate & Send
            if (e.ctrlKey && e.shiftKey && e.key === "Enter") {
                e.preventDefault();
                if (!state.loading) await generateAndSend();
                return;
            }
            // Escape -> Reset
            if (e.key === "Escape") {
                resetUI();
            }
            // Ctrl + Shift + D -> Debug dump
            if (e.ctrlKey && e.shiftKey && e.key === "D") {
                console.table(state);
            }
        });

        document.addEventListener("visibilitychange", () => {
            if (document.hidden) saveDraft();
        });

        window.addEventListener("beforeunload", () => {
            if (state.generated) saveDraft();
        });

        window.addEventListener("online", () => notify("Internet connection restored.", "success"));
        window.addEventListener("offline", () => notify("No internet connection.", "error"));

        window.addEventListener("resize", () => debug("Resize", window.innerWidth));

        window.addEventListener("error", (event) => {
            console.error(event.error);
            addLog(event.message, "error");
        });

        window.addEventListener("unhandledrejection", (event) => {
            console.error(event.reason);
            addLog("Unhandled Promise Error", "error");
        });

        setInterval(autoSave, CONFIG.AUTOSAVE_INTERVAL);

        attachValidationEvents();
    }

    /*=================================================================
        BOOTSTRAP  (the single DOMContentLoaded entry point)
    =================================================================*/

    function initializeAgent() {
        resetUI();
        buildTimeline();
        updateProgress(0);
        setDecision(DEFAULTS.decision, "waiting");
        if (DOM.agentStatus) DOM.agentStatus.textContent = DEFAULTS.status;
        if (DOM.currentAgent) DOM.currentAgent.textContent = DEFAULTS.currentAgent;
        if (DOM.progressText) DOM.progressText.textContent = DEFAULTS.progressText;
        addLog("AI Agent initialized.", "info");
    }

    function bootstrap() {
        debug("Starting AI Agent...");

        if (!browserSupport()) return;
        if (!systemHealthCheck()) return;

        showVersion();
        initializeAgent();
        loadDraft();
        registerEvents();

        if (DOM.agentStatus) DOM.agentStatus.textContent = "Ready";
        if (DOM.currentAgent) DOM.currentAgent.textContent = "Idle";
        setDecision("Ready", "waiting");
        addLog("AI Agent Ready.", "success");

        debug("Initialization Complete.");
        debug(`${APP.NAME} v${APP.VERSION} Loaded Successfully`);
    }

    document.addEventListener("DOMContentLoaded", bootstrap);

    /*=================================================================
        PUBLIC API  (same surface the templates/inline scripts call)
    =================================================================*/

    return {
        generate: handleGenerate,
        generateAndSend,
        send: sendApplication,
        resend: resendApplication,
        reset: resetApplication,
        copyAll,
        downloadAll: downloadAllDocuments,
        exportJSON: exportRawJSON,
        exportTXT,
        print: printDocuments,
        share: shareJSON,
        showStatistics,
        showConfidence,
        sessionSummary,
        state,
        version: APP.VERSION
    };

})();

window.Agent = Agent;