document.getElementById('due_date').min = new Date().toISOString().split('T')[0];

document.querySelectorAll('.project-item').forEach(item => {
    const menu = item.querySelector('.dots-menu');
    item.addEventListener('mouseleave', () => {
        menu.style.display = 'none';
    });
});