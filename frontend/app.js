let token = "";
let currentUser = null;
let currentUserId = null;  // store numeric/user-id from backend
let selectedListId = null;
let editingTaskId = null;  // Track which task is being edited

// API Configuration
const API_CONFIG = {
  baseUrl: "http://localhost:8000/api/v1",
  endpoints: {
    login: "/login",
    users: "/users",
    todolists: "/todolists",
    tasks: "/tasks"
  },
};

// SIGNUP HANDLER
document.getElementById("signupLink").addEventListener("click", (e) => {
  e.preventDefault();
  document.getElementById("loginForm").classList.add("hidden");
  document.getElementById("signupForm").classList.remove("hidden");
});

document.getElementById("loginLink").addEventListener("click", (e) => {
  e.preventDefault();
  document.getElementById("signupForm").classList.add("hidden");
  document.getElementById("loginForm").classList.remove("hidden");
});

document.getElementById("signupForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("signupUsername").value;
  const email = document.getElementById("signupEmail").value;
  const password = document.getElementById("signupPassword").value;

  try {
    // Construct query string with all required fields
    const params = new URLSearchParams({
      username,
      email,
      password
    });
    
    const response = await fetch(
      `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.users}?${params.toString()}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        }
      }
    );

    if (response.ok) {
      // Show success message and switch back to login
      document.getElementById("signupSuccess").style.display = "block";
      document.getElementById("signupError").style.display = "none";
      
      // Clear form fields
      document.getElementById("signupUsername").value = "";
      document.getElementById("signupEmail").value = "";
      document.getElementById("signupPassword").value = "";
      
      // Switch back to login form after 2 seconds
      setTimeout(() => {
        document.getElementById("signupForm").classList.add("hidden");
        document.getElementById("loginForm").classList.remove("hidden");
        document.getElementById("signupSuccess").style.display = "none";
      }, 2000);
    } else {
      const data = await response.json();
      document.getElementById("signupError").style.display = "block";
      document.getElementById("signupError").textContent = data.detail || "Signup failed";
    }
  } catch (error) {
    console.error("Signup error:", error);
    document.getElementById("signupError").style.display = "block";
    document.getElementById("signupError").textContent = `Signup failed: ${error.message}`;
  }
});

// LOGIN HANDLER
document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  try {
    const response = await fetch(
      `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.login}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      }
    );

    const data = await response.json();
    if (response.ok) {
      token = data.access_token;
      currentUser = username;
      // Fetch and store user ID immediately
      const userRes = await fetch(
        `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.users}/${currentUser}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const userData = await userRes.json();
      currentUserId = userData.id;

      document.getElementById("loginContainer").classList.add("hidden");
      document.getElementById("appContainer").classList.remove("hidden");
      loadTodoLists();
    } else {
      document.getElementById("loginError").style.display = "block";
      document.getElementById("loginError").textContent =
        data.detail || "Login failed";
    }
  } catch (error) {
    console.error("Login error:", error);
    document.getElementById("loginError").style.display = "block";
    document.getElementById("loginError").textContent = `Login failed: ${
      error.message
    }`;
  }
});

// LOGOUT HANDLER
document.getElementById("logoutBtn").addEventListener("click", () => {
  token = "";
  currentUser = null;
  currentUserId = null;
  selectedListId = null;
  document.getElementById("appContainer").classList.add("hidden");
  document.getElementById("loginContainer").classList.remove("hidden");
  document.getElementById("todolist").innerHTML = "";
  document.getElementById("taskList").innerHTML = "";
  document.getElementById("noListSelected").classList.remove("hidden");
  document.getElementById("taskSection").classList.add("hidden");
  document.getElementById("editTaskModal").classList.add("hidden");
});

// CREATE A NEW TODO LIST
document.getElementById("createListForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const newListName = document.getElementById("newListName").value.trim();
  if (!newListName || !currentUserId) return;

  try {
    // POST using query parameter user_id and name
    const query = new URLSearchParams({ 
      user_id: currentUserId,
      name: newListName  // Add the name parameter
    });
    const res = await fetch(
      `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.todolists}?${query.toString()}`,
      {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      }
    );
    if (!res.ok) throw new Error("Could not create list");

    document.getElementById("newListName").value = "";
    loadTodoLists();
  } catch (error) {
    console.error("Create list error:", error);
  }
});

// CREATE A NEW TASK IN THE SELECTED LIST
document.getElementById("createTaskForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = document.getElementById("newTaskTitle").value.trim();
  const description = document.getElementById("newTaskDesc").value.trim();
  const priority = parseInt(
    document.getElementById("newTaskPriority").value
  );

  if (!selectedListId || !title || !currentUserId) return;

  try {
    // Construct query string with all required fields
    const params = new URLSearchParams({
      user_id: currentUserId,
      todolist_id: selectedListId,
      title,
      description,
      priority: priority.toString(),
    });
    const res = await fetch(
      `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.todolists}/${selectedListId}/tasks?${params.toString()}`,
      {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      }
    );
    if (!res.ok) {
      const err = await res.json();
      console.error("Backend error:", err);
      throw new Error("Could not create task");
    }

    document.getElementById("newTaskTitle").value = "";
    document.getElementById("newTaskDesc").value = "";
    document.getElementById("newTaskPriority").value = "1";
    loadTasksForList(selectedListId);
  } catch (error) {
    console.error("Create task error:", error);
  }
});

// EDIT TASK FORM SUBMISSION
document.getElementById("editTaskForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  
  if (!editingTaskId || !selectedListId) return;
  
  const title = document.getElementById("editTaskTitle").value.trim();
  const description = document.getElementById("editTaskDesc").value.trim();
  const priority = parseInt(document.getElementById("editTaskPriority").value);
  const completed = document.getElementById("editTaskCompleted").checked;
  
  try {
    // Construct query string with all fields to update
    const params = new URLSearchParams({
      todolist_id: selectedListId,
      title,
      description,
      priority: priority.toString(),
      completed: completed.toString()
    });
    
    // Use the second API endpoint format which seems more RESTful
    const res = await fetch(
      `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.todolists}/${selectedListId}/tasks/${editingTaskId}?${params.toString()}`,
      {
        method: "PUT",
        headers: { Authorization: `Bearer ${token}` },
      }
    );
    
    if (!res.ok) {
      const err = await res.json();
      console.error("Backend error:", err);
      throw new Error("Could not update task");
    }
    
    // Close modal and refresh task list
    closeEditTaskModal();
    loadTasksForList(selectedListId);
  } catch (error) {
    console.error("Update task error:", error);
    document.getElementById("editTaskError").textContent = `Error: ${error.message}`;
    document.getElementById("editTaskError").style.display = "block";
  }
});

// Close modal when clicking the close button
document.getElementById("closeEditTaskModal").addEventListener("click", () => {
  closeEditTaskModal();
});

// Close modal when clicking outside the modal content
document.getElementById("editTaskModal").addEventListener("click", (e) => {
  if (e.target === document.getElementById("editTaskModal")) {
    closeEditTaskModal();
  }
});

function closeEditTaskModal() {
  document.getElementById("editTaskModal").classList.add("hidden");
  editingTaskId = null;
  document.getElementById("editTaskError").style.display = "none";
}

// FETCH ALL TODO LISTS (with their tasks) FOR THE CURRENT USER
async function loadTodoLists() {
  try {
    if (!currentUserId) return;
    // GET /todolists/{user_id}/all
    const response = await fetch(
      `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.todolists}/${currentUserId}/all`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );
    const lists = response.ok ? await response.json() : [];
    const ul = document.getElementById("todolist");
    ul.innerHTML = "";

    lists.forEach((list) => {
      const li = document.createElement("li");
      
      // Format the created_at date if available
      let displayText = "";
      if (list.name && list.name.trim() !== "") {
        // If there's a name, use it
        displayText = list.name;
      } else if (list.created_at) {
        // Format the date nicely
        const createdDate = new Date(list.created_at);
        const formattedDate = createdDate.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
        displayText = `Todolist for date: ${formattedDate}`;
      } else {
        // Fallback if neither name nor created_at is available
        displayText = `List ${list.id}`;
      }
      
      li.innerHTML = `
        <span class="list-name">${displayText}</span>
        <button class="btn-small delete-list" data-id="${list.id}">X</button>
      `;
      li.classList.add("list-item");
      if (list.id === selectedListId) li.classList.add("selected");

      // Clicking a list loads its tasks
      li.addEventListener("click", () => {
        selectedListId = list.id;
        document
          .querySelectorAll(".list-item")
          .forEach((el) => el.classList.remove("selected"));
        li.classList.add("selected");

        // Update the task section header to show the current list name
        document.getElementById("taskSectionHeader").textContent = `Tasks - ${displayText}`;

        document.getElementById("noListSelected").classList.add("hidden");
        document.getElementById("taskSection").classList.remove("hidden");
        loadTasksForList(list.id);
      });

      // Delete list button
      li.querySelector(".delete-list").addEventListener("click", async (e) => {
        e.stopPropagation();
        try {
          console.log(`Attempting to delete todolist: ${list.id} for user: ${currentUserId}`);
          
          // The correct API format based on the curl example:
          // DELETE /todolists/user?todolist_id=todo
          const deleteUrl = `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.todolists}/${currentUserId}?todolist_id=${list.id}`;
          console.log(`DELETE request to: ${deleteUrl}`);
          
          const res = await fetch(deleteUrl, {
            method: "DELETE",
            headers: { 
              Authorization: `Bearer ${token}`,
              "accept": "application/json"
            },
          });
          
          console.log(`Delete response status: ${res.status}`);
          
          if (!res.ok) {
            let errorMessage = "Could not delete list";
            try {
              const errorData = await res.json();
              console.error("Server error response:", errorData);
              errorMessage = errorData.detail || errorMessage;
            } catch (jsonError) {
              console.error("Could not parse error response as JSON:", jsonError);
            }
            throw new Error(errorMessage);
          }
      
          // Try to get the success response
          try {
            const successData = await res.json();
            console.log("Delete success response:", successData);
          } catch (jsonError) {
            console.log("No JSON in success response");
          }
      
          if (list.id === selectedListId) {
            selectedListId = null;
            document.getElementById("taskList").innerHTML = "";
            document.getElementById("taskSection").classList.add("hidden");
            document.getElementById("noListSelected").classList.remove("hidden");
          }
          loadTodoLists();
        } catch (error) {
          console.error("Delete list error:", error);
          alert(`Failed to delete list: ${error.message}`);
        }
      });

      ul.appendChild(li);
    });
  } catch (error) {
    console.error("Error loading todo lists:", error);
  }
}

// FETCH ALL TASKS FOR A GIVEN LIST
async function loadTasksForList(listId) {
  try {
    const response = await fetch(
      `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.todolists}/${listId}/tasks`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );
    const tasks = response.ok ? await response.json() : [];
    const ul = document.getElementById("taskList");
    ul.innerHTML = "";

    // Sort tasks by priority (0 is highest)
    tasks.sort((a, b) => a.priority - b.priority);

    tasks.forEach((task) => {
      const li = document.createElement("li");
      li.classList.add("task-item");
      
      // Add priority indicator
      const priorityClass = task.priority === 0 ? "high-priority" : 
                           task.priority <= 3 ? "medium-priority" : "low-priority";
      
      li.innerHTML = `
        <div class="task-content">
          <input
            type="checkbox"
            class="task-complete"
            data-id="${task.id}"
            ${task.completed ? "checked" : ""}
          />
          <span class="task-title${task.completed ? " completed" : ""} ${priorityClass}">
            ${task.title}
          </span>
          <span class="task-priority">Priority: ${task.priority}</span>
        </div>
        <div class="task-actions">
          <button class="btn-small edit-task" data-id="${task.id}">Edit</button>
          <button class="btn-small delete-task" data-id="${task.id}">X</button>
        </div>
      `;

      // Make the task content clickable for editing
      li.querySelector(".task-content").addEventListener("click", (e) => {
        // Don't trigger edit if clicking on the checkbox
        if (e.target.classList.contains("task-complete")) return;
        
        openEditTaskModal(task);
      });

      // Edit task button
      li.querySelector(".edit-task").addEventListener("click", (e) => {
        e.stopPropagation();
        openEditTaskModal(task);
      });

      // Toggle completion
      li.querySelector(".task-complete").addEventListener("change", async (e) => {
        const completed = e.target.checked;
        try {
          const bodyParams = new URLSearchParams({ completed: completed.toString() });
          const res = await fetch(
            `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.todolists}/${listId}/tasks/${task.id}?${bodyParams.toString()}`,
            {
              method: "PUT",
              headers: { Authorization: `Bearer ${token}` },
            }
          );
          if (!res.ok) throw new Error("Could not update task");
          loadTasksForList(listId);
        } catch (error) {
          console.error("Update task error:", error);
        }
      });

      // Delete task
      li.querySelector(".delete-task").addEventListener("click", async (e) => {
        e.stopPropagation();
        try {
          const res = await fetch(
            `${API_CONFIG.baseUrl}/tasks/${task.id}?todolist_id=${listId}`,
            {
              method: "DELETE",
              headers: { Authorization: `Bearer ${token}` },
            }
          );
          if (!res.ok) throw new Error("Could not delete task");
          loadTasksForList(listId);
        } catch (error) {
          console.error("Delete task error:", error);
        }
      });

      ul.appendChild(li);
    });
  } catch (error) {
    console.error("Error loading tasks:", error);
  }
}

// Open the edit task modal and populate it with task data
function openEditTaskModal(task) {
  editingTaskId = task.id;
  
  // Populate form fields with current task data
  document.getElementById("editTaskTitle").value = task.title || "";
  document.getElementById("editTaskDesc").value = task.description || "";
  document.getElementById("editTaskPriority").value = task.priority || 0;
  document.getElementById("editTaskCompleted").checked = task.completed || false;
  
  // Show the modal
  document.getElementById("editTaskModal").classList.remove("hidden");
  
  // Focus on the title field
  document.getElementById("editTaskTitle").focus();
}