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

  function toggleAvatarDropdown(e) {
    e.stopPropagation();
    document.getElementById('avatar-dropdown').classList.toggle('open');
}

document.addEventListener('click', function() {
    document.getElementById('avatar-dropdown').classList.remove('open');
});

function openSettingsModal() {
    document.getElementById('avatar-dropdown').classList.remove('open');
    document.getElementById('settings-modal').style.display = 'flex';
}

function closeSettingsModal(e) {
    if (e.target === document.getElementById('settings-modal')) {
        document.getElementById('settings-modal').style.display = 'none';
    }
}

function saveAccount() {
    const username = document.getElementById('settings-username').value.trim();
    const email = document.getElementById('settings-email').value.trim();
    const password = document.getElementById('settings-password').value;
    const confirm = document.getElementById('settings-password-confirm').value;
    const errorEl = document.getElementById('account-error');
    const successEl = document.getElementById('account-success');
    errorEl.style.display = 'none';
    successEl.style.display = 'none';

    if (password && password !== confirm) {
        errorEl.textContent = 'Passwords do not match.';
        errorEl.style.display = 'block';
        return;
    }

    const payload = {};
    if (username) payload.username = username;
    if (email) payload.email = email;
    if (password) payload.password = password;

    fetch('/settings/account', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            errorEl.textContent = data.error;
            errorEl.style.display = 'block';
        } else {
            successEl.style.display = 'block';
            document.getElementById('settings-password').value = '';
            document.getElementById('settings-password-confirm').value = '';
        }
    });
}

function selectTheme(themeName, el) {
    document.querySelectorAll('.theme-swatch').forEach(s => s.classList.remove('active'));
    el.classList.add('active');
    const errorEl = document.getElementById('theme-error');
    const successEl = document.getElementById('theme-success');
    errorEl.style.display = 'none';
    successEl.style.display = 'none';

    fetch('/settings/theme', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ theme: themeName })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            errorEl.textContent = data.error;
            errorEl.style.display = 'block';
        } else {
            successEl.style.display = 'block';
            setTimeout(() => successEl.style.display = 'none', 2000);
        }
    });
}