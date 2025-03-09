let completedVideos = 0;
let progress = 0;
let totalVideos = 5;

window.onload = function() {
    fetch('/get_progress')
    .then(response => response.json())
    .then(data => {
        progress = data.progress;
        completedVideos = data.completed_videos;
        document.getElementById('progressBar').value = progress;

        // Enable Quiz Button
        if (completedVideos === totalVideos) {
            document.getElementById('quizButton').disabled = false;
        }
    });
}

function updateProgress(videoId) {
    completedVideos++;
    progress = (completedVideos / totalVideos) * 100;
    document.getElementById('progressBar').value = progress;

    if (completedVideos === totalVideos) {
        document.getElementById('quizButton').disabled = false;
    }

    fetch('/update_progress', {
        method: 'POST',
        body: JSON.stringify({
            video_id: videoId,
            progress: progress
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    });
}
