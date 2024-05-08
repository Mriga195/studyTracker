let timer;
let isBreakTime = false;

function startTimer() {
    const duration = isBreakTime ? 300 : 1500; // 5 minutes break or 25 minutes focus
    const timerDisplay = document.getElementById('timer');
    const startButton = document.getElementById('start-btn');
    const resetButton = document.getElementById('reset-btn');

    startButton.disabled = true;
    resetButton.disabled = false;

    let timeLeft = duration;
    displayTimeLeft(timeLeft, timerDisplay);

    timer = setInterval(() => {
        timeLeft--;
        displayTimeLeft(timeLeft, timerDisplay);

        if (timeLeft === 0) {

            if (isBreakTime === false){
                
                fetch('update', {method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({}),
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data.message);  // Log the server response
                })
                .catch(error => {
                    console.error('Error updating focus time count:', error);
                });
            } 
            
            clearInterval(timer);
            isBreakTime = !isBreakTime;
            startButton.disabled = false;
            resetButton.disabled = true;
            startButton.innerText = isBreakTime ? 'Start Break' : 'Start Focus';
        }
    }, 1000);
}

function displayTimeLeft(seconds, timerDisplay) {
    const minutes = Math.floor(seconds / 60);
    const remainderSeconds = seconds % 60;
    const display = `${minutes}:${remainderSeconds < 10 ? '0' : ''}${remainderSeconds}`;
    timerDisplay.textContent = display;
}

function resetTimer() {
    clearInterval(timer);
    document.getElementById('timer').textContent = '25:00';
    isBreakTime = false;
    document.getElementById('start-btn').innerText = 'Start Focus';
    document.getElementById('start-btn').disabled = false;
    document.getElementById('reset-btn').disabled = true;
}
