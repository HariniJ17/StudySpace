document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        let selectedAnswer = form.querySelector('input[type="radio"]:checked');
        if (selectedAnswer) {
            alert(`You selected: ${selectedAnswer.value}`);
        } else {
            alert("Please select an answer.");
        }
    });
});
