document.addEventListener('DOMContentLoaded', function () {
    // Initialize components
    const monthSelect = document.getElementById('monthSelect');
    const yearSelect = document.getElementById('yearSelect');
    const generateBtn = document.getElementById('generateBtn');
    const tableContainer = document.getElementById('tableContainer');
    const attendanceTableBody = document.getElementById('attendanceTableBody');
    const logoutBtn = document.getElementById('logoutBtn');
    // const rfidTag = document.getElementById('')
    let rfidTag = document.querySelector(".nav-link").innerText.split(": ")[1];

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

    // Fetch attendance data
    async function getAttendanceData(month, year) {
        try {
            const response = await fetch("/api/student-generate-attendance", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ month, year, rfidTag})
            });
            if (!response.ok) {
                console.error("Server returned an error:", response.status);
                return null;
            }
            return await response.json();
        } catch (error) {
            console.error("Error fetching data:", error);
            return null;
        }
    }
    // Generate attendance table
    async function generateAttendanceTable() {
        const month = monthSelect.value;
        const year = yearSelect.value;

        if (!month || !year) {
            alert('Please select both month and year');
            return;
        }

        console.log("Fetching attendance for:", month, year); // Debugging

        const attendanceData = await getAttendanceData(month, year);
        if (!attendanceData || attendanceData.length === 0) {
            alert("No attendance data found for the selected period.");
            return;
        }

        attendanceTableBody.innerHTML = '';
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

        tableContainer.classList.remove('d-none');
        tableContainer.classList.add('fade-in');
    }

    // Event Listeners
    generateBtn.addEventListener('click', generateAttendanceTable);

    if (logoutBtn) {
        logoutBtn.addEventListener('click', function () {
            // alert('Logout functionality to be implemented');
            //TODO: Here make the url to point to the sign-in page path
            window.location.href = 'http://127.0.0.1:5000/';

        });
    }

    // Initialize dropdowns
    populateYears();
});