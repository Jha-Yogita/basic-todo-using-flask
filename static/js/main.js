$(document).ready(function() {
    setMinDate();
    
    $('#statsModal').on('show.bs.modal', function() {
        updateStats();
    });
    
    $('.alert').each(function() {
        setTimeout(() => {
            $(this).fadeOut('slow');
        }, 3000);
    });
    
    $('form').on('submit', function() {
        $(this).find('button[type="submit"]').prop('disabled', true);
    });
});

function setMinDate() {
    const dateInput = document.getElementById('due_date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
    }
}

function updateStats() {
    $.ajax({
        url: '/api/stats',
        method: 'GET',
        success: function(data) {
            $('#total-stats').text(data.total);
            $('#completed-stats').text(data.completed);
            $('#active-stats').text(data.active);
            $('#overdue-stats').text(data.overdue);
        },
        error: function() {
            console.log('Error fetching stats');
        }
    });
}

function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

document.addEventListener('DOMContentLoaded', function() {
    const todoItems = document.querySelectorAll('.todo-item');
    
    todoItems.forEach((item, index) => {
        item.style.animationDelay = `${index * 0.1}s`;
    });
});