document.getElementById('due_date').min = new Date().toISOString().split('T')[0];

document.querySelectorAll('.project-item').forEach(item => {
    const menu = item.querySelector('.dots-menu');
    item.addEventListener('mouseleave', () => {
        menu.style.display = 'none';
    });
});

document.getElementById('add-project-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const submitBtn = document.getElementById('submit-btn');
    const errorEl = document.getElementById('form-error');
    
    // Reset error
    errorEl.style.display = 'none';
    errorEl.innerText = '';

    // Disable button
    submitBtn.disabled = true;
    submitBtn.innerText = 'Generating steps...';

    const formData = new FormData(this);

    try {
        const response = await fetch('/add_project', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            // Show error inside modal
            errorEl.innerText = data.error;
            errorEl.style.display = 'block';
            submitBtn.disabled = false;
            submitBtn.innerText = 'Create Project';
        } else {
            window.location.href = data.redirect;
        }
    } catch (err) {
        errorEl.innerText = 'Something went wrong. Please try again.';
        errorEl.style.display = 'block';
        submitBtn.disabled = false;
        submitBtn.innerText = 'Create Project';
    }
});


let currentTaskId = null;

function openTaskModal(taskId, title, instructions) {
    currentTaskId = taskId;
    document.getElementById('task-modal-title').innerText = title;
    document.getElementById('task-modal-instructions').innerText = instructions;
    document.getElementById('task-modal-instructions').style.display = 'block';
    document.getElementById('task-modal-edit').style.display = 'none';
    document.getElementById('edit-btn').style.display = 'flex';
    document.getElementById('save-btn').style.display = 'none';
    document.getElementById('task-modal').style.display = 'flex';
}

function closeTaskModal() {
    document.getElementById('task-modal').style.display = 'none';
}

function enableEdit() {
    const instructions = document.getElementById('task-modal-instructions').innerText;
    document.getElementById('task-modal-edit').value = instructions;
    document.getElementById('task-modal-instructions').style.display = 'none';
    document.getElementById('task-modal-edit').style.display = 'block';
    document.getElementById('edit-btn').style.display = 'none';
    document.getElementById('save-btn').style.display = 'block';
}

async function saveInstructions() {
    const newInstructions = document.getElementById('task-modal-edit').value;

    const response = await fetch(`/update_task/${currentTaskId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instructions: newInstructions })
    });

    if (response.ok) {
        document.getElementById('task-modal-instructions').innerText = newInstructions;
        document.getElementById('task-modal-instructions').style.display = 'block';
        document.getElementById('task-modal-edit').style.display = 'none';
        document.getElementById('edit-btn').style.display = 'flex';
        document.getElementById('save-btn').style.display = 'none';

        const taskCards = document.querySelectorAll('.task-card');
        taskCards.forEach(card => {
            const onclick = card.getAttribute('onclick');
            if (onclick && onclick.includes(`openTaskModal(${currentTaskId},`)) {
                card.setAttribute('onclick', 
                    `openTaskModal(${currentTaskId}, '${document.getElementById('task-modal-title').innerText}', '${newInstructions.replace(/'/g, "\\'")}')`)
            }
        });

        closeTaskModal();
        showToast();
    }
}

function showToast() {
    const toast = document.getElementById('toast');
    toast.style.display = 'block';
    toast.style.opacity = '1';
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.style.display = 'none', 500);
    }, 2000);
}

function openRubricModal(row) {
    const criteria = row.dataset.criteria;
    const inContext = row.dataset.inContext;
    const levels = JSON.parse(row.dataset.levels);

    document.getElementById('rubric-modal-criteria').innerText = criteria;
    
    const inContextEl = document.getElementById('rubric-modal-in-context');
    if (inContext) {
        inContextEl.innerText = inContext;
        inContextEl.style.display = 'block';
    } else {
        inContextEl.style.display = 'none';
    }

    const levelsContainer = document.getElementById('rubric-modal-levels');
    levelsContainer.innerHTML = '';

    if (levels && levels.length > 0) {
        const table = document.createElement('table');
        table.className = 'rubric-table';
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Grade</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                ${levels.map(l => `
                    <tr>
                        <td style="white-space: nowrap;">${l.grade}</td>
                        <td>${l.description}</td>
                    </tr>
                `).join('')}
            </tbody>
        `;
        levelsContainer.appendChild(table);
    }

    document.getElementById('rubric-modal').style.display = 'flex';
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('sidebar-overlay').classList.toggle('open');
    document.getElementById('hamburger-btn').classList.toggle('hidden');
  }