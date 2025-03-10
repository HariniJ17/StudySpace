document.getElementById("quiz-form").addEventListener("submit", function(event) {
    event.preventDefault();  // Prevent form submission

    let correctAnswers = {
        q1: "c",  // Correct answer for Question 1
        q2: "c",  // Correct answer for Question 2
        q3: "c",  // Correct answer for Question 3
        q4: "c",  // Correct answer for Question 4
        q5: "c",  // Correct answer for Question 5
        q6: "a",  // Correct answer for Question 6
        q7: "a",  // Correct answer for Question 7
        q8: "a",  // Correct answer for Question 8
        q9: "a",  // Correct answer for Question 9
        q10: "c"  // Correct answer for Question 10
    };

    let userAnswers = {};
    let correctCount = 0;
    let incorrectCount = 0;

    // Loop through all questions to check answers
    for (let question in correctAnswers) {
        let selectedOption = document.querySelector(`input[name="${question}"]:checked`);
        if (selectedOption) {
            userAnswers[question] = selectedOption.value;
            if (selectedOption.value === correctAnswers[question]) {
                correctCount++;
            } else {
                incorrectCount++;
            }
        }
    }

    // Show the result in the modal (pop-up box)
    let resultModal = document.getElementById("result-modal");
    let scoreText = document.getElementById("score");
    scoreText.innerHTML = `You got ${correctCount} correct answers and ${incorrectCount} wrong answers.`;
    resultModal.style.display = "block";  // Show the modal

    // Close the modal when the user clicks the "x" (close) button
    document.querySelector(".close").addEventListener("click", function() {
        resultModal.style.display = "none";
    });

    // Close the modal when the user clicks outside of the modal content
    window.addEventListener("click", function(event) {
        if (event.target == resultModal) {
            resultModal.style.display = "none";
        }
    });
});
