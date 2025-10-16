/**
 * Django Formset Management Script
 *
 * Handles dynamic addition and removal of ingredient forms in the recipe form.
 * Works with Django's inline formset for RecipeIngredients.
 */

document.addEventListener('DOMContentLoaded', function() {
    const formsetContainer = document.getElementById('ingredient-formset');
    const addButton = document.getElementById('add-ingredient');
    const totalFormsInput = document.querySelector('input[name$="-TOTAL_FORMS"]');

    if (!formsetContainer || !addButton || !totalFormsInput) {
        console.warn('Formset elements not found');
        return;
    }

    /**
     * Get the current number of forms in the formset
     */
    function getTotalForms() {
        return parseInt(totalFormsInput.value);
    }

    /**
     * Update the TOTAL_FORMS counter
     */
    function updateTotalForms(value) {
        totalFormsInput.value = value;
    }

    /**
     * Get an empty form template
     * Takes the last form and clones it, then clears all values
     */
    function getEmptyForm() {
        const allForms = formsetContainer.querySelectorAll('.ingredient-form');
        if (allForms.length === 0) {
            console.error('No forms found to clone');
            return null;
        }

        // Clone the last form
        const lastForm = allForms[allForms.length - 1];
        const newForm = lastForm.cloneNode(true);

        // Get the new form index
        const totalForms = getTotalForms();

        // Update form index in all name and id attributes
        const regex = new RegExp('(-\\d+-)', 'g');
        newForm.innerHTML = newForm.innerHTML.replace(regex, `-${totalForms}-`);

        // Clear all input values
        const inputs = newForm.querySelectorAll('input[type="text"], input[type="number"], textarea');
        inputs.forEach(input => {
            input.value = '';
        });

        // Clear any error messages
        const errors = newForm.querySelectorAll('.error-message');
        errors.forEach(error => error.remove());

        // Uncheck any checkboxes (like DELETE checkbox)
        const checkboxes = newForm.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });

        return newForm;
    }

    /**
     * Add a new ingredient form to the formset
     */
    function addForm() {
        const newForm = getEmptyForm();
        if (!newForm) return;

        // Add the new form to the container
        formsetContainer.appendChild(newForm);

        // Update the total forms count
        updateTotalForms(getTotalForms() + 1);

        // Attach remove handler to the new form's remove button
        const removeButton = newForm.querySelector('.remove-ingredient');
        if (removeButton) {
            removeButton.addEventListener('click', function() {
                removeForm(newForm);
            });
        }

        // Focus on the first input of the new form
        const firstInput = newForm.querySelector('input[type="text"]');
        if (firstInput) {
            firstInput.focus();
        }
    }

    /**
     * Remove an ingredient form from the formset
     * If the form is saved (has an ID), mark it for deletion
     * Otherwise, just remove it from the DOM
     */
    function removeForm(formElement) {
        // Check if this is a saved form (has an ID field with a value)
        const idInput = formElement.querySelector('input[name$="-id"]');
        const deleteInput = formElement.querySelector('input[name$="-DELETE"]');

        if (idInput && idInput.value) {
            // This is a saved form, mark it for deletion
            if (deleteInput) {
                deleteInput.checked = true;
            }
            // Hide the form instead of removing it
            formElement.style.display = 'none';
        } else {
            // This is a new unsaved form, just remove it
            formElement.remove();
            // Update total forms count
            updateTotalForms(getTotalForms() - 1);
            // Re-index remaining forms
            reindexForms();
        }
    }

    /**
     * Re-index all visible forms after deletion
     * This ensures form indices are sequential (0, 1, 2, ...)
     */
    function reindexForms() {
        const visibleForms = Array.from(formsetContainer.querySelectorAll('.ingredient-form'))
            .filter(form => form.style.display !== 'none');

        visibleForms.forEach((form, index) => {
            // Update all name and id attributes with the new index
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                ['name', 'id'].forEach(attr => {
                    if (input.hasAttribute(attr)) {
                        const value = input.getAttribute(attr);
                        input.setAttribute(attr, value.replace(/-\d+-/, `-${index}-`));
                    }
                });

                // Update for attribute in labels
                const label = form.querySelector(`label[for="${input.id}"]`);
                if (label) {
                    label.setAttribute('for', input.id);
                }
            });
        });
    }

    /**
     * Initialize existing remove buttons
     */
    function initializeRemoveButtons() {
        const removeButtons = formsetContainer.querySelectorAll('.remove-ingredient');
        removeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const form = button.closest('.ingredient-form');
                if (form) {
                    removeForm(form);
                }
            });
        });
    }

    // Initialize
    initializeRemoveButtons();

    // Add button click handler
    addButton.addEventListener('click', addForm);

    // Prevent form submission on Enter key in ingredient fields
    const ingredientInputs = formsetContainer.querySelectorAll('input[type="text"]');
    ingredientInputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                addForm();
            }
        });
    });
});
