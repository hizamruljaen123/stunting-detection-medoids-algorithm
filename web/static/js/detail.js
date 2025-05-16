document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing detail page charts...');
    
    // Check if Chart is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded!');
        return;
    }

    // Get kecamatan from URL path
    const pathParts = window.location.pathname.split('/');
    const kecamatan = pathParts[pathParts.length - 1];

    // Initialize charts if elements exist
    function initChart(chartId, type, data, options = {}) {
        const ctx = document.getElementById(chartId);
        if (!ctx) {
            console.error(`Chart element ${chartId} not found`);
            return null;
        }
        return new Chart(ctx, { type, data, options });
    }

    // Fetch chart data from API
    fetch(`/api/chart_data/${kecamatan}`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            // Initialize Trend Chart (Line)
            initChart('trenChart', 'line', {
                labels: data.tahun_labels,
                datasets: [{
                    label: 'Total Kecelakaan',
                    data: data.jenis_data.map(item => item.total),
                    backgroundColor: 'rgba(78, 115, 223, 0.05)',
                    borderColor: 'rgba(78, 115, 223, 1)',
                    pointBackgroundColor: 'rgba(78, 115, 223, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(78, 115, 223, 1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true
                }]
            }, {
                maintainAspectRatio: false,
                responsive: true,
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.parsed.y} kasus`;
                            }
                        }
                    },
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Jumlah Kecelakaan'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Tahun'
                        }
                    }
                },
                animation: {
                    duration: 1000
                }
            });

            // Initialize Accident Type Chart (Doughnut)
            initChart('jenisChart', 'doughnut', {
                labels: data.jenis_labels,
                datasets: [{
                    data: data.jenis_values,
                    backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796'],
                    hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf', '#dda20a', '#be2617', '#656774'],
                    hoverBorderColor: "rgba(234, 236, 244, 1)",
                    borderWidth: 1
                }]
            }, {
                maintainAspectRatio: false,
                responsive: true,
                cutout: '70%',
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const value = context.raw;
                                const percentage = Math.round((value / total) * 100);
                                return `${context.label}: ${value} kasus (${percentage}%)`;
                            }
                        }
                    },
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            });

            // Initialize Age Group Chart (Pie)
            initChart('usiaChart', 'pie', {
                labels: data.usia_labels,
                datasets: [{
                    data: data.usia_values,
                    backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b'],
                    hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf', '#dda20a', '#be2617'],
                    hoverBorderColor: "rgba(234, 236, 244, 1)",
                    borderWidth: 1
                }]
            }, {
                maintainAspectRatio: false,
                responsive: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const value = context.raw;
                                const percentage = Math.round((value / total) * 100);
                                return `${context.label}: ${value} korban (${percentage}%)`;
                            }
                        }
                    },
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            });
        })
        .catch(error => {
            console.error('Error fetching chart data:', error);
            // Show error message to user
            const errorElement = document.getElementById('chartError');
            if (errorElement) {
                errorElement.textContent = 'Gagal memuat data grafik. Silakan coba lagi.';
                errorElement.style.display = 'block';
            }
        });
});