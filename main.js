document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const predictBtn = document.getElementById('predictBtn');
    const previewImage = document.getElementById('previewImage');
    const resultSection = document.querySelector('.result-section');
    const diseaseType = document.getElementById('diseaseType');
    const confidence = document.getElementById('confidence');
    const details = document.getElementById('details');
    const resultImage = document.getElementById('resultImage');

    // Handle file input change (when user selects a file)
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFile(file);
        }
    });

    // Show image preview and enable the predict button
    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Mohon pilih file gambar');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            previewImage.style.display = 'block';  // Show image preview
            resultSection.style.display = 'none';  // Hide result section
        };
        reader.readAsDataURL(file);

        predictBtn.disabled = false;  // Enable the predict button
    }

    // Handle predict button click (send the file to the backend for analysis)
    predictBtn.addEventListener('click', async () => {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        try {
            predictBtn.disabled = true;
            predictBtn.textContent = 'Menganalisis...';

            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.error) {
                alert(result.error);
                return;
            }

            // Update the result section with server response
            diseaseType.textContent = result.class;
            confidence.textContent = `${(result.confidence * 100).toFixed(2)}%`;
            details.textContent = result.details;

            // Show result image
            resultImage.src = result.image_path;
            resultImage.style.display = 'block';

            resultSection.style.display = 'flex';  // Show the result section

        } catch (error) {
            alert('Error dalam memproses gambar. Silakan coba lagi.');
        } finally {
            predictBtn.disabled = false;
            predictBtn.textContent = 'Analisis Semangka';
        }
    });
});
