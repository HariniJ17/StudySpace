document.addEventListener("DOMContentLoaded", function () {
    const faqs = document.querySelectorAll(".faq");

    faqs.forEach(faq => {
        const question = faq.querySelector(".faq-question");
        const answer = faq.querySelector(".faq-answer");
        const toggleBtn = faq.querySelector(".toggle-btn");

        question.addEventListener("click", () => {
            const isOpen = answer.style.maxHeight;

            // Close all answers before opening a new one (optional)
            document.querySelectorAll(".faq-answer").forEach(ans => {
                ans.style.maxHeight = null;
                ans.style.padding = "0 10px";
            });
            document.querySelectorAll(".toggle-btn").forEach(btn => btn.textContent = "+");

            if (!isOpen || isOpen === "0px") {
                answer.style.maxHeight = answer.scrollHeight + "px";
                answer.style.padding = "10px 10px";
                toggleBtn.textContent = "-";
            }
        });
    });
});



