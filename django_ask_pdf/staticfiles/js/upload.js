alert('upload.js loaded');
document.addEventListener('DOMContentLoaded', (event) => {
    const uploadButton = document.getElementById('upload-button');
    const uploadModal = document.getElementById('upload-modal');
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('pdf-file');
    const fileName = document.getElementById('file-name');
    const progressBar = document.getElementById('progress-bar');
    const form = document.getElementById('upload-form');

    uploadButton.addEventListener('click', () => {
        uploadModal.classList.remove('hidden');
        console.log("Clicked");
    });

    uploadModal.addEventListener('click', (e) => {
        if (e.target === uploadModal) {
            uploadModal.classList.add('hidden');
        }
    });

    dropzone.addEventListener('click', () => {
        fileInput.click();
    });

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('border-blue-500');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('border-blue-500');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('border-blue-500');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            updateFileName();
        }
    });

    fileInput.addEventListener('change', updateFileName);

    function updateFileName() {
        if (fileInput.files.length) {
            fileName.textContent = fileInput.files[0].name;
        } else {
            fileName.textContent = '';
        }
    }

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Redirect to the file page or show success message
                window.location.href = data.file_url;
            } else {
                // Show error message
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while uploading the file.');
        });

        // Show progress bar (this is simulated, you'd need to implement real progress tracking)
        progressBar.classList.remove('hidden');
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10;
            progressBar.firstElementChild.style.width = `${progress}%`;
            if (progress >= 100) clearInterval(interval);
        }, 200);
    });
});