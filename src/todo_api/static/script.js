// URL de base de l'API
const API_BASE = '';

// Éléments du DOM
const taskForm = document.getElementById('taskForm');
const tasksList = document.getElementById('tasksList');

// Charger les tâches au démarrage
document.addEventListener('DOMContentLoaded', loadTasks);

// Gérer la soumission du formulaire
taskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await createTask();
});

// Fonction pour charger toutes les tâches
async function loadTasks() {
    try {
        const response = await fetch(`${API_BASE}/tasks/`);
        const tasks = await response.json();

        displayTasks(tasks);
    } catch (error) {
        console.error('Erreur lors du chargement des tâches:', error);
        tasksList.innerHTML = '<div class="task-item"><div class="task-content"><p>Erreur de chargement</p></div></div>';
    }
}

// Fonction pour afficher les tâches
function displayTasks(tasks) {
    if (tasks.length === 0) {
        tasksList.innerHTML = '<div class="task-item"><div class="task-content"><p>Aucune tâche pour le moment</p></div></div>';
        return;
    }

    tasksList.innerHTML = tasks.map(task => `
        <div class="task-item">
            <div class="task-content">
                <h3>${task.title}</h3>
                <p>${task.description}</p>
                <small>Créé le: ${new Date(task.created_at).toLocaleDateString('fr-FR')}</small>
            </div>
            <div class="task-meta">
                <span class="task-status status-${task.status.toLowerCase().replace(' ', '-')}">${task.status}</span>
                <div class="task-actions">
                    <button class="btn-edit" onclick="editTask(${task.id})">Modifier</button>
                    <button class="btn-delete" onclick="deleteTask(${task.id})">Supprimer</button>
                </div>
            </div>
        </div>
    `).join('');
}

// Fonction pour créer une tâche
async function createTask() {
    const formData = new FormData(taskForm);
    const taskData = {
        title: formData.get('title'),
        description: formData.get('description'),
        status: formData.get('status')
    };

    try {
        const response = await fetch(`${API_BASE}/tasks/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(taskData)
        });

        if (response.ok) {
            // Réinitialiser le formulaire
            taskForm.reset();
            // Recharger les tâches
            await loadTasks();
        } else {
            alert('Erreur lors de la création de la tâche');
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur de connexion');
    }
}

async function deleteTask(taskId) {
    // Demander confirmation
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette tâche ?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            // Recharger les tâches après suppression
            await loadTasks();
        } else {
            alert('Erreur lors de la suppression de la tâche');
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur de connexion');
    }
}

async function editTask(taskId) {
    // Récupérer la tâche actuelle
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}`);
        const task = await response.json();

        // Demander les nouvelles valeurs (simple avec prompt)
        const newTitle = prompt('Nouveau titre:', task.title);
        if (newTitle === null) return; // Annulé

        const newDescription = prompt('Nouvelle description:', task.description);
        if (newDescription === null) return; // Annulé

        const newStatus = prompt('Nouveau statut (To do, Doing, Done, Cancelled):', task.status);
        if (newStatus === null) return; // Annulé

        // Mettre à jour la tâche
        const updateResponse = await fetch(`${API_BASE}/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: newTitle,
                description: newDescription,
                status: newStatus
            })
        });

        if (updateResponse.ok) {
            // Recharger les tâches
            await loadTasks();
        } else {
            alert('Erreur lors de la modification');
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur de connexion');
    }
}