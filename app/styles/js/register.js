document.addEventListener('DOMContentLoaded', function() {
    const registrationForm = document.getElementById('registrationForm');
    const batchYearSelect = document.getElementById('batchYear');

    // Populate batch years (current year and 4 years back)
    function populateBatchYears() {
        const currentYear = new Date().getFullYear();
        for (let year = currentYear; year >= currentYear - 4; year--) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            batchYearSelect.appendChild(option);
        }
    }

    // Handle form submission
    registrationForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Create FormData object
        const formData = new FormData(registrationForm);
        const userData = Object.fromEntries(formData.entries());

        // Send registration request to server
        fetch('/register-user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("place the card in the Rfid machine");
                alert('User registered successfully!');
                //TODO:Change this url into server url admin page dashbaord
                window.location.href = 'http://127.0.0.1:5000/admin-dashboard';
            } else {
                alert('Error registering user: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error registering user. Please try again.');
        });
    });

    // Initialize batch years
    populateBatchYears();
});



// document.addEventListener('DOMContentLoaded', function () {
//     const registrationForm = document.getElementById('registrationForm');
//     const batchYearSelect = document.getElementById('batchYear');

//     // Populate batch years (current year and 4 years back)
//     function populateBatchYears() {
//         const currentYear = new Date().getFullYear();
//         for (let year = currentYear; year >= currentYear - 4; year--) {
//             const option = document.createElement('option');
//             option.value = year;
//             option.textContent = year;
//             batchYearSelect.appendChild(option);
//         }
//     }

//     // Handle form submission
//     registrationForm.addEventListener('submit', async function (e) {
//         e.preventDefault();
    
//         // Collect form data and convert it into a JSON object
//         const formData = new FormData(registrationForm);
//         const userData = {};
//         formData.forEach((value, key) => {
//             userData[key] = value;
//         });
    
//         // Debugging: Show JSON data being sent
//         const jsonData = JSON.stringify(userData, null, 2);
//         console.log("Sending User Data:", userData);
//         alert("Sending JSON Data:\n" + jsonData); // Alert to see JSON being sent
    
//         try {
//             const response = await fetch('/register-user', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json' // Ensure JSON format
//                 },
//                 body: jsonData // Convert to JSON string
//             });
    
//             const data = await response.json();
//             console.log("Server Response:", data); // Debugging
    
//             if (data.success) {
//                 alert("Place the card in the RFID machine");
//                 alert('User registered successfully!');
//                 window.location.href = '/';
//             } else {
//                 alert('Error registering user: ' + data.error);
//             }
//         } catch (error) {
//             console.error('Error:', error);
//             alert('Error registering user. Please try again.');
//         }
//     });
    
//     // Initialize batch years
//     populateBatchYears();
    

    populateBatchYears();
// });
