document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    const daySelect = document.getElementById('daySelect');
    const monthSelect = document.getElementById('monthSelect');
    const yearSelect = document.getElementById('yearSelect');
    const generateBtn = document.getElementById('generateBtn');
    const tableContainer = document.getElementById('tableContainer');
    const attendanceTableBody = document.getElementById('attendanceTableBody');
    const logoutBtn = document.getElementById('logoutBtn');

    // Populate years (current year and 2 years back)
    function populateYears() {
        const currentYear = new Date().getFullYear();
        yearSelect.innerHTML = '<option value="" selected disabled>Select year</option>';
        for (let year = currentYear; year >= currentYear - 2; year--) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            yearSelect.appendChild(option);
        }
    }

    // Populate days based on selected month and year
    function populateDays() {
        const month = parseInt(monthSelect.value);
        const year = parseInt(yearSelect.value);

        // Clear existing options
        daySelect.innerHTML = '<option value="" selected disabled>Select day</option>';

        if (!month || !year) return;

        const daysInMonth = new Date(year, month, 0).getDate();

        // Add new date options
        for (let i = 1; i <= daysInMonth; i++) {
            const option = document.createElement('option');
            option.value = i;
            option.textContent = i;
            daySelect.appendChild(option);
        }
    }
    async function getAttendanceData(day, month, year) {
        const requestData = { day, month, year };
    
        try {
            const response = await fetch("/api/generate-attendance", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(requestData)
            });
    
            if (!response.ok) {
                console.error("Server returned an error:", response.status);
                return null;
            }
    
            return await response.json(); // Directly returning parsed JSON
        } catch (error) {
            console.error("Error fetching data:", error);
            return null;
        }
    }
    
    
        
        
    // Generate attendance table
    async function generateAttendanceTable() {
        const day = document.getElementById("daySelect").value;
        const month = document.getElementById("monthSelect").value;
        const year = document.getElementById("yearSelect").value;
        const attendanceTableBody = document.getElementById("attendanceTableBody");
        const tableContainer = document.getElementById("tableContainer");
    
        if (!day || !month || !year) {
            alert('Please select day, month, and year');
            return;
        }
    
        // Fetch attendance data
        const attendanceData = await getAttendanceData(day, month, year);
    
        if (!attendanceData || attendanceData.length === 0) {
            alert("No attendance data found for the selected date.");
            return;
        }
    
        // Clear existing table content
        attendanceTableBody.innerHTML = '';
    
        // Populate table with data
        attendanceData.forEach(record => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${record.rollNo}</td>
                <td>${record.name}</td>
                <td>${record.date}</td>
                <td>${record.entryTime}</td>
                <td>${record.exitTime}</td>
            `;
            attendanceTableBody.appendChild(row);
        });
    
        // Show table container with animation
        tableContainer.classList.remove('d-none');
        tableContainer.classList.add('fade-in');
    }
    

    // Event Listeners
    monthSelect.addEventListener('change', populateDays);
    yearSelect.addEventListener('change', populateDays);
    generateBtn.addEventListener('click', generateAttendanceTable);
    logoutBtn.addEventListener('click', function() {
        // For now, just reload the page since we don't have authentication
        // window.location.reload();
        //TODO: Here make the url to point to the sign-in page path
        window.location.href = 'http://127.0.0.1:5000/';

    });

    // Initialize years and trigger month change to populate days
    populateYears();
    // Set default year to current year
    yearSelect.value = new Date().getFullYear();
    // Set default month to current month
    monthSelect.value = new Date().getMonth() + 1;
    // Populate days for current month/year
    populateDays();
});
