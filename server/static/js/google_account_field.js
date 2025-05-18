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

        // Remove button click handlers (if any)
        this.container.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-account-btn')) {
                this.removeField(e.target);
            }
        });
    }

    initializeFields() {
        // Add remove buttons to all fields except the first one if min_entries > 1
        const fields = this.container.querySelectorAll('.google-account-field-wrapper');
        fields.forEach((field, index) => {
            if (index >= this.options.minEntries) {
                this.addRemoveButton(field);
            }
        });
    }

    addField() {
        const fieldWrapper = this.container.querySelector('.google-account-field-wrapper');
        const newField = fieldWrapper.cloneNode(true);
        const fieldCount = this.container.querySelectorAll('.google-account-field-wrapper').length;
        
        // Update the input field
        const input = newField.querySelector('input');
        input.name = input.name.replace(/\d+$/, fieldCount);
        input.id = input.id.replace(/\d+$/, fieldCount);
        input.value = '';
        
        // Add remove button
        this.addRemoveButton(newField);
        
        // Insert before the add button
        const addButtonContainer = this.container.querySelector('.add-account-btn').parentNode;
        this.container.insertBefore(newField, addButtonContainer);
    }

    removeField(button) {
        const fieldWrapper = button.closest('.google-account-field-wrapper');
        if (fieldWrapper) {
            fieldWrapper.remove();
            this.updateFieldNames();
        }
    }

    addRemoveButton(fieldWrapper) {
        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.className = 'remove-account-btn';
        removeButton.innerHTML = '🗑️';
        removeButton.title = 'Remove this account';
        fieldWrapper.appendChild(removeButton);
    }

    updateFieldNames() {
        // Update the name and id of all fields to maintain sequential order
        const fields = this.container.querySelectorAll('.google-account-field-wrapper');
        fields.forEach((field, index) => {
            const input = field.querySelector('input');
            input.name = input.name.replace(/\d+$/, index);
            input.id = input.id.replace(/\d+$/, index);
        });
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

    // Initialize user management form
    const userManagementContainer = document.getElementById('user-management-form');
    if (userManagementContainer) {
        new GoogleAccountField('user-management-form', {
            minEntries: 1,
            addButtonText: "Add Another User"
        });
    }
}); 