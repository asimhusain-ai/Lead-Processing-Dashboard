
document.addEventListener('DOMContentLoaded', function() {
    initializeDragAndDrop();
    initializePreviewControls();
    hideUploadSection();
});

function initializeDragAndDrop() {
    const dropZones = document.querySelectorAll('.drop-zone');
    
    dropZones.forEach(dropZone => {
        const fileInput = dropZone.querySelector('.file-input');
        const dropZoneText = dropZone.querySelector('.drop-zone-text');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });
        
        dropZone.addEventListener('drop', handleDrop, false);
        
        dropZone.addEventListener('click', () => {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', function() {
            if (this.files.length) {
                updateFileNameDisplay(dropZoneText, this.files[0].name);
            }
        });
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight(e) {
        e.currentTarget.classList.add('active');
    }
    
    function unhighlight(e) {
        e.currentTarget.classList.remove('active');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        const fileInput = e.currentTarget.querySelector('.file-input');
        const dropZoneText = e.currentTarget.querySelector('.drop-zone-text');
        
        if (files.length) {
            fileInput.files = files;
            updateFileNameDisplay(dropZoneText, files[0].name);
        }
    }
    
    function updateFileNameDisplay(element, fileName) {
        element.textContent = `Selected file: ${fileName}`;
        element.style.color = '#4a90e2';
        element.style.fontWeight = '600';
    }
}

function initializePreviewControls() {
    const previewSelect = document.getElementById('preview-select');
    if (previewSelect) {
        const initialLimit = parseInt(previewSelect.value) || 10;
        updatePreview(initialLimit);
        
        previewSelect.addEventListener('change', function() {
            updatePreview(this.value);
        });
    }
}

function updatePreview(limit) {
    const tableBody = document.getElementById('preview-table');
    if (!tableBody) return;

    const rowsToShow = parseInt(limit) || 10;
    tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Loading preview...</td></tr>';
    
    if (window.filePath) {
        fetch(`/api/preview/${window.filePath}?limit=${rowsToShow}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    tableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Error: ${data.error}</td></tr>`;
                    return;
                }
                
                renderPreviewTable(tableBody, data);
            })
            .catch(error => {
                console.error('Error fetching preview data:', error);
                tableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Error loading preview</td></tr>`;
            });
    } else {
        if (window.previewData && window.previewData.length > 0) {
            renderPreviewTable(tableBody, window.previewData.slice(0, rowsToShow));
        } else {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No data available</td></tr>';
        }
    }
}

function renderPreviewTable(tableBody, data) {
    tableBody.innerHTML = '';
    
    if (data.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No data to display</td></tr>';
        return;
    }
    
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${escapeHtml(row.Name || '')}</td>
            <td>${escapeHtml(row.Email || '')}</td>
            <td>${escapeHtml(row.Phone || '')}</td>
            <td>${escapeHtml(row.Company || '')}</td>
            <td>${escapeHtml(row.Title || '')}</td>
        `;
        tableBody.appendChild(tr);
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Hide upload section after successful processing
function hideUploadSection() {
    const uploadForm = document.getElementById('upload-form');
    const formContainer = document.querySelector('.form-container');
    if (uploadForm && formContainer && window.fileUploaded) {
        formContainer.style.display = 'none';
    }
}

// Add some visual feedback for form submissions
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            const fileInput = this.querySelector('.file-input');
            const dropZoneText = this.querySelector('.drop-zone-text');
            
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
                submitBtn.disabled = true;
            }
            
            if (fileInput && fileInput.files.length > 0) {
                const file = fileInput.files[0];
                const fileSize = (file.size / (1024 * 1024)).toFixed(2);
                
                if (dropZoneText) {
                    dropZoneText.innerHTML = `Processing: ${file.name} (${fileSize} MB) <span class="spinner-border spinner-border-sm ms-2" role="status"></span>`;
                    dropZoneText.style.color = '#ff9800';
                }
                

                if (file.size > 100 * 1024 * 1024) { 
                    const existingAlert = document.querySelector('.large-file-alert');
                    if (!existingAlert) {
                        const alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-warning large-file-alert mt-2';
                        alertDiv.innerHTML = `
                            <i class="bi bi-exclamation-triangle"></i>
                            Large file detected (${fileSize} MB). This may take a few moments to process...
                        `;
                        if (dropZoneText && dropZoneText.parentNode) {
                            dropZoneText.parentNode.appendChild(alertDiv);
                        }
                    }
                }
            }
            
            // Debug logging for filter leads form
            if (form.id === 'upload-form' && window.location.pathname.includes('filter_leads')) {
                const rolesTextarea = document.getElementById('roles-textarea');
                const selectedRolesContainer = document.getElementById('selected-roles-container');
                const hiddenRoleInputs = selectedRolesContainer ? selectedRolesContainer.querySelectorAll('input[type="hidden"][name="roles"]') : [];
                
                console.log('=== FILTER LEADS DEBUG INFO ===');
                console.log('Roles textarea value:', rolesTextarea ? rolesTextarea.value : 'No textarea found');
                console.log('Hidden role inputs:', Array.from(hiddenRoleInputs).map(input => input.value));
                console.log('Number of roles being submitted:', hiddenRoleInputs.length);
                console.log('==============================');
            }
        });
    });
});

// Add file size validation
document.addEventListener('DOMContentLoaded', function() {
    const fileInputs = document.querySelectorAll('.file-input');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const maxSize = 2 * 1024 * 1024 * 1024;
            const file = this.files[0];
            
            if (file && file.size > maxSize) {
                alert('File size exceeds 2GB limit. Please choose a smaller file.');
                this.value = '';
                
                const dropZoneText = this.closest('.drop-zone').querySelector('.drop-zone-text');
                if (dropZoneText) {
                    dropZoneText.textContent = 'Drag & drop your file here or click to browse';
                    dropZoneText.style.color = '';
                    dropZoneText.style.fontWeight = '';
                }
            }
        });
    });
});