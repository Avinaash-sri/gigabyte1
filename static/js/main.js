document.addEventListener('DOMContentLoaded', function () {
    console.log("Dashboard JS loaded");

    const form = document.getElementById('verifyForm');
    const resultBox = document.getElementById('resultBox');
    const scanBtn = document.getElementById('scanBtn');
    const btnText = document.getElementById('btnText');
    const loader = document.getElementById('loader');

    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            console.log("Form submitted");

            const url = document.getElementById('urlInput').value;
            const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');

            if (!csrfTokenElement) {
                console.error("CSRF Token not found!");
                alert("Security Error: CSRF Token missing. Please refresh the page.");
                return;
            }
            const csrfToken = csrfTokenElement.value;

            // UI State: Loading
            scanBtn.disabled = true;
            btnText.style.display = 'none';
            if (loader) loader.style.display = 'inline-block';
            if (resultBox) resultBox.style.display = 'none';

            fetch('/verify/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: 'url=' + encodeURIComponent(url)
            })
                .then(response => {
                    console.log("Response status:", response.status);
                    if (!response.ok) {
                        throw new Error('Network response was not ok: ' + response.statusText);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("Data received:", data);
                    // UI Update
                    if (resultBox) {
                        resultBox.style.display = 'block';
                        resultBox.classList.add('active');
                    }

                    document.getElementById('resultUrl').textContent = data.url;
                    document.getElementById('trustScore').textContent = data.trust_score;

                    // Update specific metrics
                    if (data.breakdown) {
                        document.getElementById('legitimacyScore').textContent = data.breakdown.legitimacy + '%';
                        document.getElementById('brandScore').textContent = data.breakdown.brand + '%';
                        document.getElementById('scamScore').textContent = data.breakdown.scam + '%';
                        document.getElementById('reviewScore').textContent = data.breakdown.reviews + '%';

                        // Color coding for metrics
                        colorMetric('legitimacyScore', data.breakdown.legitimacy);
                        colorMetric('brandScore', data.breakdown.brand);
                        colorInverseMetric('scamScore', data.breakdown.scam); // High scam score is BAD (Red)
                        colorMetric('reviewScore', data.breakdown.reviews);
                    }

                    const safetyStatus = document.getElementById('safetyStatus');

                    if (data.is_safe) {
                        if (safetyStatus) {
                            safetyStatus.textContent = 'Trusted Platform';
                            safetyStatus.className = 'status-badge status-safe';
                        }
                    } else {
                        if (safetyStatus) {
                            safetyStatus.textContent = 'Potential Scam';
                            safetyStatus.className = 'status-badge status-unsafe';
                        }
                    }

                    // Append to history list dynamically
                    const historyList = document.querySelector('.history-list');
                    const noScansMsg = historyList.querySelector('li[style*="text-align: center"]');
                    if (noScansMsg) noScansMsg.remove();

                    const newItem = document.createElement('li');
                    newItem.className = 'history-item';
                    newItem.innerHTML = `
                    <span style="font-size: 0.9rem; max-width: 60%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${data.url}</span>
                    <span class="status-badge ${data.is_safe ? 'status-safe' : 'status-unsafe'}">${data.is_safe ? 'Trusted' : 'Suspicious'}</span>
                `;
                    historyList.prepend(newItem);
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Verification failed: ' + error.message);
                })
                .finally(() => {
                    // UI State: Reset Button
                    scanBtn.disabled = false;
                    btnText.style.display = 'inline-block';
                    if (loader) loader.style.display = 'none';
                });
        });
    }

    function colorMetric(elementId, score) {
        const el = document.getElementById(elementId);
        if (!el) return;
        if (score >= 80) el.style.color = '#4ade80'; // Green
        else if (score >= 50) el.style.color = '#eab308'; // Yellow
        else el.style.color = '#f87171'; // Red
    }

    // For metrics where HIGH score is BAD (e.g. Scam Score)
    function colorInverseMetric(elementId, score) {
        const el = document.getElementById(elementId);
        if (!el) return;
        if (score >= 50) el.style.color = '#f87171'; // Red (High Risk)
        else if (score >= 20) el.style.color = '#eab308'; // Yellow
        else el.style.color = '#4ade80'; // Green (Safe)
    }
});
