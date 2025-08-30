document.addEventListener("DOMContentLoaded", function () {
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
            document.body.style.overflow = 'auto'; // Restore scrolling
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