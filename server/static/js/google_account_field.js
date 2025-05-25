class GoogleAccountField {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container with id ${containerId} not found`);
            return;
        }

        this.options = {
            minEntries: 1,
            addButtonText: "Add Another Account",
            ...options
        };

        this.setupEventListeners();
        this.initializeFields();
    }

    setupEventListeners() {
        // Add button click handler
        const addButton = this.container.querySelector('.add-account-btn');
        if (addButton) {
            addButton.addEventListener('click', () => this.addField());
        }
    }

}

// Initialize all google account fields on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize scorer emails in tournament creation form
    const scorerEmailsContainer = document.getElementById('scorer-emails');
    if (scorerEmailsContainer) {
        new GoogleAccountField('scorer-emails', {
            minEntries: 1,
            addButtonText: "Add Another Scorer"
        });
    }
}); 