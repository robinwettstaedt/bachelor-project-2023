$(document).ready(function() {
    // Function to refresh data every 10 seconds
    function refreshData() {
        fetch('/update_data')
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('HTTP error, status = ' + response.status);
                }
                return response.json();  // This returns a promise
            })
            .then(function(data) {
                // Now 'data' is the actual JSON data

                // Determine the row class based on the data
                var zd_log_combined = data['zd_log_all'] + data['zd_invalid_log_all'];

                var isLogAmountEqual = (data['eplf_log_all'] == zd_log_combined);
                var paymentAndValidatedAreEqual = (data['zd_payment_all'] === data['eplf_log_validated']) && (data['eplf_log_validated'] === data['zd_log_validated']);

                var rowClass = (paymentAndValidatedAreEqual && isLogAmountEqual) ? 'green-row' : 'red-row';
                // var darkCell1 = (rowClass == 'green-row') ? 'dark-cell-1-green' : 'dark-cell-1-red';
                // var darkCell2 = (rowClass == 'green-row') ? 'dark-cell-2-green' : 'dark-cell-2-red';

                // Create a new row with the updated data and the determined class
                var newRow = '<tr class="' + rowClass + '">' +
                                '<td>' + getCurrentTime() + '</td>' +
                                '<td>' + data['eplf_payment_all'] + '</td>' +
                                '<td>' + data['zd_payment_all'] + '</td>' +
                                // `<td class="${darkCell1}">` + data['eplf_log_all'] + '</td>' +
                                // `<td class="${darkCell1}">` + data['zd_log_all'] + '</td>' +
                                `<td>` + data['eplf_log_all'] + '</td>' +
                                `<td>` + data['zd_log_all'] + '</td>' +
                                '<td>' + data['zd_invalid_log_all'] + '</td>' +
                                // `<td class="${darkCell2}">` + data['eplf_log_validated'] + '</td>' +
                                // `<td class="${darkCell2}">` + data['zd_log_validated'] + '</td>' +
                                `<td>` + data['eplf_log_validated'] + '</td>' +
                                `<td>` + data['zd_log_validated'] + '</td>' +
                            '</tr>';

                // Append the new row to the table body
                $('#data-table').append(newRow);
            })
            .catch(function(error) {
                console.error('Error:', error);
            });
    }

    // Run refreshData immediately and then every minute
    refreshData();
    setInterval(refreshData, 60000);
});

// Function to get the current time in the format HH:MM:SS
function getCurrentTime() {
    var now = new Date();
    var hours = String(now.getHours()).padStart(2, '0');
    var minutes = String(now.getMinutes()).padStart(2, '0');
    var seconds = String(now.getSeconds()).padStart(2, '0');
    return hours + ':' + minutes + ':' + seconds;
}
