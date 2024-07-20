async function searchProduct() {
    const query = document.getElementById('search-input').value;
    if (query.length > 2) {
        const response = await fetch(`/search_suggestions?q=${query}`);
        const suggestions = await response.json();
        console.log(suggestions);
        // You can display the suggestions in a dropdown menu or similar
    }
}

async function performSearch() {
    const query = document.getElementById('search-input').value;
    window.location.href = `/search_results?q=${query}`;
}
