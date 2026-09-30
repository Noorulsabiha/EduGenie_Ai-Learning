document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("eduForm");
    const task = document.getElementById("task");
    const input = document.getElementById("user_input");
    const button = document.getElementById("submitBtn");
    const statusBox = document.getElementById("status");
    const resultSection = document.getElementById("resultSection");
    const resultContent = document.getElementById("resultContent");

    // Check required HTML elements
    if (!form || !task || !input || !button ||
        !statusBox || !resultSection || !resultContent) {

        console.error("EduGenie: Required HTML element is missing.");
        return;
    }

    function showStatus(message, type = "") {
        statusBox.textContent = message;
        statusBox.className = "status";

        if (type) {
            statusBox.classList.add(type);
        }

        statusBox.classList.remove("hidden");
    }

    function hideStatus() {
        statusBox.classList.add("hidden");
    }

    function renderResult(result) {

        resultContent.innerHTML = "";

        // Quiz result
        if (Array.isArray(result)) {

            result.forEach((item, index) => {

                const box = document.createElement("div");
                box.className = "quiz-question";

                const title = document.createElement("h3");
                title.textContent =
                    `${index + 1}. ${item.question || ""}`;

                box.appendChild(title);

                if (Array.isArray(item.options)) {

                    const list = document.createElement("ol");
                    list.type = "A";

                    item.options.forEach(option => {

                        const li = document.createElement("li");
                        li.textContent = option;

                        list.appendChild(li);
                    });

                    box.appendChild(list);
                }

                if (item.answer) {

                    const answer = document.createElement("p");

                    const strong = document.createElement("strong");
                    strong.textContent = "Answer: ";

                    answer.appendChild(strong);
                    answer.appendChild(
                        document.createTextNode(String(item.answer))
                    );

                    box.appendChild(answer);
                }

                resultContent.appendChild(box);
            });

        } else {

            // Normal text result
            const text = document.createElement("div");

            text.textContent =
                result !== undefined && result !== null
                    ? String(result)
                    : "No result received.";

            resultContent.appendChild(text);
        }

        resultSection.classList.remove("hidden");
    }

    // Form submit
    form.addEventListener("submit", async (event) => {

        event.preventDefault();

        const value = input.value.trim();

        if (!value) {
            showStatus("Please enter your question or topic.", "error");
            input.focus();
            return;
        }

        button.disabled = true;
        resultSection.classList.add("hidden");

        showStatus("EduGenie is thinking...");

        const endpoints = {
            "Explain": "/explain",
            "QnA": "/qa",
            "Quiz": "/quiz",
            "Summary": "/summarize",
            "Recommend Path": "/learn/recommendations"
        };

        const selectedTask = task.value;
        const endpoint = endpoints[selectedTask];

        if (!endpoint) {
            showStatus("Invalid task selected.", "error");
            button.disabled = false;
            return;
        }

        let payload;

        switch (selectedTask) {

            case "Explain":
                payload = {
                    topic: value
                };
                break;

            case "QnA":
                payload = {
                    question: value
                };
                break;

            case "Quiz":
                payload = {
                    passage: value
                };
                break;

            case "Summary":
                payload = {
                    text: value
                };
                break;

            case "Recommend Path":
                payload = {
                    topic: value,
                    level: "Beginner"
                };
                break;
        }

        try {

            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const contentType =
                response.headers.get("content-type") || "";

            if (!contentType.includes("application/json")) {

                throw new Error(
                    `Server returned an unexpected response (${response.status}).`
                );
            }

            const data = await response.json();

            if (!response.ok) {

                throw new Error(
                    data.error || `Server error: ${response.status}`
                );
            }

            if (data.error) {
                throw new Error(data.error);
            }

            if (!("result" in data)) {
                throw new Error("No result received from EduGenie.");
            }

            renderResult(data.result);

            showStatus("Answer generated successfully.", "success");

        } catch (error) {

            console.error("EduGenie error:", error);

            const rawMessage = error && error.message ? error.message : "Something went wrong.";
            const lowerMessage = rawMessage.toLowerCase();

            let userMessage = "Unable to generate the answer. Please try again shortly.";

            if (lowerMessage.includes("quota")) {
                userMessage = "Gemini API quota has been reached. Please try again after the quota resets.";
            } else if (
                lowerMessage.includes("temporarily unavailable") ||
                lowerMessage.includes("503") ||
                lowerMessage.includes("unavailable")
            ) {
                userMessage = "Gemini is temporarily unavailable. Please try again shortly.";
            } else if (
                lowerMessage.includes("api key") ||
                lowerMessage.includes(".env") ||
                lowerMessage.includes("configuration error")
            ) {
                userMessage = "Gemini API key configuration error. Please check the .env configuration.";
            } else if (
                lowerMessage.includes("model") &&
                (lowerMessage.includes("supported") || lowerMessage.includes("configuration"))
            ) {
                userMessage = "Gemini model configuration error. Please check the configured model in .env.";
            }

            resultContent.textContent = userMessage;
            resultSection.classList.remove("hidden");
            showStatus(userMessage, "error");

        } finally {

            button.disabled = false;
        }
    });

});