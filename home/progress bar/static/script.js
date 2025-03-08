let totalProgress = 0;

function loadProgress() {
    fetch('/get_progress')
    .then(response => response.json())
    .then(data => {
        if (data.length === 0) {
            document.getElementById('progressBar').value = 0;
            document.getElementById('progressText').innerText = `0% Completed`;
            return;
        }

        let total = 0;
        data.forEach(item => {
            total += item.progress;
        });

        // Calculate overall progress
        totalProgress = (total / (data.length * 100)) * 100;

        // Update progress bar
        document.getElementById('progressBar').value = totalProgress;
        document.getElementById('progressText').innerText = `${totalProgress.toFixed(0)}% Completed`;
    });
}

function markAsWatched(videoId) {
    fetch('/update_progress', {
        method: 'POST',
        body: JSON.stringify({
            video_id: videoId,
            progress: 50,  // Mark as 50% completed after watching
            quiz_score: 0
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(() => {
        alert("✅ Video watched. Progress Updated.");
        loadProgress();
    });
}

function takeQuiz(videoId) {
    let score = prompt("Answer this question:\n\nWhat is 2 + 2?");
    if (score == 4) {
        alert("✅ Correct Answer! Your progress increased.");
        fetch('/update_progress', {
            method: 'POST',
            body: JSON.stringify({
                video_id: videoId,
                progress: 100,  // Mark as 100% after quiz
                quiz_score: 100
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(() => {
            loadProgress();
        });
    } else {
        alert("❌ Wrong Answer! Try again.");
    }
}

function downloadCertificate() {
    fetch('/generate_certificate')
    .then(response => {
        if (response.ok) {
            window.location.href = '/static/certificate.pdf';
        } else {
            alert("⚠️ Complete all videos and quizzes to download the certificate.");
        }
    });
}

window.onload = loadProgress;
