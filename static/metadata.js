/**
 * Metadata Module for Py Home Gallery
 *
 * Handles fetching and displaying media metadata in a modal
 */

class MetadataViewer {
    constructor() {
        this.modal = null;
        this.init();
    }

    init() {
        // Create modal if it doesn't exist
        if (!document.querySelector('.metadata-modal')) {
            this.createModal();
        } else {
            this.modal = document.querySelector('.metadata-modal');
        }

        // Attach event listeners
        this.attachEventListeners();
    }

    createModal() {
        const modal = document.createElement('div');
        modal.className = 'metadata-modal';
        modal.innerHTML = `
            <div class="metadata-content">
                <div class="metadata-header">
                    <h2>Media Information</h2>
                    <button class="metadata-close" aria-label="Close">&times;</button>
                </div>
                <div class="metadata-body">
                    <div class="metadata-loading">Loading metadata...</div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        this.modal = modal;
    }

    attachEventListeners() {
        // Close modal on background click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });

        // Close button
        const closeBtn = this.modal.querySelector('.metadata-close');
        closeBtn.addEventListener('click', () => this.close());

        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('active')) {
                this.close();
            }
        });
    }

    async show(mediaPath) {
        // Show modal
        this.modal.classList.add('active');

        // Show loading state
        const body = this.modal.querySelector('.metadata-body');
        body.innerHTML = '<div class="metadata-loading">Loading metadata...</div>';

        try {
            // Fetch metadata from API
            const response = await fetch(`/api/metadata/${mediaPath}`);
            const data = await response.json();

            if (data.success) {
                this.displayMetadata(data.metadata);
            } else {
                this.displayError(data.error || 'Failed to load metadata');
            }
        } catch (error) {
            console.error('Error fetching metadata:', error);
            this.displayError('Failed to load metadata');
        }
    }

    displayMetadata(metadata) {
        const body = this.modal.querySelector('.metadata-body');
        let html = '';

        // Display each section
        for (const [sectionKey, sectionData] of Object.entries(metadata)) {
            if (Object.keys(sectionData).length === 0) continue;

            // Format section title
            const sectionTitle = sectionKey
                .replace(/_/g, ' ')
                .split(' ')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ');

            html += `
                <div class="metadata-section">
                    <h3>${sectionTitle}</h3>
            `;

            // Display each row in the section
            for (const [key, value] of Object.entries(sectionData)) {
                html += `
                    <div class="metadata-row">
                        <span class="metadata-label">${key}</span>
                        <span class="metadata-value">${value}</span>
                    </div>
                `;
            }

            html += `</div>`;
        }

        if (html === '') {
            html = '<div class="metadata-loading">No metadata available</div>';
        }

        body.innerHTML = html;
    }

    displayError(message) {
        const body = this.modal.querySelector('.metadata-body');
        body.innerHTML = `<div class="metadata-error">${message}</div>`;
    }

    close() {
        this.modal.classList.remove('active');
    }
}

// Initialize metadata viewer
const metadataViewer = new MetadataViewer();

// Function to add info icons to grid items
function addInfoIcons() {
    const gridItems = document.querySelectorAll('.grid-item');

    gridItems.forEach(item => {
        // Skip if already has info icon
        if (item.querySelector('.info-icon')) return;

        // Get media path from the link
        const link = item.querySelector('a');
        if (!link) return;

        const href = link.getAttribute('href');
        const mediaPath = href.replace('/media/', '');

        // Create info icon
        const infoIcon = document.createElement('div');
        infoIcon.className = 'info-icon';
        infoIcon.innerHTML = 'i';
        infoIcon.setAttribute('title', 'View metadata');
        infoIcon.setAttribute('aria-label', 'View metadata');

        // Add click handler
        infoIcon.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            metadataViewer.show(mediaPath);
        });

        // Add to grid item link
        link.appendChild(infoIcon);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', addInfoIcons);

// Export for use in dynamic content (infinite scroll, etc.)
window.addInfoIcons = addInfoIcons;
window.metadataViewer = metadataViewer;
