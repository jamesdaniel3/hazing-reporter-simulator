function goBackToAdmin() {
    window.location.href = '/site_admin';
}
function goBackToMyReports() {
    window.location.href = '/my_reports';
}

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