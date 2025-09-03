/**
 * NEXUS Dashboard JavaScript
 * Dynamic task tracking and management system
 */

// Global data storage
let taskData = null;
let currentView = 'table';
let currentFilter = 'all';
let sortColumn = 'id';
let sortDirection = 'asc';

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', () => {
    // Clear old cached data if it's the old version
    const cachedData = localStorage.getItem('nexusTaskData');
    if (cachedData) {
        try {
            const parsed = JSON.parse(cachedData);
            if (parsed.tasks && parsed.tasks.length < 5000) {
                console.log('Clearing old cached data with', parsed.tasks.length, 'tasks');
                localStorage.removeItem('nexusTaskData');
            }
        } catch (e) {
            localStorage.removeItem('nexusTaskData');
        }
    }
    
    loadTaskData();
    setInterval(loadTaskData, 30000); // Auto-refresh every 30 seconds
});

/**
 * Load task data from JSON file
 */
async function loadTaskData() {
    try {
        // Force bypass cache with headers and timestamp
        const response = await fetch('nexus_tasks.json?nocache=' + Math.random() + '&t=' + Date.now(), {
            method: 'GET',
            cache: 'no-store',
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch JSON');
        }
        
        taskData = await response.json();
        
        // Verify we got the new data
        console.log('Loaded tasks:', taskData.tasks.length);
        console.log('Version:', taskData.metadata.version || 'unknown');
        console.log('File size: ~' + (JSON.stringify(taskData).length / 1024 / 1024).toFixed(2) + ' MB');
        
        // Don't cache large data in localStorage (>5MB limit)
        // Just store a small metadata flag
        try {
            localStorage.setItem('nexusDataVersion', taskData.tasks.length.toString());
            localStorage.setItem('nexusLastLoad', Date.now().toString());
        } catch (e) {
            console.warn('Could not cache metadata:', e);
        }
        
        updateDashboard();
        showToast(`Data loaded: ${taskData.tasks.length} tasks`, 'success');
    } catch (error) {
        console.error('Error loading task data:', error);
        showToast('Loading data... please wait', 'error');
        
        // For large data, always fetch fresh instead of using localStorage
        // Clear any old cached data
        try {
            localStorage.removeItem('nexusTaskData');
        } catch (e) {
            // Ignore
        }
    }
}

/**
 * Update entire dashboard with current data
 */
function updateDashboard() {
    if (!taskData) return;
    
    // Don't cache large data in localStorage (exceeds quota)
    // Data will be fetched fresh each time
    
    // Update metadata
    document.getElementById('lastUpdated').textContent = 
        new Date(taskData.metadata.last_updated || Date.now()).toLocaleString();
    document.getElementById('currentCheckpoint').textContent = 
        taskData.metadata.recovery_checkpoint || 'ENV-001';
    
    // Update statistics
    updateStatistics();
    
    // Update progress bar
    updateProgressBar();
    
    // Update phases
    updatePhases();
    
    // Update tasks view
    updateTasksView();
    
    // Update dependency graph
    updateDependencyGraph();
    
    // Update checkpoints
    updateCheckpoints();
}

/**
 * Update statistics cards
 */
function updateStatistics() {
    const stats = taskData.statistics;
    
    document.getElementById('totalTasks').textContent = stats.total_tasks || 0;
    document.getElementById('completedTasks').textContent = stats.completed || 0;
    document.getElementById('inProgressTasks').textContent = stats.in_progress || 0;
    document.getElementById('pendingTasks').textContent = stats.pending || 0;
    document.getElementById('blockedTasks').textContent = stats.blocked || 0;
}

/**
 * Update overall progress bar
 */
function updateProgressBar() {
    const progress = taskData.metadata.overall_progress || 0;
    
    document.getElementById('overallPercentage').textContent = `${progress}%`;
    document.getElementById('progressFill').style.width = `${progress}%`;
    
    // Add color coding based on progress
    const fill = document.getElementById('progressFill');
    if (progress < 25) {
        fill.style.background = 'linear-gradient(135deg, #ff3366 0%, #ff6666 100%)';
    } else if (progress < 50) {
        fill.style.background = 'linear-gradient(135deg, #ffaa00 0%, #ffcc00 100%)';
    } else if (progress < 75) {
        fill.style.background = 'linear-gradient(135deg, #00aaff 0%, #00ccff 100%)';
    } else {
        fill.style.background = 'linear-gradient(135deg, #00ff88 0%, #00d4ff 100%)';
    }
}

/**
 * Update phases grid
 */
function updatePhases() {
    const phasesGrid = document.getElementById('phasesGrid');
    phasesGrid.innerHTML = '';
    
    taskData.phases.forEach(phase => {
        const phaseCard = createPhaseCard(phase);
        phasesGrid.appendChild(phaseCard);
    });
}

/**
 * Create phase card element
 */
function createPhaseCard(phase) {
    const card = document.createElement('div');
    card.className = 'phase-card';
    card.onclick = () => filterByPhase(phase.id);
    
    // Calculate phase statistics
    const phaseTasks = phase.tasks || [];
    const completed = phaseTasks.filter(t => t.status === 'COMPLETED').length;
    const total = phaseTasks.length;
    const progress = total > 0 ? Math.round((completed / total) * 100) : 0;
    
    card.innerHTML = `
        <div class="phase-header">
            <div class="phase-title">${phase.name}</div>
            <div class="phase-id">${phase.id}</div>
        </div>
        <div class="phase-progress">
            <div class="phase-progress-bar">
                <div class="phase-progress-fill" style="width: ${progress}%"></div>
            </div>
        </div>
        <div class="phase-stats">
            <span>${completed}/${total} tasks</span>
            <span>${progress}% complete</span>
        </div>
        <div class="phase-meta" style="margin-top: 10px; font-size: 12px;">
            <span style="color: var(--text-muted);">Priority: ${phase.priority}</span>
            <span style="color: var(--text-muted); float: right;">Risk: ${phase.risk}</span>
        </div>
    `;
    
    return card;
}

/**
 * Update tasks view based on current view mode
 */
function updateTasksView() {
    const filteredTasks = filterTasks(false);
    
    switch(currentView) {
        case 'table':
            updateTableView(filteredTasks);
            break;
        case 'cards':
            updateCardsView(filteredTasks);
            break;
        case 'kanban':
            updateKanbanView(filteredTasks);
            break;
    }
}

/**
 * Update table view
 */
function updateTableView(tasks) {
    const tbody = document.getElementById('tasksTableBody');
    tbody.innerHTML = '';
    
    tasks.forEach(task => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span class="task-id">${task.id}</span></td>
            <td>${task.name}</td>
            <td>${task.phase || '-'}</td>
            <td><span class="status-badge ${task.status.toLowerCase().replace('_', '-')}">${task.status}</span></td>
            <td><span class="priority-badge ${task.priority}">${task.priority}</span></td>
            <td>
                <div class="dependency-list">
                    ${task.dependencies.map(d => `<span class="dependency-tag">${d}</span>`).join('')}
                </div>
            </td>
            <td>${task.time_estimate || '-'}</td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn" onclick="viewTaskDetails('${task.id}')" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn" onclick="editTaskStatus('${task.id}')" title="Edit Status">
                        <i class="fas fa-edit"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Update cards view
 */
function updateCardsView(tasks) {
    const grid = document.getElementById('tasksCardsGrid');
    grid.innerHTML = '';
    
    tasks.forEach(task => {
        const card = document.createElement('div');
        card.className = 'task-card';
        card.onclick = () => viewTaskDetails(task.id);
        
        card.innerHTML = `
            <div class="task-card-header">
                <span class="task-card-id">${task.id}</span>
                <span class="status-badge ${task.status.toLowerCase().replace('_', '-')}">${task.status}</span>
            </div>
            <div class="task-card-title">${task.name}</div>
            <div class="task-card-meta">
                <span class="priority-badge ${task.priority}">${task.priority}</span>
                <span style="color: var(--text-muted);">${task.time_estimate || 'No estimate'}</span>
            </div>
            ${task.actions.length > 0 ? `
                <div class="task-card-actions">
                    <ul class="task-card-action-list">
                        ${task.actions.slice(0, 3).map(a => `<li>${a}</li>`).join('')}
                        ${task.actions.length > 3 ? `<li>... and ${task.actions.length - 3} more</li>` : ''}
                    </ul>
                </div>
            ` : ''}
        `;
        
        grid.appendChild(card);
    });
}

/**
 * Update kanban view
 */
function updateKanbanView(tasks) {
    const columns = {
        pending: document.getElementById('pendingTasks'),
        in_progress: document.getElementById('inProgressTasksList'),
        completed: document.getElementById('completedTasksList'),
        blocked: document.getElementById('blockedTasksList')
    };
    
    // Clear all columns
    Object.values(columns).forEach(col => col.innerHTML = '');
    
    // Reset counts
    const counts = {
        pending: 0,
        in_progress: 0,
        completed: 0,
        blocked: 0
    };
    
    // Add tasks to appropriate columns
    tasks.forEach(task => {
        const status = task.status.toLowerCase().replace('_', '-');
        const column = columns[status] || columns.pending;
        
        const taskElement = document.createElement('div');
        taskElement.className = 'kanban-task';
        taskElement.draggable = true;
        taskElement.dataset.taskId = task.id;
        taskElement.onclick = () => viewTaskDetails(task.id);
        
        taskElement.innerHTML = `
            <div class="kanban-task-id">${task.id}</div>
            <div class="kanban-task-title">${task.name}</div>
            <div class="kanban-task-meta">
                <span class="priority-badge ${task.priority}">${task.priority}</span>
                <span>${task.time_estimate || 'No estimate'}</span>
            </div>
        `;
        
        column.appendChild(taskElement);
        counts[status] = (counts[status] || 0) + 1;
    });
    
    // Update counts
    document.getElementById('pendingCount').textContent = counts.pending;
    document.getElementById('inProgressCount').textContent = counts.in_progress;
    document.getElementById('completedCount').textContent = counts.completed;
    document.getElementById('blockedCount').textContent = counts.blocked;
    
    // Setup drag and drop
    setupDragAndDrop();
}

/**
 * Setup drag and drop for kanban board
 */
function setupDragAndDrop() {
    const tasks = document.querySelectorAll('.kanban-task');
    const columns = document.querySelectorAll('.kanban-tasks');
    
    tasks.forEach(task => {
        task.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('taskId', e.target.dataset.taskId);
            e.target.style.opacity = '0.5';
        });
        
        task.addEventListener('dragend', (e) => {
            e.target.style.opacity = '';
        });
    });
    
    columns.forEach(column => {
        column.addEventListener('dragover', (e) => {
            e.preventDefault();
            column.style.background = 'rgba(0, 212, 255, 0.1)';
        });
        
        column.addEventListener('dragleave', (e) => {
            column.style.background = '';
        });
        
        column.addEventListener('drop', (e) => {
            e.preventDefault();
            column.style.background = '';
            
            const taskId = e.dataTransfer.getData('taskId');
            const newStatus = column.parentElement.dataset.status.toUpperCase();
            
            updateTaskStatus(taskId, newStatus);
        });
    });
}

/**
 * Filter tasks based on current filters
 */
function filterTasks(updateView = true) {
    let filtered = [...taskData.tasks];
    
    // Apply status filter
    if (currentFilter !== 'all') {
        filtered = filtered.filter(t => 
            t.status.toLowerCase().replace('_', '-') === currentFilter
        );
    }
    
    // Apply search filter
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    if (searchTerm) {
        filtered = filtered.filter(t => 
            t.id.toLowerCase().includes(searchTerm) ||
            t.name.toLowerCase().includes(searchTerm) ||
            (t.phase && t.phase.toLowerCase().includes(searchTerm))
        );
    }
    
    // Apply priority filter
    const priorityFilter = document.getElementById('priorityFilter').value;
    if (priorityFilter !== 'all') {
        filtered = filtered.filter(t => t.priority === priorityFilter);
    }
    
    // Apply sorting
    filtered.sort((a, b) => {
        let aVal = a[sortColumn];
        let bVal = b[sortColumn];
        
        if (typeof aVal === 'string') aVal = aVal.toLowerCase();
        if (typeof bVal === 'string') bVal = bVal.toLowerCase();
        
        if (sortDirection === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });
    
    if (updateView) {
        updateTasksView();
    }
    
    return filtered;
}

/**
 * Filter by status
 */
function filterByStatus(status) {
    currentFilter = status;
    
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    filterTasks();
}

/**
 * Filter by phase
 */
function filterByPhase(phaseId) {
    document.getElementById('searchInput').value = phaseId;
    filterTasks();
    
    // Scroll to tasks section
    document.querySelector('.tasks-section').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Sort tasks by column
 */
function sortTasks(column) {
    if (sortColumn === column) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn = column;
        sortDirection = 'asc';
    }
    
    filterTasks();
}

/**
 * Change view mode
 */
function setView(view) {
    currentView = view;
    
    // Update active button
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Show/hide views
    document.querySelectorAll('.view-container').forEach(container => {
        container.classList.remove('active');
    });
    document.getElementById(`${view}View`).classList.add('active');
    
    updateTasksView();
}

/**
 * View task details in modal
 */
function viewTaskDetails(taskId) {
    const task = taskData.tasks.find(t => t.id === taskId);
    if (!task) return;
    
    const modal = document.getElementById('taskModal');
    const modalBody = document.getElementById('modalBody');
    
    document.getElementById('modalTaskId').textContent = `${task.id}: ${task.name}`;
    
    modalBody.innerHTML = `
        <div style="display: grid; gap: 15px;">
            <div>
                <strong>Status:</strong> 
                <span class="status-badge ${task.status.toLowerCase().replace('_', '-')}">${task.status}</span>
            </div>
            <div>
                <strong>Priority:</strong> 
                <span class="priority-badge ${task.priority}">${task.priority}</span>
            </div>
            <div>
                <strong>Phase:</strong> ${task.phase || 'N/A'}
            </div>
            <div>
                <strong>Time Estimate:</strong> ${task.time_estimate || 'N/A'}
            </div>
            <div>
                <strong>Risk Level:</strong> ${task.risk || 'N/A'}
            </div>
            ${task.line_range ? `
                <div>
                    <strong>Line Range:</strong> ${task.line_range}
                </div>
            ` : ''}
            ${task.dependencies.length > 0 ? `
                <div>
                    <strong>Dependencies:</strong>
                    <div class="dependency-list" style="margin-top: 5px;">
                        ${task.dependencies.map(d => `<span class="dependency-tag">${d}</span>`).join('')}
                    </div>
                </div>
            ` : ''}
            ${task.actions.length > 0 ? `
                <div>
                    <strong>Actions:</strong>
                    <ul style="margin-top: 5px; padding-left: 20px;">
                        ${task.actions.map(a => `<li>${a}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            ${task.checks.length > 0 ? `
                <div>
                    <strong>Verification Checks:</strong>
                    <ul style="margin-top: 5px; padding-left: 20px;">
                        ${task.checks.map(c => `<li>${c}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            ${task.verification ? `
                <div>
                    <strong>Verification Command:</strong>
                    <code style="display: block; margin-top: 5px; padding: 10px; background: var(--bg-secondary); border-radius: 5px;">
                        ${task.verification}
                    </code>
                </div>
            ` : ''}
            ${task.automation ? `
                <div>
                    <span style="background: var(--gradient-quantum); padding: 5px 10px; border-radius: 5px;">
                        <i class="fas fa-robot"></i> Automation Available
                    </span>
                </div>
            ` : ''}
        </div>
    `;
    
    modal.style.display = 'block';
    modal.dataset.currentTaskId = taskId;
}

/**
 * Edit task status
 */
function editTaskStatus(taskId) {
    const task = taskData.tasks.find(t => t.id === taskId);
    if (!task) return;
    
    const newStatus = prompt(
        `Update status for ${task.id}\n\nCurrent: ${task.status}\n\nEnter new status:\n- PENDING\n- IN_PROGRESS\n- COMPLETED\n- BLOCKED`,
        task.status
    );
    
    if (newStatus && ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'BLOCKED'].includes(newStatus.toUpperCase())) {
        updateTaskStatus(taskId, newStatus.toUpperCase());
    }
}

/**
 * Update task status
 */
function updateTaskStatus(taskId, newStatus) {
    // Find and update task
    const task = taskData.tasks.find(t => t.id === taskId);
    if (!task) return;
    
    const oldStatus = task.status;
    task.status = newStatus;
    
    // Update statistics
    const stats = taskData.statistics;
    stats[oldStatus.toLowerCase()]--;
    stats[newStatus.toLowerCase()]++;
    
    // Recalculate overall progress
    taskData.metadata.overall_progress = Math.round(
        (stats.completed / stats.total_tasks) * 100
    );
    
    // Update last modified
    taskData.metadata.last_updated = new Date().toISOString();
    
    // Save to JSON (would need backend endpoint in production)
    saveTaskData();
    
    // Refresh dashboard
    updateDashboard();
    
    showToast(`Task ${taskId} updated to ${newStatus}`, 'success');
}

/**
 * Save task data (placeholder - needs backend implementation)
 */
async function saveTaskData() {
    try {
        // In production, this would POST to a backend endpoint
        // Cannot save to localStorage - data too large (8+ MB exceeds 5MB limit)
        console.log('Task data updated in memory (', taskData.tasks.length, 'tasks)');
        
        // Attempt to save to file using File System API if available
        if ('showSaveFilePicker' in window) {
            // This would prompt user to save file
            // Commented out to avoid repeated prompts
            // const handle = await window.showSaveFilePicker();
            // const writable = await handle.createWritable();
            // await writable.write(JSON.stringify(taskData, null, 2));
            // await writable.close();
        }
    } catch (error) {
        console.error('Error saving task data:', error);
    }
}

/**
 * Update dependency graph
 */
function updateDependencyGraph() {
    const graphContainer = document.getElementById('dependencyGraph');
    
    // Create simple text representation of dependencies
    const deps = taskData.dependencies;
    const depsList = Object.entries(deps).slice(0, 10); // Show first 10
    
    if (depsList.length > 0) {
        graphContainer.innerHTML = `
            <div style="text-align: left; width: 100%;">
                <h4 style="margin-bottom: 15px;">Task Dependencies</h4>
                ${depsList.map(([task, deps]) => `
                    <div style="margin-bottom: 10px;">
                        <strong>${task}</strong> → ${deps.join(', ')}
                    </div>
                `).join('')}
                ${Object.keys(deps).length > 10 ? `
                    <div style="color: var(--text-muted); font-style: italic;">
                        ... and ${Object.keys(deps).length - 10} more dependencies
                    </div>
                ` : ''}
            </div>
        `;
    } else {
        graphContainer.innerHTML = '<div>No dependencies defined</div>';
    }
}

/**
 * Update checkpoints timeline
 */
function updateCheckpoints() {
    const timeline = document.getElementById('checkpointsTimeline');
    timeline.innerHTML = '';
    
    const checkpoints = taskData.checkpoints || [];
    const currentCheckpoint = taskData.metadata.recovery_checkpoint;
    
    checkpoints.forEach(checkpoint => {
        const item = document.createElement('div');
        item.className = 'checkpoint-item';
        
        // Determine if checkpoint is completed or current
        if (checkpoint.id === currentCheckpoint) {
            item.classList.add('current');
        } else if (checkpoint.id < currentCheckpoint) {
            item.classList.add('completed');
        }
        
        item.innerHTML = `
            <div class="checkpoint-dot"></div>
            <div class="checkpoint-label">${checkpoint.id}</div>
        `;
        
        timeline.appendChild(item);
    });
}

/**
 * Close modal
 */
function closeModal() {
    document.getElementById('taskModal').style.display = 'none';
}

/**
 * Refresh data
 */
function refreshData() {
    const btn = document.querySelector('.btn-refresh i');
    btn.classList.add('fa-spin');
    
    loadTaskData().then(() => {
        setTimeout(() => {
            btn.classList.remove('fa-spin');
        }, 500);
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    const toastIcon = toast.querySelector('i');
    
    toastMessage.textContent = message;
    
    // Update icon based on type
    toastIcon.className = type === 'success' ? 'fas fa-check-circle' : 
                         type === 'error' ? 'fas fa-exclamation-circle' : 
                         'fas fa-info-circle';
    
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('taskModal');
    if (event.target === modal) {
        closeModal();
    }
}