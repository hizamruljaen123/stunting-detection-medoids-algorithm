// Sidebar toggle functionality
$(document).ready(function() {
    // Toggle sidebar on button click
    $('#sidebarCollapse').on('click', function() {
        $('#sidebar').toggleClass('active');
        $('.main-content').toggleClass('active');
    });

    // Initialize DataTables
    $('.data-table').DataTable({
        responsive: true,
        language: {
            url: "//cdn.datatables.net/plug-ins/1.13.4/i18n/id.json"
        }
    });

    // Loading overlay for AJAX operations
    $(document).ajaxStart(function() {
        $('#loadingOverlay').show();
    }).ajaxStop(function() {
        $('#loadingOverlay').hide();
    });

    // Form validation for CRUD operations
    $('.needs-validation').on('submit', function(e) {
        if (!this.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        $(this).addClass('was-validated');
    });

    // Initialize Bootstrap tooltips if needed
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

// Helper function to show toast notifications
function showToast(type, message) {
    if (typeof bootstrap === 'undefined' || !bootstrap.Toast) {
        console.log(`${type}: ${message}`);
        return;
    }
    
    const toast = $(`
        <div class="toast ${type}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-body">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `);
    
    $('#toastContainer').append(toast);
    const bsToast = new bootstrap.Toast(toast[0]);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// Helper function to handle API errors
function handleApiError(error) {
    console.error('API Error:', error);
    showToast('danger', 'Terjadi kesalahan saat memproses permintaan');
}

// Peta Interaktif Functions
let map;
let markers = [];
let clusterLayer;

function initMap() {
    // Initialize map centered on Aceh Utara
    map = L.map('map').setView([4.9726, 97.1416], 10);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Initialize cluster layer
    clusterLayer = L.layerGroup().addTo(map);

    // Setup event listeners
    setupMapControls();

    // Load initial data
    loadMapData();
}

function setupMapControls() {
    // Refresh button
    $('#refreshMap').on('click', loadMapData);

    // Cluster toggle button
    $('#clusterToggle').on('click', function() {
        const isActive = $(this).hasClass('bg-green-500');
        $(this).toggleClass('bg-green-500 bg-gray-500');
        $(this).text(isActive ? 'Single Mode' : 'Cluster Mode');
        updateMapDisplay();
    });

    // Filter changes
    $('#yearFilter, #gampongFilter').on('change', function() { // Changed #districtFilter to #gampongFilter
        loadMapData();
    });
}

function loadMapData() {
    const year = $('#yearFilter').val();
    const gampong = $('#gampongFilter').val(); // Changed district to gampong and #districtFilter to #gampongFilter

    showLoading(true);
    
    let url = '/api/peta_data'; // Changed endpoint to /api/peta_data
    if (year !== 'all' || gampong !== 'all') {
        url += `?tahun=${year}&gampong=${gampong}`; // Changed district to gampong, and year to tahun to match backend
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            displayClusterData(data);
            updateStatistics(data);
            showLoading(false);
        })
        .catch(error => {
            handleApiError(error);
            showLoading(false);
        });
}

function displayClusterData(apiData) { // Renamed clusterData to apiData to reflect it's an array
    // Clear existing markers
    clusterLayer.clearLayers();
    markers = [];

    // Define cluster colors and sizes
    const clusterStyles = {
        0: { color: '#ef4444', size: 15 }, // High risk (example)
        1: { color: '#f59e0b', size: 12 }, // Medium risk (example)
        2: { color: '#10b981', size: 10 }, // Low risk (example)
        // Add more styles if k can be > 3
    };

    try {
        if (!Array.isArray(apiData)) { // Check if it's an array
            throw new Error('Invalid API data format: Expected an array.');
        }

        apiData.forEach((gampongEntry, index) => {
            if (!gampongEntry || typeof gampongEntry !== 'object') {
                console.warn(`Invalid data for entry at index: ${index}`);
                return;
            }
            
            const lat = parseFloat(gampongEntry.latitude);
            const lon = parseFloat(gampongEntry.longitude);

            if (isNaN(lat) || isNaN(lon)) {
                console.warn(`Invalid coordinates for gampong: ${gampongEntry.nama_gampong || `Entry ${index}`}. Lat: ${gampongEntry.latitude}, Lon: ${gampongEntry.longitude}`);
                return;
            }

            const clusterId = gampongEntry.cluster !== undefined ? parseInt(gampongEntry.cluster) : 0;
            const style = clusterStyles[clusterId] || clusterStyles[0]; // Fallback to default style
            
            const marker = L.circleMarker(
                [lat, lon],
                {
                    radius: style.size,
                    fillColor: style.color,
                    color: '#fff', // Border color of the circle
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                }
            );

            const popupContent = createPopupContent(gampongEntry);
            if (popupContent) {
                marker.bindPopup(popupContent);
                markers.push(marker);
            }
        });

    } catch (error) {
        console.error('Error processing map data:', error);
        showToast('danger', 'Gagal memproses data peta: ' + error.message);
    }

    updateMapDisplay();
}

function updateMapDisplay() {
    clusterLayer.clearLayers();
    
    const isClusterMode = $('#clusterToggle').hasClass('bg-green-500'); // Assuming green means cluster mode is ON
    
    if (isClusterMode && markers.length > 0) {
        const markerClusterGroup = L.markerClusterGroup(); // Re-initialize markerClusterGroup
        markers.forEach(marker => markerClusterGroup.addLayer(marker));
        clusterLayer.addLayer(markerClusterGroup);
    } else {
        markers.forEach(marker => clusterLayer.addLayer(marker));
    }
}

function createPopupContent(gampongData) {
    // Directly use properties from gampongData
    const totalAccidents = gampongData.jumlah_kecelakaan || 0;
    const totalVictims = (gampongData.jumlah_meninggal || 0) +
                         (gampongData.jumlah_luka_berat || 0) +
                         (gampongData.jumlah_luka_ringan || 0);
    
    return `
        <div class="popup-content" style="min-width: 200px;">
            <h4 class="font-bold text-lg mb-2">${gampongData.nama_gampong || 'N/A'}</h4>
            <div class="grid grid-cols-1 gap-1 text-sm">
                <p><span class="font-medium">Tahun:</span> ${gampongData.tahun || 'N/A'}</p>
                <p><span class="font-medium">Klaster:</span> ${gampongData.cluster !== undefined ? gampongData.cluster : 'N/A'}</p>
                <p><span class="font-medium">Status:</span> ${gampongData.status_keparahan || 'N/A'}</p>
                <p><span class="font-medium">Total Kecelakaan:</span> ${totalAccidents}</p>
                <p><span class="font-medium">Total Korban:</span> ${totalVictims}</p>
                <p><span class="font-medium">Meninggal:</span> ${gampongData.jumlah_meninggal || 0}</p>
                <p><span class="font-medium">Luka Berat:</span> ${gampongData.jumlah_luka_berat || 0}</p>
                <p><span class="font-medium">Luka Ringan:</span> ${gampongData.jumlah_luka_ringan || 0}</p>
            </div>
            <div class="mt-2">
                <a href="/detail/${gampongData.nama_gampong}" class="text-blue-500 text-sm hover:underline">Lihat Detail Gampong</a>
            </div>
        </div>
    `;
}

function updateStatistics(apiDataArray) { // Parameter is now an array
    let totalAccidents = 0;
    let totalVictims = 0;
    let highRiskGampong = { name: '-', count: -1 }; // Initialize count to -1 to correctly find max

    if (!Array.isArray(apiDataArray)) {
        console.error("updateStatistics received non-array data:", apiDataArray);
        $('#totalAccidents').text('Error');
        $('#totalVictims').text('Error');
        $('#highRiskDistrict').text('Error'); // Keep ID as highRiskDistrict or change in HTML too
        return;
    }

    apiDataArray.forEach(gampongEntry => {
        const accidents = parseInt(gampongEntry.jumlah_kecelakaan) || 0;
        const victims = (parseInt(gampongEntry.jumlah_meninggal) || 0) +
                        (parseInt(gampongEntry.jumlah_luka_berat) || 0) +
                        (parseInt(gampongEntry.jumlah_luka_ringan) || 0);
        
        totalAccidents += accidents;
        totalVictims += victims;
        
        if (accidents > highRiskGampong.count) {
            highRiskGampong = { name: gampongEntry.nama_gampong, count: accidents };
        }
    });

    $('#totalAccidents').text(totalAccidents);
    $('#totalVictims').text(totalVictims);
    $('#highRiskDistrict').text(highRiskGampong.name === '-' && highRiskGampong.count === -1 ? '-' : highRiskGampong.name); // Handle no data case
}

function showLoading(show) {
    if (show) {
        $('#loadingOverlay').show();
    } else {
        $('#loadingOverlay').hide();
    }
}

// Initialize map when peta.html loads
if (document.getElementById('map')) {
    document.addEventListener('DOMContentLoaded', initMap);
}