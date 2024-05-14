function makeReport() {
    window.location.href = "make_report";
}

function signInWithGoogle() {
    document.getElementById('google-login-form').submit();
}

function myReports() {
    window.location.href = "my_reports";
}

function goBack() {
    window.location.href = "submitted_report";
}

function goBackToAdmin() {
    window.location.href = '/site_admin';
}
function goBackToMyReports() {
    window.location.href = '/my_reports';
}

/* Set max time constraint based on selected date */
function updateTimeConstraint() {
    var selectedDate = document.getElementById('date').value;
    var today = new Date();

    // Format today's date to YYYY-MM-DD using local values
    var formattedToday = today.getFullYear() + '-' + ('0' + (today.getMonth() + 1)).slice(-2) + '-' + ('0' + today.getDate()).slice(-2);

    // Format current local time to HH:MM
    var localTime = ('0' + today.getHours()).slice(-2) + ':' + ('0' + today.getMinutes()).slice(-2);

    // If selected date is today, set max time to current local time
    if (selectedDate === formattedToday) {
        document.getElementById('time').max = localTime;
    } else {
        // If selected date is not today, remove max time constraint
        document.getElementById('time').removeAttribute('max');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    var today = new Date();
    var pastDate = new Date();
    pastDate.setFullYear(today.getFullYear() - 10); // Set to 10 years in the past

    // Format today's date to YYYY-MM-DD without converting to UTC
    var formattedToday = today.getFullYear() + '-' + ('0' + (today.getMonth() + 1)).slice(-2) + '-' + ('0' + today.getDate()).slice(-2);
    var formattedPastDate = pastDate.getFullYear() + '-' + ('0' + (pastDate.getMonth() + 1)).slice(-2) + '-' + ('0' + pastDate.getDate()).slice(-2);

    // Set max and min attributes for date input
    document.getElementById('date').max = formattedToday;
    document.getElementById('date').min = formattedPastDate;

    // Add event listener to date input to update time constraint
    document.getElementById('date').addEventListener('change', updateTimeConstraint);

    // Initialize time constraint based on current date
    updateTimeConstraint();
});


document.addEventListener('DOMContentLoaded', function () {
    var textarea = document.getElementById('description');
    var charCount = document.getElementById('charCount');

    textarea.addEventListener('input', function () {
        var count = textarea.value.length;
        charCount.textContent = count + '/2500';
    });
});

$(document).ready(function() {
    $('#reportForm').submit(function(e) {
        var form = $(this);
        if (form[0].checkValidity() === false) {
            e.preventDefault();
            e.stopPropagation();
        }
    });

    $('.submit-btn').click(function(e) {
        var form = $('#reportForm')[0]; // Get the form element
        if (!form.checkValidity()) {
            return; // If the form is not valid, do nothing
        }
        e.preventDefault(); // Prevent the form from submitting immediately

        var isLoggedIn = $('#isLoggedIn').val();
        if (isLoggedIn === 'false') {
            $('#loginModal').modal('show'); // Show the modal if not logged in
        } else {
            form.submit(); // Submit the form if logged in
        }
    });

    $('#continue-btn').click(function() {
        $('#reportForm').submit(); // Submit the form when continuing anonymously
    });
});

$(document).ready(function() {
    $('#submitNotes').click(function(e) {
        e.preventDefault();  // Prevent default form submission
        $.ajax({
            type: 'POST',
            url: '{% url "set_report_notes" current_report.id %}',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'notes': $('#notes').val()  // Ensure this line correctly references the textarea
            },
            success: function(response) {
                // Update the admin notes paragraph with the new notes from the response
                if (response.notes){
                    $('#adminNotes').html('<strong>Admin Notes: </strong>' + response.notes);
                }
                else{
                    $('#adminNotes').html('<strong>Admin Notes: </strong> No site admins have added notes to this report yet, please check back in the future!');
                }
                // Clear the input field
                $('input[name=notes]').val('');
            },
            error: function(xhr, errmsg, err) {
                console.log("Error: " + xhr.status + ": " + xhr.responseText);
            }
        });
    });
});

$(document).ready(function() {
    $('#resolveButton').click(function(e) {
        e.preventDefault();  // Prevent default form submission
        $.ajax({
            type: 'POST',
            url: '{% url "resolve_report" current_report.id %}',
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'notes': $('#notes').val()  // Send the current notes with the resolve request
            },
            success: function(response) {
                window.location.href = '/site_admin';  // Redirect after successful resolve
            },
            error: function(xhr, errmsg, err) {
                console.log("Error: " + xhr.status + ": " + xhr.responseText);
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var textarea = document.getElementById('notes');
    var charCount = document.getElementById('charCount');

    // Update character count on input
    textarea.addEventListener('input', function() {
        var count = textarea.value.length;
        charCount.textContent = count + '/1000';
    });
});

$(document).ready(function() {
    $('#confirmDeleteButton').click(function() {
        $('#deleteForm').submit();
    });
});