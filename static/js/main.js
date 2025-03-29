// Main JavaScript for PDF Promo Material Checker

document.addEventListener('DOMContentLoaded', function() {
    // Add current year to footer
    const footerYear = document.querySelector('.footer .text-muted');
    if (footerYear) {
        const year = new Date().getFullYear();
        footerYear.innerHTML = footerYear.innerHTML.replace('{{ now.year }}', year);
    }
    
    // File input validation
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            if (fileName) {
                const fileExtension = fileName.split('.').pop().toLowerCase();
                if (fileExtension !== 'pdf') {
                    alert('Please select a PDF file.');
                    this.value = '';
                }
            }
        });
    }
    
    // Smooth scrolling for page navigation
    document.querySelectorAll('a[href^="#page_"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 20,
                    behavior: 'smooth'
                });
            }
        });
    });
}); 