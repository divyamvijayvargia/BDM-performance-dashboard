document.addEventListener('DOMContentLoaded', function() {
    // Initialize date pickers with Flatpickr
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const timeFilter = document.getElementById('time-filter');
    const datePickerContainer = document.getElementById('date-picker-container');
    
    // Initialize start date picker
    const startDatePicker = flatpickr(startDateInput, {
        dateFormat: "m/d/Y",
        defaultDate: new Date(),
        onChange: function(selectedDates, dateStr) {
            // Update end date based on selection mode
            updateEndDate(selectedDates[0]);
        }
    });
    
    // Initialize end date picker
    const endDatePicker = flatpickr(endDateInput, {
        dateFormat: "m/d/Y",
        defaultDate: new Date()
    });
    
    // Time filter change handler
    timeFilter.addEventListener('change', function() {
        const selectedValue = this.value;
        
        // Show date picker for daily and weekly options
        if (selectedValue === 'daily' || selectedValue === 'weekly') {
            datePickerContainer.style.display = 'block';
            
            // Update date picker based on selection
            if (selectedValue === 'daily') {
                // For daily, just set a single day
                startDatePicker.setDate(new Date());
                endDatePicker.setDate(new Date());
            } else if (selectedValue === 'weekly') {
                // For weekly, set current week (Monday to Sunday)
                const today = new Date();
                const currentDay = today.getDay(); // 0 = Sunday, 1 = Monday, ...
                
                // Calculate start of week (Monday)
                const startOfWeek = new Date(today);
                const diff = currentDay === 0 ? 6 : currentDay - 1; // Adjust if today is Sunday
                startOfWeek.setDate(today.getDate() - diff);
                
                // Calculate end of week (Sunday)
                const endOfWeek = new Date(startOfWeek);
                endOfWeek.setDate(startOfWeek.getDate() + 6);
                
                startDatePicker.setDate(startOfWeek);
                endDatePicker.setDate(endOfWeek);
            }
            
            // Hide month and year selectors
            document.getElementById('month-filter').parentNode.style.display = 'none';
            document.getElementById('year-filter').parentNode.style.display = 'none';
        } else {
            // Hide date picker for monthly option
            datePickerContainer.style.display = 'none';
            
            // Show month and year selectors
            document.getElementById('month-filter').parentNode.style.display = 'block';
            document.getElementById('year-filter').parentNode.style.display = 'block';
        }
    });
    
    // Update end date based on selected start date and mode
    function updateEndDate(startDate) {
        if (timeFilter.value === 'daily') {
            // For daily, end date is same as start date
            endDatePicker.setDate(startDate);
        } else if (timeFilter.value === 'weekly') {
            // For weekly, end date is 6 days after start date
            const endDate = new Date(startDate);
            endDate.setDate(startDate.getDate() + 6);
            endDatePicker.setDate(endDate);
        }
    }
    
    // Initialize based on default time filter value
    if (timeFilter.value === 'monthly') {
        datePickerContainer.style.display = 'none';
    } else {
        // Trigger the change event to set up the correct date picker
        const event = new Event('change');
        timeFilter.dispatchEvent(event);
    }
}); 