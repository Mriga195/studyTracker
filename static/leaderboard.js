// Asynchronous function to fetch user scores from Flask API
async function fetchUserScores() {
    try {
        const response = await fetch('/api/user_scores');
        if (!response.ok) {
            throw new Error('Failed to fetch user scores');
        }
        const data = await response.json();
        return data; // Return the retrieved user scores data
    } catch (error) {
        console.error('Error fetching user scores:', error);
        return []; // Return empty array if fetch fails
    }
}

// Function to calculate total score for each user
function calculateLeaderboardData(data) {
    const leaderboardData = {};

    // Calculate total score for each user
    data.forEach(item => {
        const { username, score } = item; // Destructure item into username and score
        if (!leaderboardData[username]) {
            leaderboardData[username] = 0;
        }
        leaderboardData[username] += score;
    });

    return leaderboardData;
}

// Function to render leaderboard table
function renderLeaderboard(leaderboardData) {
    const leaderboardTable = document.querySelector('#leaderboard tbody');
    leaderboardTable.innerHTML = '';

    // Sort users based on total score (descending order)
    const sortedUsers = Object.entries(leaderboardData)
        .sort((a, b) => b[1] - a[1]);

    // Populate the table with sorted data
    sortedUsers.forEach(([username, totalScore]) => {
        const row = `<tr>
            <td>${username}</td>
            <td>${totalScore}</td>
        </tr>`;
        leaderboardTable.innerHTML += row;
    });
}

// Fetch user scores asynchronously and then process and render the leaderboard
fetchUserScores()
    .then(userScores => {
        console.log('User Scores:', userScores);

        // Calculate leaderboard data
        const leaderboardData = calculateLeaderboardData(userScores);

        // Render the leaderboard
        renderLeaderboard(leaderboardData);
    })
    .catch(error => {
        console.error('Error:', error);
    });
