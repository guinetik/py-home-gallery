/**
 * Shared gallery functionality for Isotope grid and GLightbox
 */

/**
 * Initialize Isotope masonry grid
 * @param {string} gridSelector - CSS selector for grid container
 * @returns {Isotope} Isotope instance
 */
function initializeIsotope(gridSelector) {
    const grid = document.querySelector(gridSelector);
    if (!grid) {
        console.error('Grid element not found:', gridSelector);
        return null;
    }

    console.log('Initializing Isotope');
    const iso = new Isotope(grid, {
        itemSelector: '.grid-item',
        layoutMode: 'masonry',
        percentPosition: true,
        masonry: {
            columnWidth: '.grid-sizer'
        }
    });

    // Re-layout as EACH image loads to prevent overlaps
    const imgLoad = imagesLoaded(grid);
    imgLoad.on('progress', function() {
        // Layout after each image loads
        iso.layout();
    });

    imgLoad.on('always', function() {
        console.log('All images loaded, final layout');
        iso.layout();
    });

    console.log('Isotope initialized - grid visible immediately');
    return iso;
}

/**
 * Initialize GLightbox for media viewing
 * @param {string} selector - CSS selector for lightbox items
 * @returns {GLightbox} GLightbox instance
 */
function initializeGLightbox(selector, options) {
    selector = selector || '.glightbox';
    options = options || {};

    // Default configuration optimized for Flask dev server
    const defaultConfig = {
        selector: selector,
        touchNavigation: true,
        loop: true,
        preload: false,  // Disable preload - fixes slowness on Windows/Flask dev server
        // Alternative: Set to true for production servers with better performance
    };

    // Merge user options with defaults
    const config = { ...defaultConfig, ...options };

    const lightbox = GLightbox(config);

    console.log('GLightbox initialized with preload:', config.preload);
    return lightbox;
}

/**
 * Hide initial loading spinner
 * @param {string} spinnerId - ID of spinner element
 */
function hideLoadingSpinner(spinnerId) {
    spinnerId = spinnerId || 'initialLoading';
    const spinner = document.getElementById(spinnerId);

    if (spinner) {
        spinner.classList.add('hidden');
        console.log('Loading spinner hidden');
    }
}

/**
 * Setup window resize handler for Isotope
 * @param {Isotope} iso - Isotope instance
 */
function setupResizeHandler(iso) {
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (iso) iso.layout();
        }, 250);
    });
}

/**
 * Initialize complete gallery (Isotope + GLightbox + spinner)
 * @param {Object} options - Configuration options
 * @param {string} options.gridSelector - Grid container selector (default: '.grid')
 * @param {string} options.lightboxSelector - Lightbox item selector (default: '.glightbox')
 * @param {string} options.spinnerId - Loading spinner ID (default: 'initialLoading')
 * @returns {Object} Object containing iso and lightbox instances
 */
function initializeGallery(options) {
    options = options || {};
    const gridSelector = options.gridSelector || '.grid';
    const lightboxSelector = options.lightboxSelector || '.glightbox';
    const spinnerId = options.spinnerId || 'initialLoading';

    // Get grid element
    const grid = document.querySelector(gridSelector);

    // Initialize Isotope
    const iso = initializeIsotope(gridSelector);

    // Hide loading spinner
    hideLoadingSpinner(spinnerId);

    // Initialize GLightbox
    const lightbox = initializeGLightbox(lightboxSelector);

    // Setup resize handler
    if (iso) {
        setupResizeHandler(iso);
    }

    return { iso, lightbox, grid };
}
