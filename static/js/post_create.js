document.addEventListener('DOMContentLoaded', function() {
    const tagPills = document.querySelectorAll('.tag-pill');
    
    tagPills.forEach(pill => {
        pill.addEventListener('click', function() {
            const checkbox = this.querySelector('input[type="checkbox"]');
            checkbox.checked = !checkbox.checked;
            
            if (checkbox.checked) {
                this.classList.add('bg-gray-800', 'text-white');
                this.classList.remove('bg-gray-200', 'text-gray-700');
            } else {
                this.classList.remove('bg-gray-800', 'text-white');
                this.classList.add('bg-gray-200', 'text-gray-700');
            }
        });
    });
});