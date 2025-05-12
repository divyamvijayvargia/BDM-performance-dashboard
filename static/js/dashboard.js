document.addEventListener('DOMContentLoaded', function() {
    // Function to export table data to CSV
    window.exportTableToCSV = function() {
        const table = document.getElementById('bdm-performance-table');
        let csv = [];
        
        // Get all rows from table
        const rows = Array.from(table.querySelectorAll('tr'));
        
        rows.forEach(row => {
            // Get all cells from row
            const cells = Array.from(row.querySelectorAll('th, td'));
            
            // Extract text from each cell
            const rowData = cells.map(cell => {
                // Escape commas and quotes
                return '"' + cell.textContent.replace(/"/g, '""') + '"';
            });
            
            // Add row to CSV
            csv.push(rowData.join(','));
        });
        
        // Create CSV content
        const csvContent = csv.join('\n');
        
        // Create download link
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        
        // Create temporary link and trigger download
        const link = document.createElement('a');
        link.setAttribute('href', url);
        
        // Generate filename with current date
        const now = new Date();
        const filename = `bdm_performance_${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}.csv`;
        
        link.setAttribute('download', filename);
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };
    
    // Function to add export button to DataTable
    function addExportButton() {
        // Find the DataTable's toolbar area
        const toolbar = document.querySelector('.dataTables_wrapper .row:first-child .col-md-6:last-child');
        
        if (toolbar) {
            // Create export button
            const exportBtn = document.createElement('button');
            exportBtn.className = 'btn btn-sm btn-outline-secondary ms-2';
            exportBtn.innerHTML = '<i class="bi bi-download"></i> Export CSV';
            exportBtn.onclick = window.exportTableToCSV;
            
            // Append button to toolbar
            toolbar.appendChild(exportBtn);
        }
    }
    
    // Call function after DataTable initialization (with a slight delay)
    setTimeout(addExportButton, 500);
});