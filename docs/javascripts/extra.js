document.addEventListener("DOMContentLoaded", function () {
    // Find all table rows with a 'data-href' attribute
    const rows = document.querySelectorAll('tr[data-href]');

    rows.forEach(row => {
        // Change the cursor to a pointer on hover to indicate it's clickable
        row.style.cursor = 'pointer';

        // Add a click event listener
        row.addEventListener('click', () => {
            // Navigate to the URL specified in the 'data-href' attribute
            window.location.href = row.dataset.href;
        });
    });


     // Select all headers you want to be collapsible
  document.querySelectorAll("h2, h3, h4").forEach(header => {
    // Add a class for CSS styling and to identify them
    header.classList.add("collapsible-header");

    // Create the div that will hold the collapsible content
    const wrapper = document.createElement("div");
    wrapper.classList.add("collapsible-content");

    // Move all sibling elements into the wrapper until the next header of the same or higher level
    let next = header.nextElementSibling;
    while (next && !(next.tagName.match(/^H[1-4]$/) && next.tagName <= header.tagName)) {
      const temp = next.nextElementSibling;
      wrapper.appendChild(next);
      next = temp;
    }

    // Insert the wrapper right after the header
    header.after(wrapper);

    // Add the click event listener to the header
    header.addEventListener("click", () => {
      // Toggle the 'active' class on the header for styling (e.g., rotating the arrow)
      header.classList.toggle("active");

      // Toggle the display of the content wrapper
      if (wrapper.style.display === "none" || wrapper.style.display === "") {
        wrapper.style.display = "block";
      } else {
        wrapper.style.display = "none";
      }
    });

    // Start with all content collapsed by default
    wrapper.style.display = "block"; // Changed from "none"
    header.classList.add("active");   // Add "active" class so it's bold initially
  });
});

function openFullscreen(imageElement, url) {
//    console.log('openFullscreen');
//    console.log(imageElement);
    const fullscreenContainer = document.createElement('div');
    fullscreenContainer.style.position = 'fixed';
    fullscreenContainer.style.top = '0';
    fullscreenContainer.style.left = '0';
    fullscreenContainer.style.width = '100%';
    fullscreenContainer.style.height = '100%';
    fullscreenContainer.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    fullscreenContainer.style.display = 'flex';
    fullscreenContainer.style.justifyContent = 'center';
    fullscreenContainer.style.alignItems = 'center';
    fullscreenContainer.style.zIndex = '1000';

    const fullscreenImage = document.createElement('img');
//    fullscreenImage.src = imageElement.src + '?format=jpg&name=orig'
    fullscreenImage.src = url
    fullscreenImage.style.maxWidth = '100%';
    fullscreenImage.style.maxHeight = '100%';

    fullscreenContainer.appendChild(fullscreenImage);
    document.body.appendChild(fullscreenContainer);

// Function to close the overlay
    const closeFullscreen = () => {
        if (document.body.contains(fullscreenContainer)) {
            document.body.removeChild(fullscreenContainer);
//            document.body.style.overflow = 'auto'; // Restore scrolling
            // Remove the keydown listener when not needed
            document.removeEventListener('keydown', handleKeydown);
        }
    };

    fullscreenContainer.onclick = closeFullscreen;

    // Enhancement: Also close on 'Escape' key press
    const handleKeydown = (event) => {
        if (event.key === 'Escape') {
            closeFullscreen();
        }
    };

    document.addEventListener('keydown', handleKeydown);
}