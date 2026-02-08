import React, { useState, useEffect } from 'react';
import './TaskManager.css';

const TaskManager = () => {
  const [tasks, setTasks] = useState([
    { id: 1, title: 'Sample Task', description: 'This is a sample task', status: 'pending', priority: 'medium', createdAt: new Date() },
    { id: 2, title: 'Another Task', description: 'This is another sample task', status: 'in-progress', priority: 'high', createdAt: new Date() }
  ]);
  const [newTask, setNewTask] = useState({ title: '', description: '', priority: 'medium' });

  const handleAddTask = () => {
    if (newTask.title.trim() === '') return;

    const task = {
      id: tasks.length + 1,
      title: newTask.title,
      description: newTask.description,
      status: 'pending',
      priority: newTask.priority,
      createdAt: new Date()
    };

    setTasks([...tasks, task]);
    setNewTask({ title: '', description: '', priority: 'medium' });
  };

  const handleToggleStatus = (taskId) => {
    setTasks(tasks.map(task => {
      if (task.id === taskId) {
        const newStatus = task.status === 'completed' ? 'pending' : 'completed';
        return { ...task, status: newStatus };
      }
      return task;
    }));
  };

  const handleDeleteTask = (taskId) => {
    setTasks(tasks.filter(task => task.id !== taskId));
  };

  const getPriorityClass = (priority) => {
    switch (priority) {
      case 'high': return 'priority-high';
      case 'medium': return 'priority-medium';
      case 'low': return 'priority-low';
      default: return '';
    }
  };

  return (
    <div className="task-manager">
      <h3>Task Manager</h3>
      
      <div className="add-task-form">
        <input
          type="text"
          placeholder="Task title"
          value={newTask.title}
          onChange={(e) => setNewTask({...newTask, title: e.target.value})}
          className="task-input"
        />
        <textarea
          placeholder="Task description"
          value={newTask.description}
          onChange={(e) => setNewTask({...newTask, description: e.target.value})}
          className="task-textarea"
        />
        <select
          value={newTask.priority}
          onChange={(e) => setNewTask({...newTask, priority: e.target.value})}
          className="priority-select"
        >
          <option value="low">Low Priority</option>
          <option value="medium">Medium Priority</option>
          <option value="high">High Priority</option>
        </select>
        <button onClick={handleAddTask} className="add-task-button">
          Add Task
        </button>
      </div>

      <div className="tasks-list">
        {tasks.map(task => (
          <div key={task.id} className={`task-item ${task.status}`}>
            <div className="task-header">
              <h4>{task.title}</h4>
              <span className={`task-status ${task.status}`}>{task.status}</span>
            </div>
            <p className="task-description">{task.description}</p>
            <div className="task-meta">
              <span className={`priority-badge ${getPriorityClass(task.priority)}`}>
                {task.priority} priority
              </span>
              <span className="task-created">
                Created: {task.createdAt.toLocaleDateString()}
              </span>
            </div>
            <div className="task-actions">
              <button 
                onClick={() => handleToggleStatus(task.id)}
                className={`status-toggle ${task.status === 'completed' ? 'mark-pending' : 'mark-complete'}`}
              >
                {task.status === 'completed' ? 'Mark Pending' : 'Mark Complete'}
              </button>
              <button 
                onClick={() => handleDeleteTask(task.id)}
                className="delete-task"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TaskManager;