// Function to fetch and display recommended movies in a scrolling container
// recommendButton.addEventListener('click', () => getRecommendations(movieRatingsArray));
const recommendButton = document.getElementById('getRecommendationsButton');

async function recommendMovies() {
    const response = await fetch('/recommend/all_genres/highly_rated/');
    const data = await response.json();
    displayMoviesScrollingContainer(data);
}

// Function to display movies in a scrolling container
async function displayMoviesScrollingContainer(movieRatings) {
    const scrollingContainer = document.getElementById('scrollingContainer');

    // Array to store entered movie ratings as objects
    const movieRatingsArray = [];

    for (const movieId in movieRatings) {
        const movieTitle = movieRatings[movieId];
        // console.log(movieId);
        // console.log(movieTitle);
        // console.log("called");


        const response = await fetch(`/movies/${movieId}`)
        const movieEntryDiv = document.createElement('div');


        if (response.ok) {
            const image = await response.json();
            const imageDiv = document.createElement('img');
            imageDiv.setAttribute("src", image)

            movieEntryDiv.appendChild(imageDiv)


        }
        //div to contain each movie entry

        // Create a paragraph element for each movie
        const movieParagraph = document.createElement('p');
        movieParagraph.textContent = `MovieID: ${movieId}, Movie Title: ${movieTitle}`;

        // Create an input field for user ratings
        const ratingInput = document.createElement('input');
        ratingInput.type = 'number';
        ratingInput.min = 1;
        ratingInput.max = 10;
        ratingInput.step = 1;
        ratingInput.placeholder = 'Enter rating';

        // Add an event listener for input changes
        ratingInput.addEventListener('input', (event) => {
            const enteredRank = parseInt(event.target.value);

            // Check if the movie already has a rating in the array
            const existingRatingIndex = movieRatingsArray.findIndex(item => item.movieId === movieId);

            // If the movie has a rating, update it; otherwise, add a new object to the array
            if (existingRatingIndex !== -1) {
                movieRatingsArray[existingRatingIndex].rating = enteredRank;
            } else {
                // movieRatingsArray.push({ movieId, movieTitle, rating: enteredRank });
                if (enteredRank) {
                    movieRatingsArray.push({ movie_id: parseInt(movieId), ratings: enteredRank });
                }
                // movieRatingsArray.push([parseInt(movieId), enteredRank]);
            }

            // For demonstration purposes, you can log the array
            console.log(movieRatingsArray);
        });

        // Append elements to the movie entry div
        movieEntryDiv.appendChild(movieParagraph);
        movieEntryDiv.appendChild(ratingInput);

        // Append the movie entry div to the scrolling container
        scrollingContainer.appendChild(movieEntryDiv);
    }

    // Create a button to trigger the recommendations
    // const recommendButton = document.createElement('button');
    // const recommendButton = document.getElementById('getRecommendationsButton');
    // recommendButton.textContent = 'Get Recommendations';
    recommendButton.addEventListener('click', () => getRecommendations(movieRatingsArray));
    // console.log("recommendButton", recommendButton);
    console.log("movieRatingsArray", movieRatingsArray);
    // Append the button to the scrolling container
    // scrollingContainer.appendChild(recommendButton);

    // Return the array of movie ratings
    return movieRatingsArray;
}


// Function to get recommendations from the server
async function getRecommendations(userRatings) {
    // console.log("called");
    try {
        recommendButton.disabled = true
        const response = await fetch('/recommendations/ibcf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            // body: JSON.stringify({ user_ratings: userRatings }),  // Ensure the correct JSON structure
            body: JSON.stringify({ user_ratings: userRatings }),  // Ensure the correct JSON structure
        });

        if (response.ok) {
            const recommendations = await response.json();
            console.log(recommendations);  // Log recommendations to the console
            displayRecommendationsDropdown(recommendations);
            recommendButton.disabled = trfalseue

        } else {
            console.error('Error fetching recommendations:', response.statusText);
            recommendButton.disabled = false

        }
    } catch (error) {
        console.error('Error:', error.message);
        recommendButton.disabled = false

    }
}


// Function to display recommendations in a dropdown container
function displayRecommendationsDropdown(recommendations) {
    // Assuming you have a container with the id 'recommendationsDropdownContainer'
    const dropdownContainer = document.getElementById('recommendationsDropdownContainer');
    dropdownContainer.innerHTML = ''; // Clear existing content

    // Create a select element for the dropdown
    const dropdown = document.createElement('select');

    // Iterate through recommendations and create options
    for (const movieId in recommendations) {
        const option = document.createElement('option');
        option.value = movieId;
        option.text = recommendations[movieId];
        dropdown.appendChild(option);
    }

    // Append the dropdown to the container
    dropdownContainer.appendChild(dropdown);
}

// Call the recommendMovies function initially to display the movies
recommendMovies();


