// JavaScript for K-Medoids Simulation
document.addEventListener('DOMContentLoaded', function() {
    // Tab navigation
    function setupTabNavigation() {
        const tabButtons = document.querySelectorAll('#tabButtons button');
        
        // Debug all button IDs and content IDs
        console.log('Tab Button IDs:');
        tabButtons.forEach(btn => console.log(btn.id));
        
        // Debug all content divs
        console.log('Content Elements:');
        ['dataContent', 'iterationsContent', 'chartsContent', 'mapContent'].forEach(id => {
            const el = document.getElementById(id);
            console.log(`${id}: ${el ? 'Found' : 'Not Found'}`);
        });
        
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                console.log('Tab clicked:', this.id);
                
                // Reset all tab buttons
                tabButtons.forEach(btn => {
                    btn.classList.remove('bg-blue-500', 'text-white');
                    btn.classList.add('bg-gray-200', 'text-gray-700');
                });
                
                // Hide all tab contents
                document.querySelectorAll('#dataContent, #iterationsContent, #chartsContent, #mapContent').forEach(content => {
                    content.classList.add('hidden');
                });
                
                // Activate selected tab button
                this.classList.remove('bg-gray-200', 'text-gray-700');
                this.classList.add('bg-blue-500', 'text-white');
                
                // Show selected content
                let contentId = this.id.replace('tab', '') + 'Content';
                console.log('Looking for content with ID:', contentId);

                // Convert first letter to lowercase for content IDs
                contentId = contentId.charAt(0).toLowerCase() + contentId.slice(1);
                console.log('Converted to lowercase first letter:', contentId);

                const contentElement = document.getElementById(contentId);
                
                if (contentElement) {
                    contentElement.classList.remove('hidden');
                    
                    // Force map resize if map tab is selected
                    if (contentId === 'mapContent' && clusterMap) {
                        setTimeout(() => {
                            clusterMap.invalidateSize(true);
                            console.log('Map size invalidated');
                        }, 200);
                    }
                } else {
                    console.error('Tab content not found:', contentId);
                }
            });
        });
    }
    
    // Setup tabs initially
    setupTabNavigation();

    // Form submission
    const kmedoidsForm = document.getElementById('kmedoidsForm');
    kmedoidsForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate form
        const numClusters = parseInt(document.getElementById('numClusters').value);
        const maxIterations = parseInt(document.getElementById('maxIterations').value);
        const yearFilter = document.getElementById('yearFilter').value;
        
        // Get selected features
        const selectedFeatures = [];
        document.querySelectorAll('input[name="features"]:checked').forEach(checkbox => {
            selectedFeatures.push(checkbox.value);
        });
        
        if (selectedFeatures.length < 2) {
            alert('Pilih minimal 2 fitur untuk clustering');
            return;
        }
        
        // Show loading section
        document.getElementById('loadingSection').classList.remove('hidden');
        document.getElementById('resultSection').classList.add('hidden');
        document.getElementById('loadingText').textContent = 'Memproses Data...';
        document.getElementById('progressText').textContent = 'Mengambil data dari database';
        
        // Run simulation
        runKMedoidsSimulation(numClusters, maxIterations, yearFilter, selectedFeatures);
    });

    // Iteration slider event
    const iterationSlider = document.getElementById('iterationSlider');
    iterationSlider.addEventListener('input', function() {
        const iteration = parseInt(this.value);
        document.getElementById('currentIteration').textContent = iteration;
        updateIterationDetails(iteration);
    });
});

// Global variables to store simulation results
let simulationData = null;
let simulationResults = null;
let clusterMap = null;

// Function to display iteration details
function displayIterationDetails(results) {
    const summaryDataPoints = document.getElementById('summaryDataPoints');
    const summaryNumClusters = document.getElementById('summaryNumClusters');
    const summaryTotalIterations = document.getElementById('summaryTotalIterations');
    const summaryTotalTime = document.getElementById('summaryTotalTime');
    const iterationSlider = document.getElementById('iterationSlider');
    const currentIteration = document.getElementById('currentIteration');
    const logContainer = document.getElementById('algorithmLog');
    
    if (!summaryDataPoints || !summaryNumClusters || !summaryTotalIterations || 
        !summaryTotalTime || !iterationSlider || !currentIteration || !logContainer) {
        console.error('One or more required elements for iteration details not found');
        return;
    }
    
    // Update summary
    summaryDataPoints.textContent = results.num_data_points;
    summaryNumClusters.textContent = results.k;
    summaryTotalIterations.textContent = results.iterations.length;
    summaryTotalTime.textContent = `${results.execution_time.toFixed(3)} detik`;
    
    // Set up iteration slider
    iterationSlider.min = 0;
    iterationSlider.max = results.iterations.length - 1;
    iterationSlider.value = 0;
    currentIteration.textContent = 0;
    
    // Initialize with first iteration
    updateIterationDetails(0);
    
    // Fill algorithm log
    logContainer.innerHTML = '';
    
    results.logs.forEach(log => {
        const logEntry = document.createElement('div');
        logEntry.className = 'mb-1';
        
        if (log.includes('Iteration')) {
            logEntry.className += ' text-green-400 font-bold';
        } else if (log.includes('Error') || log.includes('Failed')) {
            logEntry.className += ' text-red-400';
        } else if (log.includes('Selected')) {
            logEntry.className += ' text-yellow-400';
        }
        
        logEntry.textContent = log;
        logContainer.appendChild(logEntry);
    });
}

// Function to create cluster map
function createClusterMap(inputData, results) {
    // Initialize map
    const mapElement = document.getElementById('clusterMap');
    if (!mapElement) {
        console.error('Element with id "clusterMap" not found');
        return;
    }
    
    if (!inputData || inputData.length === 0) {
        mapElement.innerHTML = 
            '<div class="flex items-center justify-center h-full bg-gray-100 text-gray-500">Tidak ada data untuk ditampilkan</div>';
        return;
    }
    
    // Clear existing map if it exists
    if (clusterMap) {
        clusterMap.remove();
        clusterMap = null;
        console.log('Previous map instance cleared');
    }
    
    // Clear the map container HTML to ensure clean state
    mapElement.innerHTML = '';
    
    // Find data point with valid coordinates for center
    let centerPoint = inputData.find(point => 
        point.latitude && point.longitude && 
        !isNaN(parseFloat(point.latitude)) && 
        !isNaN(parseFloat(point.longitude))
    );
    
    // Default to Lhokseumawe if no valid points
    const center = centerPoint 
        ? [parseFloat(centerPoint.latitude), parseFloat(centerPoint.longitude)] 
        : [5.1794, 97.1328]; // Lhokseumawe coordinates
    
    // Create new map instance
    if (document.getElementById('clusterMap')) {
        clusterMap = L.map('clusterMap').setView(center, 9);
        
        // Add tile layers with more options
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19,
            minZoom: 5
        }).addTo(clusterMap);
        
        // Add scale control
        L.control.scale({
            imperial: false,
            position: 'bottomright'
        }).addTo(clusterMap);
    } else {
        console.error('Element with id "clusterMap" not found');
        return;
    }
    
    // Create marker cluster group with custom options
    const markers = L.markerClusterGroup({
        disableClusteringAtZoom: 15,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        zoomToBoundsOnClick: true,
        maxClusterRadius: 40
    });
    
    // Define colors for clusters with improved color scheme
    const colors = ['#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', 
                   '#ec4899', '#06b6d4', '#84cc16', '#a855f7', '#14b8a6'];
    
    // Add markers for each data point
    const finalCluster = inputData.map((data, index) => {
        // Find cluster assignment in final iteration
        const finalIteration = results.iterations[results.iterations.length - 1];
        let cluster = 0;
        
        for (let i = 0; i < finalIteration.clusters.length; i++) {
            if (finalIteration.clusters[i].includes(index)) {
                cluster = i;
                break;
            }
        }
        
        return {
            ...data,
            cluster: cluster
        };
    });
      // Add points to map
    finalCluster.forEach(point => {
        if (!point.latitude || !point.longitude || 
            isNaN(parseFloat(point.latitude)) || 
            isNaN(parseFloat(point.longitude))) {
            return;
        }
        
        const lat = parseFloat(point.latitude);
        const lng = parseFloat(point.longitude);
        const cluster = point.cluster;
        const color = colors[cluster % colors.length];
        
        // Create improved popup content with better styling
        const popupContent = `
            <div style="width: 270px;">
                <div style="background-color: ${color}; color: white; padding: 8px; border-radius: 4px 4px 0 0; margin-bottom: 8px;">
                    <h4 style="margin: 0; font-weight: bold; font-size: 15px;">
                        ${point.nama_gampong}
                    </h4>
                    <div style="font-size: 12px; margin-top: 3px;">Tahun: ${point.tahun}</div>
                </div>
                <div style="padding: 0 8px 8px;">
                    <p style="margin: 0 0 8px; background-color: #f3f4f6; padding: 5px; border-radius: 4px; font-weight: 500;">
                        Klaster ${cluster + 1}
                    </p>
                    <div style="margin-top: 5px;">
                        <div style="font-weight: bold; margin-bottom: 4px; color: #374151; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px;">Data:</div>
                        <div style="max-height: 200px; overflow-y: auto;">
                            <table style="width: 100%; font-size: 12px; border-collapse: collapse;">
                                ${Object.entries(point)
                                    .filter(([key, _]) => !['nama_gampong', 'tahun', 'latitude', 'longitude', 'cluster', 'gampong_id'].includes(key))
                                    .map(([key, value]) => `
                                        <tr>
                                            <td style="padding: 4px 0; border-bottom: 1px solid #f3f4f6; font-weight: 500;">${formatFeatureName(key)}</td>
                                            <td style="padding: 4px 0; border-bottom: 1px solid #f3f4f6; text-align: right;">${value}</td>
                                        </tr>
                                    `)
                                    .join('')
                                }
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Use pulsing marker for medoids and circle markers for regular points
        const finalIteration = results.iterations[results.iterations.length - 1];
        const isMedoid = finalIteration.medoids.some(m => m.original_index === finalCluster.indexOf(point));
        
        let marker;
        
        if (isMedoid) {
            // Create custom pulsing marker for medoids
            const pulseMarker = L.divIcon({
                html: `<div class="pulse-marker" style="background-color: ${color};"></div>`,
                className: '',
                iconSize: [16, 16],
                iconAnchor: [8, 8]
            });
              marker = L.marker([lat, lng], {
                icon: pulseMarker,
                title: `${point.nama_gampong} (Medoid Klaster ${cluster + 1})`
            }).bindPopup(popupContent, {
                className: 'custom-popup',
                maxWidth: 300
            });
        } else {            // Create marker with popup
            marker = L.circleMarker([lat, lng], {
                radius: 7,
                fillColor: color,
                color: 'white',
                weight: 1.5,
                opacity: 1,
                fillOpacity: 0.8
            }).bindPopup(popupContent, {
                className: 'custom-popup',
                maxWidth: 300
            });
        }
        
        markers.addLayer(marker);
    });
      clusterMap.addLayer(markers);
    
    // Add legend with year filter information
    const legendDiv = document.getElementById('mapLegend');
    if (!legendDiv) {
        console.error('Element with id "mapLegend" not found');
        return;
    }
    
    legendDiv.innerHTML = '';
      // Show year filter information at the top of the legend
    const yearFilter = results.year_filter || 'Semua Tahun';
    const yearInfoDiv = document.createElement('div');
    yearInfoDiv.className = 'mb-4 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-md text-center shadow-sm';
    
    // Create pulsing indicator for year filter
    let yearFilterHTML = '';
    if (yearFilter !== 'Semua Tahun') {
        yearFilterHTML = `
            <div class="year-filter-badge">${yearFilter}</div>
        `;
    } else {
        yearFilterHTML = `
            <span class="font-semibold text-gray-700">Semua Tahun</span>
        `;
    }
    
    yearInfoDiv.innerHTML = `
        <div class="text-sm text-gray-500 mb-1">Filter Tahun</div>
        <div>${yearFilterHTML}</div>
    `;
    legendDiv.appendChild(yearInfoDiv);
    
    // Display the count of points in each cluster
    const totalPointsDiv = document.createElement('div');
    totalPointsDiv.className = 'mb-3 p-2 bg-gray-50 border border-gray-200 rounded-md';
    totalPointsDiv.innerHTML = `<span class="font-semibold">Total Data:</span> ${inputData.length} titik`;
    legendDiv.appendChild(totalPointsDiv);
    
    // Add cluster colors to legend
    const legendTitle = document.createElement('div');
    legendTitle.className = 'font-semibold mb-2';
    legendTitle.textContent = 'Klaster:';
    legendDiv.appendChild(legendTitle);
    
    // Create legend items container
    const legendItemsContainer = document.createElement('div');
    legendItemsContainer.className = 'space-y-2 ml-1';
    legendDiv.appendChild(legendItemsContainer);
    
    for (let i = 0; i < results.k; i++) {
        const color = colors[i % colors.length];
        const clusterPoints = finalCluster.filter(p => p.cluster === i);
        
        const legendItem = document.createElement('div');
        legendItem.className = 'flex items-center justify-between';
        legendItem.innerHTML = `
            <div class="flex items-center">
                <div class="w-4 h-4 rounded-full mr-2" style="background-color: ${color};"></div>
                <span class="text-sm">Klaster ${i + 1}</span>
            </div>
            <span class="text-xs bg-gray-100 px-2 py-1 rounded-full">${clusterPoints.length} data</span>
        `;
        legendItemsContainer.appendChild(legendItem);
    }
    
    // Add marker type explanation
    const markerTypesDiv = document.createElement('div');
    markerTypesDiv.className = 'mt-4 pt-3 border-t border-gray-200';
    markerTypesDiv.innerHTML = `
        <div class="font-semibold mb-2">Jenis Marker:</div>
        <div class="flex items-center mb-2">
            <div class="w-4 h-4 rounded-full mr-2 pulse-marker" style="background-color: #3b82f6; animation: none;"></div>
            <span class="text-sm">Medoid (pusat klaster)</span>
        </div>
        <div class="flex items-center">
            <div class="w-4 h-4 rounded-full mr-2" style="background-color: #3b82f6;"></div>
            <span class="text-sm">Anggota klaster</span>
        </div>
    `;
    legendDiv.appendChild(markerTypesDiv);
    
    // Add cluster summary with enhanced styling
    const summaryDiv = document.getElementById('clusterSummary');
    if (!summaryDiv) {
        console.error('Element with id "clusterSummary" not found');
        return;
    }
    summaryDiv.innerHTML = '';
    
    for (let i = 0; i < results.k; i++) {
        const clusterPoints = finalCluster.filter(p => p.cluster === i);
        const color = colors[i % colors.length];
        
        const summaryItem = document.createElement('div');
        summaryItem.className = 'p-3 border border-gray-200 rounded-lg bg-white shadow-sm mb-3';
        
        let summaryContent = `
            <div class="flex items-center mb-2">
                <div class="w-3 h-3 rounded-full mr-2" style="background-color: ${color};"></div>
                <div class="font-semibold">Klaster ${i + 1}</div>
                <div class="text-xs bg-gray-100 px-2 py-1 rounded-full ml-auto">${clusterPoints.length} data</div>
            </div>
        `;
        
        // Add medoid information with enhanced styling
        const finalIteration = results.iterations[results.iterations.length - 1];
        const medoid = finalIteration.medoids.find(m => m.cluster === i);
        
        if (medoid) {
            const medoidData = inputData[medoid.original_index];
            
            if (medoidData) {
                // Filter by year if year filter is active
                const yearFilter = results.year_filter || 'Semua Tahun';
                const yearFilterText = yearFilter !== 'Semua Tahun' ? ` (Tahun: ${yearFilter})` : '';
                
                summaryContent += `
                    <div class="bg-gray-50 p-2 rounded-md mb-2">
                        <div class="text-sm font-medium text-gray-700">Medoid${yearFilterText}:</div>
                        <div class="text-sm mt-1 flex items-center">
                            <div class="w-2 h-2 rounded-full mr-2 pulse-marker" style="background-color: ${color}; animation: none;"></div>
                            <strong>${medoidData.nama_gampong}</strong> - Tahun: ${medoidData.tahun}
                        </div>
                    </div>
                `;
            }
        }
        
        // Add top gampongs with year filter indicator
        if (clusterPoints.length > 0) {
            const gampongGroups = {};
            
            clusterPoints.forEach(point => {
                if (!gampongGroups[point.nama_gampong]) {
                    gampongGroups[point.nama_gampong] = {
                        count: 0,
                        years: new Set()
                    };
                }
                gampongGroups[point.nama_gampong].count++;
                gampongGroups[point.nama_gampong].years.add(point.tahun);
            });
            
            const sortedGampongs = Object.entries(gampongGroups)
                .sort((a, b) => b[1].count - a[1].count)
                .slice(0, 5);
            
            if (sortedGampongs.length > 0) {
                summaryContent += `
                    <div class="text-sm font-medium text-gray-700 mb-1">Gampong terbanyak:</div>
                    <div class="bg-gray-50 p-2 rounded-md text-sm">
                        <ul class="space-y-1">
                            ${sortedGampongs.map(([name, data]) => 
                                `<li class="flex items-center justify-between">
                                    <span>${name}</span>
                                    <span class="text-xs bg-gray-200 px-1.5 py-0.5 rounded-full">
                                        ${data.count} data (${Array.from(data.years).join(', ')})
                                    </span>
                                </li>`
                            ).join('')}
                        </ul>
                    </div>
                `;
            }
        }
        
        summaryItem.innerHTML = summaryContent;
        summaryDiv.appendChild(summaryItem);
    }
    
    // Force map to recalculate size
    setTimeout(() => {
        if (clusterMap) {
            clusterMap.invalidateSize(true);
            console.log('Map size invalidated');
        }
    }, 200);
}

// Helper function to format feature names
function formatFeatureName(name) {
    return name
        .replace(/_/g, ' ')
        .replace(/\b\w/g, c => c.toUpperCase());
}

// Function to run K-Medoids simulation
function runKMedoidsSimulation(numClusters, maxIterations, yearFilter, selectedFeatures) {
    // Make API call to run simulation
    fetch('/api/kmedoids_simulation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            k: numClusters,
            max_iter: maxIterations,
            year: yearFilter,
            features: selectedFeatures
        }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })    .then(data => {
        // Store the results
        simulationData = data;
        simulationResults = data.results;
        
        // Store the year filter
        simulationData.year_filter = yearFilter;
        
        // Update progress
        document.getElementById('loadingText').textContent = 'Rendering Visualisasi...';
        document.getElementById('progressText').textContent = 'Membuat chart dan peta';
        
        // Update UI with results
        setTimeout(() => {
            document.getElementById('loadingSection').classList.add('hidden');
            document.getElementById('resultSection').classList.remove('hidden');
            
            // Make sure all content divs are initialized correctly
            // First, make all content divs hidden except the first one
            document.querySelectorAll('#iterationsContent, #chartsContent, #mapContent').forEach(content => {
                if (content) content.classList.add('hidden');
            });
            const dataContent = document.getElementById('dataContent');
            if (dataContent) dataContent.classList.remove('hidden');
            
            // Reset all tab buttons
            document.querySelectorAll('#tabButtons button').forEach(btn => {
                btn.classList.remove('bg-blue-500', 'text-white');
                btn.classList.add('bg-gray-200', 'text-gray-700');
            });
            
            // Make the first tab active
            const firstTab = document.getElementById('tabData');
            if (firstTab) {
                firstTab.classList.remove('bg-gray-200', 'text-gray-700');
                firstTab.classList.add('bg-blue-500', 'text-white');
            }
            
            // Display the results
            displayInputData(data.input_data, selectedFeatures);
            displayIterationDetails(data.results);
            createVisualizationCharts(data.results, data.input_data);
            createClusterMap(data.input_data, data.results);
        }, 500);
    })
    .catch(error => {
        console.error('Error running simulation:', error);
        document.getElementById('loadingSection').classList.add('hidden');
        alert('Terjadi kesalahan dalam menjalankan simulasi. Silakan coba lagi.');
    });
}

// Function to display input data
function displayInputData(inputData, selectedFeatures) {
    const table = document.getElementById('inputDataTable');
    if (!table) {
        console.error('Element with id "inputDataTable" not found');
        return;
    }
    
    const tableHead = table.querySelector('thead tr');
    const tableBody = table.querySelector('tbody');
    
    if (!tableHead || !tableBody) {
        console.error('Table structure is incomplete');
        return;
    }
    
    // Clear existing headers and rows
    while (tableHead.children.length > 2) {
        tableHead.removeChild(tableHead.lastChild);
    }
    tableBody.innerHTML = '';
    
    // Add feature headers
    selectedFeatures.forEach(feature => {
        const th = document.createElement('th');
        th.className = 'py-2 px-3 bg-gray-100 border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider';
        th.textContent = formatFeatureName(feature);
        tableHead.appendChild(th);
    });
    
    // Add data rows
    inputData.forEach(item => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';
        
        // Add gampong and year
        const tdGampong = document.createElement('td');
        tdGampong.className = 'py-2 px-3 border-b border-gray-200 text-sm';
        tdGampong.textContent = item.nama_gampong;
        row.appendChild(tdGampong);
        
        const tdYear = document.createElement('td');
        tdYear.className = 'py-2 px-3 border-b border-gray-200 text-sm';
        tdYear.textContent = item.tahun;
        row.appendChild(tdYear);
        
        // Add feature values
        selectedFeatures.forEach(feature => {
            const td = document.createElement('td');
            td.className = 'py-2 px-3 border-b border-gray-200 text-sm text-right';
            td.textContent = item[feature] !== undefined ? item[feature] : '-';
            row.appendChild(td);
        });
        
        tableBody.appendChild(row);
    });
    
    // Display data statistics
    displayDataStatistics(inputData, selectedFeatures);
}

// Function to display data statistics
function displayDataStatistics(inputData, selectedFeatures) {
    const statsContainer = document.getElementById('dataStats');
    if (!statsContainer) {
        console.error('Element with id "dataStats" not found');
        return;
    }
    
    statsContainer.innerHTML = '';
    
    // Create stats card for each feature
    selectedFeatures.forEach(feature => {
        // Calculate statistics
        const values = inputData.map(item => parseFloat(item[feature])).filter(val => !isNaN(val));
        if (values.length === 0) return;
        
        const min = Math.min(...values);
        const max = Math.max(...values);
        const sum = values.reduce((a, b) => a + b, 0);
        const avg = sum / values.length;
        
        // Sort values for median and quartiles
        values.sort((a, b) => a - b);
        const median = values.length % 2 === 0 
            ? (values[values.length / 2 - 1] + values[values.length / 2]) / 2
            : values[Math.floor(values.length / 2)];
        
        // Create card
        const card = document.createElement('div');
        card.className = 'bg-white p-3 rounded-md shadow-sm';
        
        card.innerHTML = `
            <div class="text-md font-semibold text-gray-700 mb-2">${formatFeatureName(feature)}</div>
            <div class="grid grid-cols-2 gap-2 text-sm">
                <div>
                    <div class="text-xs text-gray-500">Min</div>
                    <div class="font-bold">${min.toFixed(2)}</div>
                </div>
                <div>
                    <div class="text-xs text-gray-500">Max</div>
                    <div class="font-bold">${max.toFixed(2)}</div>
                </div>
                <div>
                    <div class="text-xs text-gray-500">Rata-rata</div>
                    <div class="font-bold">${avg.toFixed(2)}</div>
                </div>
                <div>
                    <div class="text-xs text-gray-500">Median</div>
                    <div class="font-bold">${median.toFixed(2)}</div>
                </div>
            </div>
        `;
        
        statsContainer.appendChild(card);
    });
}

// Function to create visualization charts
function createVisualizationCharts(results, inputData) {
    // Cost per iteration chart
    const costChart = document.getElementById('costChart');
    if (!costChart) {
        console.error('Element with id "costChart" not found');
        return;
    }

    const costValues = results.iterations.map(iter => iter.total_cost);
    const costTrace = {
        x: Array.from({length: costValues.length}, (_, i) => i),
        y: costValues,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Total Cost',
        line: {
            color: 'rgb(59, 130, 246)',
            width: 2
        },
        marker: {
            size: 6,
            color: 'rgb(37, 99, 235)'
        }
    };    
    Plotly.newPlot('costChart', [costTrace], {
        margin: {t: 10, l: 50, r: 20, b: 40},
        xaxis: {title: 'Iterasi'},
        yaxis: {title: 'Total Cost'},
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
    });
    
    // Cluster sizes chart
    const clusterSizesChart = document.getElementById('clusterSizesChart');
    if (!clusterSizesChart) {
        console.error('Element with id "clusterSizesChart" not found');
        return;
    }

    const clusterSizesData = [];
    const colors = ['rgb(239, 68, 68)', 'rgb(59, 130, 246)', 'rgb(16, 185, 129)', 'rgb(245, 158, 11)', 'rgb(139, 92, 246)'];
    
    for (let i = 0; i < results.k; i++) {
        const sizes = results.iterations.map(iter => {
            const cluster = iter.clusters[i] || [];
            return cluster.length;
        });
        
        clusterSizesData.push({
            x: Array.from({length: sizes.length}, (_, i) => i),
            y: sizes,
            type: 'scatter',
            mode: 'lines+markers',
            name: `Klaster ${i+1}`,
            line: {
                color: colors[i % colors.length],
                width: 2
            },
            marker: {
                size: 6,
                color: colors[i % colors.length]
            }
        });
    }
    
    Plotly.newPlot('clusterSizesChart', clusterSizesData, {
        margin: {t: 10, l: 50, r: 20, b: 40},
        xaxis: {title: 'Iterasi'},
        yaxis: {title: 'Jumlah Anggota'},
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
    });
    
    // t-SNE visualization (placeholder - will be populated by backend)
    const tsneVisualization = document.getElementById('tsneVisualization');
    if (!tsneVisualization) {
        console.error('Element with id "tsneVisualization" not found');
        return;
    }

    if (results.tsne && results.tsne.length > 0) {
        const tsneTraces = [];
        
        for (let i = 0; i < results.k; i++) {
            const clusterPoints = results.tsne.filter(p => p.cluster === i);
            
            if (clusterPoints.length > 0) {
                tsneTraces.push({
                    x: clusterPoints.map(p => p.x),
                    y: clusterPoints.map(p => p.y),
                    mode: 'markers',
                    type: 'scatter',
                    name: `Klaster ${i+1}`,
                    marker: {
                        size: 10,
                        color: colors[i % colors.length],
                        opacity: 0.7
                    },
                    text: clusterPoints.map(p => p.label || `Point ${p.index}`),
                    hoverinfo: 'text'
                });
            }
        }
        
        // Add medoids as stars
        const finalIteration = results.iterations[results.iterations.length - 1];
        const medoidTrace = {
            x: finalIteration.medoids.map(m => {
                const point = results.tsne.find(p => p.index === m.original_index);
                return point ? point.x : 0;
            }),
            y: finalIteration.medoids.map(m => {
                const point = results.tsne.find(p => p.index === m.original_index);
                return point ? point.y : 0;
            }),
            mode: 'markers',
            type: 'scatter',
            name: 'Medoids',
            marker: {
                symbol: 'star',
                size: 15,
                color: 'rgba(0, 0, 0, 0.8)',
                line: {
                    color: 'white',
                    width: 1
                }
            },
            text: finalIteration.medoids.map(m => `Medoid ${m.cluster}`),
            hoverinfo: 'text'
        };
        
        tsneTraces.push(medoidTrace);
        
        Plotly.newPlot('tsneVisualization', tsneTraces, {
            margin: {t: 10, l: 50, r: 20, b: 40},
            xaxis: {title: 't-SNE Dimension 1'},
            yaxis: {title: 't-SNE Dimension 2'},
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            showlegend: true
        });
    } else {
        document.getElementById('tsneVisualization').innerHTML = 
            '<div class="flex items-center justify-center h-full text-gray-500">Visualisasi t-SNE tidak tersedia</div>';
    }
    
    // Feature distribution by cluster
    const featureDistributionChart = document.getElementById('featureDistributionChart');
    if (!featureDistributionChart) {
        console.error('Element with id "featureDistributionChart" not found');
        return;
    }

    if (results.feature_importance && results.feature_importance.length > 0) {
        const featureNames = results.feature_importance[0].features.map(f => formatFeatureName(f.name));
        const featureTraces = [];
        
        for (let i = 0; i < results.k; i++) {
            const clusterFeatures = results.feature_importance.find(fi => fi.cluster === i);
            
            if (clusterFeatures) {
                featureTraces.push({
                    x: featureNames,
                    y: clusterFeatures.features.map(f => f.value),
                    type: 'bar',
                    name: `Klaster ${i+1}`,
                    marker: {
                        color: colors[i % colors.length]
                    }
                });
            }
        }
        
        Plotly.newPlot('featureDistributionChart', featureTraces, {
            margin: {t: 10, l: 50, r: 20, b: 80},
            xaxis: {
                title: 'Fitur',
                tickangle: -45
            },
            yaxis: {title: 'Nilai Rata-rata'},
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            barmode: 'group'
        });    } else {
        document.getElementById('featureDistributionChart').innerHTML = 
            '<div class="flex items-center justify-center h-full text-gray-500">Distribusi fitur tidak tersedia</div>';
    }
      // Create cluster similarity matrix (confusion matrix analog)
    try {
        createClusterSimilarityMatrix(results, inputData);
    } catch (error) {
        console.error('Error in createClusterSimilarityMatrix:', error);
        const matrixContainer = document.getElementById('clusterMatrixContainer');
        if (matrixContainer) {
            matrixContainer.parentElement.style.display = 'none';
        }
    }
}

// Function to create cluster similarity matrix (confusion matrix analog for clustering)
function createClusterSimilarityMatrix(results, inputData) {
    // Find target container
    const matrixContainer = document.getElementById('clusterMatrixContainer');
    if (!matrixContainer) {
        console.error('Element with id "clusterMatrixContainer" not found');
        return;
    }

    try {
        const finalIteration = results.iterations[results.iterations.length - 1];
        const k = results.k;
        
        // Create matrix data structure (k x k)
        const matrix = [];
        const clusterSizes = Array(k).fill(0);
        
        // Calculate cluster sizes
        finalIteration.clusters.forEach((cluster, idx) => {
            clusterSizes[idx] = cluster.length;
        });
        
        // Calculate similarity between each pair of clusters based on feature values
        for (let i = 0; i < k; i++) {
            matrix[i] = [];
            for (let j = 0; j < k; j++) {
                if (i === j) {
                    // Diagonal shows cluster size
                    matrix[i][j] = clusterSizes[i];
                } else {
                    // Calculate similarity score between clusters
                    const clusterI = finalIteration.clusters[i];
                    const clusterJ = finalIteration.clusters[j];
                    
                    // Calculate average distance between points in clusters
                    let totalSimilarity = 0;
                    let count = 0;
                    
                    if (clusterI.length > 0 && clusterJ.length > 0) {
                        // Sample up to 100 point pairs to keep calculation reasonable
                        const maxPairs = Math.min(100, clusterI.length * clusterJ.length);
                        const samplingRate = maxPairs / (clusterI.length * clusterJ.length);
                        
                        for (const pointIdxI of clusterI) {
                            for (const pointIdxJ of clusterJ) {
                                // Sample points to reduce computation
                                if (Math.random() > samplingRate) continue;
                                
                                const pointI = inputData[pointIdxI];
                                const pointJ = inputData[pointIdxJ];
                                
                                // Calculate similarity based on common features
                                let distance = 0;
                                let featCount = 0;
                                
                                for (const key in pointI) {
                                    if (
                                        key !== 'nama_gampong' && 
                                        key !== 'tahun' && 
                                        key !== 'latitude' && 
                                        key !== 'longitude' && 
                                        key !== 'gampong_id' &&
                                        !isNaN(parseFloat(pointI[key])) && 
                                        !isNaN(parseFloat(pointJ[key]))
                                    ) {
                                        distance += Math.pow(parseFloat(pointI[key]) - parseFloat(pointJ[key]), 2);
                                        featCount++;
                                    }
                                }
                                
                                if (featCount > 0) {
                                    // Convert distance to similarity (higher is more similar)
                                    const avgDistance = Math.sqrt(distance / featCount);
                                    const similarity = 1 / (1 + avgDistance);
                                    totalSimilarity += similarity;
                                    count++;
                                }
                            }
                        }
                    }
                    
                    const averageSimilarity = count > 0 ? totalSimilarity / count : 0;
                    // Scale similarity for better visualization (0-100)
                    matrix[i][j] = Math.round(averageSimilarity * 100);
                }
            }
        }
        
        // Create the heatmap using Plotly
        const heatmapData = [{
            z: matrix,
            x: Array.from({length: k}, (_, i) => `Klaster ${i+1}`),
            y: Array.from({length: k}, (_, i) => `Klaster ${i+1}`),
            type: 'heatmap',
            colorscale: 'Blues',
            showscale: true,
            hoverongaps: false,
            hovertemplate: 'Klaster %{y} ke Klaster %{x}: %{z}<extra></extra>',
            colorbar: {
                title: {
                    text: 'Diagonal: Jumlah data<br>Non-diagonal: Kesamaan (%)',
                    side: 'right'
                }
            }
        }];
        
        const layout = {
            title: 'Matriks Kesamaan Antar Klaster',
            xaxis: {
                title: 'Klaster',
                side: 'top'
            },
            yaxis: {
                title: 'Klaster'
            },
            annotations: []
        };
        
        // Add value annotations to the heatmap
        for (let i = 0; i < k; i++) {
            for (let j = 0; j < k; j++) {
                const value = matrix[i][j];
                let text = i === j ? value.toString() : value.toString() + '%';
                let fontColor = i === j ? 'white' : (value > 50 ? 'white' : 'black');
                
                layout.annotations.push({
                    x: j,
                    y: i,
                    text: text,
                    font: {
                        color: fontColor
                    },
                    showarrow: false
                });
            }
        }
        
        // Plot the heatmap
        Plotly.newPlot('clusterMatrixContainer', heatmapData, layout, {responsive: true});
        
        // Add explanation text below the matrix
        const explanationDiv = document.createElement('div');
        explanationDiv.className = 'mt-4 p-3 bg-gray-50 rounded-md text-sm text-gray-700 border border-gray-200';
        explanationDiv.innerHTML = `
            <p class="font-medium mb-2">Penjelasan Matriks Kesamaan:</p>
            <ul class="list-disc list-inside space-y-1">
                <li><strong>Diagonal (Klaster X ke Klaster X):</strong> Menunjukkan jumlah data dalam klaster tersebut.</li>
                <li><strong>Non-diagonal:</strong> Menunjukkan tingkat kesamaan antar klaster (0-100%). Nilai yang lebih tinggi menunjukkan klaster lebih mirip.</li>
                <li>Kesamaan dihitung berdasarkan jarak rata-rata antar data di kedua klaster.</li>
            </ul>
        `;
        matrixContainer.parentNode.insertBefore(explanationDiv, matrixContainer.nextSibling);
    } catch (error) {
        console.error('Error creating cluster similarity matrix:', error);
        matrixContainer.innerHTML = `
            <div class="flex items-center justify-center h-full bg-gray-100 text-gray-500">
                <div class="text-center p-4">
                    <svg class="w-12 h-12 mx-auto text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                    </svg>
                    <p>Tidak dapat membuat matriks kesamaan. Silakan coba lagi dengan data atau parameter yang berbeda.</p>
                </div>
            </div>
        `;
    }
}

// Function to update iteration details at a specific iteration
function updateIterationDetails(iteration) {
    if (!simulationResults) return;
    
    const iterData = simulationResults.iterations[iteration];
    if (!iterData) return;
    
    // Update iteration info
    const iterSummary = document.getElementById('iterationSummary');
    if (!iterSummary) return;
    
    // Display medoids table
    const medoidsTableBody = document.getElementById('medoidsTableBody');
    if (medoidsTableBody) {
        medoidsTableBody.innerHTML = '';
        
        iterData.medoids.forEach(medoid => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50';
            
            const medoidData = simulationData.input_data[medoid.original_index];
            const yearFilter = simulationData.year_filter || 'Semua Tahun';
            
            row.innerHTML = `
                <td class="py-2 px-3 border-b border-gray-200 text-sm">${medoid.cluster}</td>
                <td class="py-2 px-3 border-b border-gray-200 text-sm">${medoidData ? medoidData.nama_gampong : '-'}</td>
                <td class="py-2 px-3 border-b border-gray-200 text-sm">${medoidData ? medoidData.tahun : '-'}</td>
                <td class="py-2 px-3 border-b border-gray-200 text-sm text-right">${medoid.cost.toFixed(3)}</td>
            `;
            
            medoidsTableBody.appendChild(row);
        });
    }
    
    // Update cost info
    const iterCost = document.getElementById('iterationCost');
    if (iterCost) {
        iterCost.textContent = iterData.total_cost.toFixed(3);
    }
    
    // Update cluster info
    const clustersTableBody = document.getElementById('clustersTableBody');
    if (clustersTableBody) {
        clustersTableBody.innerHTML = '';
        
        for (let i = 0; i < iterData.clusters.length; i++) {
            const cluster = iterData.clusters[i];
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50';
            
            const medoid = iterData.medoids.find(m => m.cluster === i);
            const medoidData = medoid ? simulationData.input_data[medoid.original_index] : null;
            
            row.innerHTML = `
                <td class="py-2 px-3 border-b border-gray-200 text-sm">${i}</td>
                <td class="py-2 px-3 border-b border-gray-200 text-sm">${medoidData ? medoidData.nama_gampong : '-'}</td>
                <td class="py-2 px-3 border-b border-gray-200 text-sm text-right">${cluster.length}</td>
            `;
            
            clustersTableBody.appendChild(row);
        }
    }
}
