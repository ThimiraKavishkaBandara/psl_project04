// system1.js

async function sendRequest(type) {
    try {
        const genreInput = document.getElementById(`genre${type}`);
        const genre = genreInput.value.trim();
        if (!genre) {
            alert('Please enter a genre.');
            return;
        }

        const endpoint = `/recommend/genre/${type}/${encodeURIComponent(genre)}`;
        const response = await fetch(`http://54.144.168.9:8000${endpoint}`);
        const data = await response.json();

        // Get the list element based on the button type
        const list = document.getElementById(`recommendationsList${type}`);

        // Clear existing list items
        list.innerHTML = "";

        // Populate the list with response data
        let index = 1; // Start index from 1
        for (const key in data) {
            if (data.hasOwnProperty(key)) {
                const listItem = document.createElement('li');
                listItem.textContent = `${index}: ${data[key]}`;
                list.appendChild(listItem);
                index++; // Increment the index
            }
        }
    } catch (error) {
        console.error(error);
    }
}


