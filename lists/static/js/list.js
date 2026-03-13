// Superlists namespace
var Superlists = {};

Superlists.initialize = function() {
    // Get input box
    var inputBox = $('#id_new_item');

    // Bind keyup event to hide error when user types
    inputBox.on('keyup', function() {
        Superlists.hideError();
    });
};

Superlists.hideError = function() {
    // Helper function to hide error elements
    $('.has-error').removeClass('has-error').hide();
};

Superlists.getErrorElement = function() {
    // Helper function to find error elements
    return $('.has-error');
};

// Initialize on page load
$(document).ready(function() {
    Superlists.initialize();
});
