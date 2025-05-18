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
    
    // Calculate statistics for each feature
    selectedFeatures.forEach(feature => {
        const values = inputData.map(item => parseFloat(item[feature] || 0));
        const min = Math.min(...values);
        const max = Math.max(...values);
        const sum = values.reduce((a, b) => a + b, 0);
        const avg = sum / values.length;
        
        const statCard = document.createElement('div');
        statCard.className = 'bg-white p-3 rounded-md shadow-sm';
        statCard.innerHTML = `
            <div class="text-sm font-semibold text-gray-700">${formatFeatureName(feature)}</div>
            <div class="grid grid-cols-2 gap-2 mt-2 text-xs">
                <div>
                    <div class="text-gray-500">Min</div>
                    <div class="font-medium">${min.toFixed(2)}</div>
                </div>
                <div>
                    <div class="text-gray-500">Max</div>
                    <div class="font-medium">${max.toFixed(2)}</div>
                </div>
                <div>
                    <div class="text-gray-500">Rata-rata</div>
                    <div class="font-medium">${avg.toFixed(2)}</div>
                </div>
                <div>
                    <div class="text-gray-500">Total</div>
                    <div class="font-medium">${sum.toFixed(2)}</div>
                </div>
            </div>
        `;
        
        statsContainer.appendChild(statCard);
    });
}

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

// Function to update iteration details
function updateIterationDetails(iterationIndex) {
    if (!simulationResults || !simulationResults.iterations) return;
    
    const iteration = simulationResults.iterations[iterationIndex];
    
    // Update medoid selection
    const medoidSelection = document.getElementById('medoidSelection');
    if (!medoidSelection) return;

    medoidSelection.innerHTML = '';
    
    const medoidList = document.createElement('ul');
    medoidList.className = 'list-disc list-inside';
    
    iteration.medoids.forEach((medoid, idx) => {
        const listItem = document.createElement('li');
        listItem.className = 'mb-1';
        
        const medoidData = simulationData.input_data[medoid.original_index] || {};
        listItem.innerHTML = `<span class="font-semibold">Medoid ${idx + 1}:</span> ${medoidData.nama_gampong || '-'} (ID: ${medoid.original_index})`;
        
        medoidList.appendChild(listItem);
    });
    
    medoidSelection.appendChild(medoidList);
    
    // Update cluster assignment
    const clusterAssignment = document.getElementById('clusterAssignment');
    if (!clusterAssignment) return;
    
    clusterAssignment.innerHTML = '';
    
    const clusterSummary = document.createElement('div');
    
    iteration.clusters.forEach((cluster, clusterIdx) => {
        const clusterSection = document.createElement('div');
        clusterSection.className = 'mb-3';
        
        const clusterHeader = document.createElement('div');
        clusterHeader.className = 'font-semibold mb-1';
        clusterHeader.textContent = `Klaster ${clusterIdx + 1} (${cluster.length} anggota)`;
        
        clusterSection.appendChild(clusterHeader);
        
        if (cluster.length > 0) {
            const membersList = document.createElement('ul');
            membersList.className = 'text-xs list-disc list-inside pl-2';
            
            // Display up to 10 members with ellipsis if more
            const displayCount = Math.min(10, cluster.length);
            
            for (let i = 0; i < displayCount; i++) {
                const dataIdx = cluster[i];
                const dataItem = simulationData.input_data[dataIdx];
                
                const memberItem = document.createElement('li');
                memberItem.textContent = `${dataItem.nama_gampong} (${dataItem.tahun})`;
                membersList.appendChild(memberItem);
            }
            
            if (cluster.length > 10) {
                const moreItem = document.createElement('li');
                moreItem.className = 'italic';
                moreItem.textContent = `...dan ${cluster.length - 10} lainnya`;
                membersList.appendChild(moreItem);
            }
            
            clusterSection.appendChild(membersList);
        } else {
            const emptyNote = document.createElement('div');
            emptyNote.className = 'text-xs italic text-gray-500';
            emptyNote.textContent = 'Tidak ada anggota';
            clusterSection.appendChild(emptyNote);
        }
        
        clusterAssignment.appendChild(clusterSection);
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
    
    // Create map
    if (document.getElementById('clusterMap')) {
        clusterMap = L.map('clusterMap').setView(center, 9);
        
        // Add tile layers
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(clusterMap);
    } else {
        console.error('Element with id "clusterMap" not found');
        return;
    }
    
    // Create marker cluster group
    const markers = L.markerClusterGroup();
    
    // Define colors for clusters
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
          // Create popup content
        const popupContent = `
            <div style="width: 270px;">
                <div style="background-color: ${color}; color: white; padding: 8px; border-radius: 4px 4px 0 0; margin-bottom: 8px;">
                    <h4 style="margin: 0; font-weight: bold; font-size: 14px;">
                        ${point.nama_gampong}
                    </h4>
                    <div style="font-size: 12px; margin-top: 2px;">Tahun: ${point.tahun}</div>
                </div>
                <p style="margin: 0 0 8px; display: flex; align-items: center; justify-content: space-between;">
                    <span><strong>Klaster:</strong> ${cluster + 1}</span>
                    <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: ${color};"></span>
                </p>
                <div style="margin-top: 5px;">
                    <strong>Data:</strong>
                    <div style="max-height: 150px; overflow-y: auto; margin-top: 5px;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                            ${Object.entries(point)
                                .filter(([key, _]) => !['nama_gampong', 'tahun', 'latitude', 'longitude', 'cluster', 'gampong_id'].includes(key))
                                .map(([key, value]) => `
                                    <tr style="border-bottom: 1px solid #eee;">
                                        <td style="padding: 4px 0; font-weight: bold;">${formatFeatureName(key)}</td>
                                        <td style="padding: 4px 0; text-align: right;">${value}</td>
                                    </tr>
                                `).join('')
                            }
                        </table>
                    </div>
                </div>
            </div>
        `;
          // Create marker with popup
        const marker = L.circleMarker([lat, lng], {
            radius: 10,
            fillColor: color,
            color: 'white',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8,
            className: `cluster-marker cluster-${cluster + 1}` // Add classes for custom styling
        }).bindPopup(popupContent, {
            maxWidth: 300,
            className: 'custom-popup'
        });
        
        // Add a pulsing effect to the markers
        const pulseMarker = L.divIcon({
            html: `<div class="pulse-marker" style="background-color: ${color};"></div>`,
            className: '',
            iconSize: [12, 12]
        });
        
        L.marker([lat, lng], { icon: pulseMarker }).addTo(clusterMap);
        
        markers.addLayer(marker);
    });
    
    clusterMap.addLayer(markers);
      // Add legend
    const legendDiv = document.getElementById('mapLegend');
    if (!legendDiv) {
        console.error('Element with id "mapLegend" not found');
        return;
    }
    
    legendDiv.innerHTML = '';
    
    // Add year filter information at the top of legend
    const yearFilterValue = simulationData.year_filter || 'Semua Tahun';
    const yearInfoDiv = document.createElement('div');
    yearInfoDiv.className = 'mb-3 p-2 bg-blue-50 border border-blue-200 rounded-md text-center';
    yearInfoDiv.innerHTML = `<span class="font-semibold">Filter Tahun:</span> ${yearFilterValue}`;
    legendDiv.appendChild(yearInfoDiv);
    
    // Add cluster color legends
    for (let i = 0; i < results.k; i++) {
        const color = colors[i % colors.length];
        const legendItem = document.createElement('div');
        legendItem.className = 'flex items-center';
        legendItem.innerHTML = `
            <div class="w-4 h-4 rounded-full mr-2" style="background-color: ${color};"></div>
            <span class="text-sm">Klaster ${i + 1}</span>
        `;
        legendDiv.appendChild(legendItem);
    }
    
    // Add cluster summary
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
        summaryItem.className = 'p-2 border-l-4 rounded-l bg-gray-50';
        summaryItem.style.borderColor = color;
        
        let summaryContent = `<div class="font-semibold">Klaster ${i + 1} (${clusterPoints.length} titik)</div>`;
        
        // Add medoid information
        const finalIteration = results.iterations[results.iterations.length - 1];
        const medoid = finalIteration.medoids.find(m => m.cluster === i);
        
        if (medoid) {
            const medoidData = inputData[medoid.original_index];
            
            if (medoidData) {
                summaryContent += `
                    <div class="text-sm mt-1">
                        <strong>Medoid:</strong> ${medoidData.nama_gampong} (${medoidData.tahun})
                    </div>
                `;
            }
        }
        
        // Add top gampongs
        if (clusterPoints.length > 0) {
            const gampongGroups = {};
            
            clusterPoints.forEach(point => {
                if (!gampongGroups[point.nama_gampong]) {
                    gampongGroups[point.nama_gampong] = 0;
                }
                gampongGroups[point.nama_gampong]++;
            });
            
            const sortedGampongs = Object.entries(gampongGroups)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5);
            
            if (sortedGampongs.length > 0) {
                summaryContent += `
                    <div class="text-sm mt-1">
                        <strong>Gampong terbanyak:</strong>
                        <ul class="list-disc list-inside mt-1 text-xs">
                            ${sortedGampongs.map(([name, count]) => 
                                `<li>${name} (${count} titik)</li>`
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

// Function to create visualization charts
function createVisualizationCharts(results) {
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
        });
    } else {
        document.getElementById('featureDistributionChart').innerHTML = 
            '<div class="flex items-center justify-center h-full text-gray-500">Distribusi fitur tidak tersedia</div>';
    }
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
        simulationData.year_filter = yearFilter; // Store the year filter
        simulationResults = data.results;
        
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
            createVisualizationCharts(data.results);
            createClusterMap(data.input_data, data.results);
        }, 500);
    })
    .catch(error => {
        console.error('Error running simulation:', error);
        document.getElementById('loadingSection').classList.add('hidden');
        alert('Terjadi kesalahan dalam menjalankan simulasi. Silakan coba lagi.');
    });
}
