// Public dashboard JavaScript for data visualization and interaction

document.addEventListener('DOMContentLoaded', function() {
    // Dummy data as fallback
    const dummyData = {
        accidentLocations: [
            { lat: 5.1714, lng: 97.1401, title: 'Lokasi 1', count: 45 },
            { lat: 5.1814, lng: 97.1501, title: 'Lokasi 2', count: 38 },
            { lat: 5.1914, lng: 97.1301, title: 'Lokasi 3', count: 32 },
            { lat: 5.1614, lng: 97.1601, title: 'Lokasi 4', count: 27 },
            { lat: 5.1514, lng: 97.1201, title: 'Lokasi 5', count: 23 }
        ]
    };

    // Create accident trends chart
    function createAccidentTrendsChart(yearData) {
        const years = yearData.map(item => item.year || item.tahun);
        const counts = yearData.map(item => item.total || item.count);
        
        Plotly.newPlot('accidentTrendsChart', [{
            x: years,
            y: counts,
            type: 'bar',
            marker: {
                color: 'rgb(59, 130, 246)'
            },
            hovertemplate: '<b>Tahun %{x}</b><br>Total Kecelakaan: %{y}<extra></extra>'
        }], {
            margin: { t: 10, l: 50, r: 20, b: 40 },
            xaxis: { title: 'Tahun' },
            yaxis: { title: 'Jumlah Kecelakaan' },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)'
        });
    }

    // Create victim statistics chart
    function createVictimStatsChart(victimData) {
        const years = victimData.map(item => item.year || item.tahun);
        const deathsData = victimData.map(item => item.deaths);
        const seriousData = victimData.map(item => item.serious);
        const minorData = victimData.map(item => item.minor);
        
        Plotly.newPlot('victimStatsChart', [
            {
                x: years,
                y: deathsData,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Meninggal',
                line: { color: 'rgb(239, 68, 68)', width: 3 },
                marker: { size: 8 }
            },
            {
                x: years,
                y: seriousData,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Luka Berat',
                line: { color: 'rgb(245, 158, 11)', width: 3 },
                marker: { size: 8 }
            },
            {
                x: years,
                y: minorData,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Luka Ringan',
                line: { color: 'rgb(16, 185, 129)', width: 3 },
                marker: { size: 8 }
            }
        ], {
            margin: { t: 10, l: 50, r: 20, b: 40 },
            xaxis: { title: 'Tahun' },
            yaxis: { title: 'Jumlah Korban' },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            legend: { orientation: 'h', y: 1.1 }
        });
    }

    // Create vehicle type chart
    function createVehicleTypeChart(vehicleData) {
        const labels = Object.keys(vehicleData);
        const values = Object.values(vehicleData);
        
        Plotly.newPlot('vehicleTypeChart', [{
            labels: labels,
            values: values,
            type: 'pie',
            hole: 0.4,
            marker: {
                colors: ['rgb(239, 68, 68)', 'rgb(59, 130, 246)', 'rgb(16, 185, 129)', 'rgb(245, 158, 11)', 'rgb(139, 92, 246)']
            },
            textinfo: 'label+percent',
            insidetextorientation: 'radial'
        }], {
            margin: { t: 10, b: 10, l: 10, r: 10 },
            showlegend: false
        });
    }

    // Create accident map
    function createAccidentMap(locations) {
        const map = L.map('accidentMap').setView([5.1794, 97.1328], 12);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);
        
        locations.forEach(location => {
            const markerSize = Math.min(20, Math.max(10, location.count / 5));
            
            L.circleMarker([location.lat, location.lng], {
                radius: markerSize,
                fillColor: '#e53e3e',
                color: 'white',
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
            }).bindPopup(`<strong>${location.title}</strong><br>Jumlah Kecelakaan: ${location.count}`).addTo(map);
        });
    }

    // Create high risk area table
    function createHighRiskAreaTable(areas) {
        const tableBody = document.getElementById('highRiskAreaTable');
        let tableHTML = '';
        
        areas.forEach(area => {
            // Calculate risk level based on accident count if not provided
            let risk = area.risk;
            if (!risk) {
                if (area.accidents > 150) risk = 'Tinggi';
                else if (area.accidents > 100) risk = 'Sedang';
                else risk = 'Rendah';
            }
            
            let riskClass = 'text-green-600 bg-green-100';
            
            if (risk === 'Tinggi') {
                riskClass = 'text-red-600 bg-red-100';
            } else if (risk === 'Sedang') {
                riskClass = 'text-yellow-600 bg-yellow-100';
            }
            
            tableHTML += `
                <tr class="hover:bg-gray-50">
                    <td class="py-2 px-4 border-b">${area.name || area.nama_gampong}</td>
                    <td class="py-2 px-4 border-b">${area.accidents}</td>
                    <td class="py-2 px-4 border-b">${area.deaths}</td>
                    <td class="py-2 px-4 border-b">
                        <span class="px-2 py-1 rounded-full text-xs font-medium ${riskClass}">
                            ${risk}
                        </span>
                    </td>
                </tr>
            `;
        });
        
        tableBody.innerHTML = tableHTML;
    }

    // Handle filter button click
    document.getElementById('applyFilter').addEventListener('click', function() {
        const year = document.getElementById('publicYearFilter').value;
        window.location.href = `/public?year=${year}`;
    });

    // Main initialization function
    function initDashboard() {
        // Get backend data from the rendered template
        let accidents_by_year, victims_by_year, vehicle_types, high_risk_areas;
        
        try {
            accidents_by_year = JSON.parse(document.getElementById('accidentData').textContent);
            victims_by_year = JSON.parse(document.getElementById('victimData').textContent);
            vehicle_types = JSON.parse(document.getElementById('vehicleData').textContent);
            high_risk_areas = JSON.parse(document.getElementById('areaData').textContent);
        } catch (error) {
            console.error('Error parsing dashboard data:', error);
            
            // Fallback data if parsing fails
            accidents_by_year = [
                {year: '2019', total: 287},
                {year: '2020', total: 245},
                {year: '2021', total: 312},
                {year: '2022', total: 403}
            ];
            
            victims_by_year = [
                {year: '2019', deaths: 42, serious: 98, minor: 187},
                {year: '2020', deaths: 38, serious: 87, minor: 162},
                {year: '2021', deaths: 46, serious: 104, minor: 219},
                {year: '2022', deaths: 57, serious: 137, minor: 324}
            ];
            
            vehicle_types = {
                'Sepeda Motor': 864,
                'Mobil Penumpang': 324,
                'Angkutan Umum': 87,
                'Truk': 64,
                'Lainnya': 41
            };
            
            high_risk_areas = [
                {name: 'Kecamatan A', accidents: 215, deaths: 32, serious: 78, minor: 132, risk: 'Tinggi'},
                {name: 'Kecamatan B', accidents: 187, deaths: 28, serious: 64, minor: 114, risk: 'Tinggi'},
                {name: 'Kecamatan C', accidents: 156, deaths: 23, serious: 52, minor: 98, risk: 'Sedang'},
                {name: 'Kecamatan D', accidents: 143, deaths: 21, serious: 48, minor: 89, risk: 'Sedang'},
                {name: 'Kecamatan E', accidents: 124, deaths: 18, serious: 41, minor: 77, risk: 'Sedang'}
            ];
        }
        
        // Initialize all visualizations
        createAccidentTrendsChart(accidents_by_year);
        createVictimStatsChart(victims_by_year);
        createVehicleTypeChart(vehicle_types);
        createAccidentMap(dummyData.accidentLocations); // No real location data yet
        createHighRiskAreaTable(high_risk_areas);
    }

    // Initialize the dashboard
    initDashboard();
});
