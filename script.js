document.getElementById("generateEmptyMaze").addEventListener("click", generateEmptyMaze);
document.getElementById("generateRandomMaze").addEventListener("click", generateRandomMaze);
document.getElementById("simulate").addEventListener("click", simulateMicromouse);
document.getElementById("clearMaze").addEventListener("click", clearMaze);
document.getElementById("toggleObstacleMode").addEventListener("click", toggleObstacleMode);
document.getElementById("setStart").addEventListener("click", setStart);
document.getElementById("setEnd").addEventListener("click", setEnd);

let maze = [];
let start = null;
let destination = null;
let customObstacleMode = false;
let settingStart = false;
let settingEnd = false;

function generateEmptyMaze() {
  const rows = parseInt(document.getElementById("rows").value);
  const cols = parseInt(document.getElementById("columns").value);

  maze = Array.from({ length: rows }, () => Array(cols).fill(0));
  start = null;
  destination = null;

  renderMaze(rows, cols);
  document.getElementById("generateRandomMaze").disabled = false;
  document.getElementById("toggleObstacleMode").disabled = false;
  document.getElementById("clearMaze").disabled = false;
  document.getElementById("setStart").disabled = false;
  document.getElementById("setEnd").disabled = false;
}

function generateRandomMaze() {
  const density = parseInt(document.getElementById("density").value);

  for (let i = 0; i < maze.length; i++) {
    for (let j = 0; j < maze[0].length; j++) {
      maze[i][j] = Math.random() * 100 < density ? 1 : 0;
    }
  }

  renderMaze(maze.length, maze[0].length);
}

function renderMaze(rows, cols) {
  const mazeDiv = document.getElementById("maze");
  mazeDiv.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
  mazeDiv.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
  mazeDiv.innerHTML = "";

  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      const cell = document.createElement("div");
      cell.className = `cell ${maze[i][j] === 1 ? "obstacle" : "empty"}`;
      cell.dataset.row = i;
      cell.dataset.col = j;
      cell.addEventListener("click", () => handleCellClick(i, j));
      mazeDiv.appendChild(cell);
    }
  }
}

function handleCellClick(row, col) {
  const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);

  if (customObstacleMode) {
    // Toggle obstacle state in custom obstacle mode
    maze[row][col] = maze[row][col] === 1 ? 0 : 1;
    renderMaze(maze.length, maze[0].length);
  } else if (start && start[0] === row && start[1] === col) {
    // If the clicked cell is the start cell, remove the start point and reset it
    cell.classList.remove("start");
    start = null;
  } else if (destination && destination[0] === row && destination[1] === col) {
    // If the clicked cell is the destination cell, remove the destination and reset it
    cell.classList.remove("destination");
    destination = null;
    document.getElementById("simulate").disabled = true; // Disable simulate button when destination is removed
  } else if (!start) {
    // Set the new start cell if no start has been set
    start = [row, col];
    cell.classList.add("start");
  } else if (!destination) {
    // Set the destination cell if no destination has been set
    destination = [row, col];
    cell.classList.add("destination");
    document.getElementById("simulate").disabled = false; // Enable simulation button
  }
}



function simulateMicromouse() {
  if (!start || !destination) {
    alert("Please set both start and destination points.");
    return;
  }

  const directions = [
    [0, -1], [0, 1], [-1, 0], [1, 0]
  ];
  const queue = [[...start, 0]];  // Start the queue with the start position and distance 0
  const visited = Array.from({ length: maze.length }, () => Array(maze[0].length).fill(false));
  const parents = Array.from({ length: maze.length }, () => Array(maze[0].length).fill(null));

  visited[start[0]][start[1]] = true;

  while (queue.length) {
    const [x, y, dist] = queue.shift();  // Get the current position and distance

    // Update the cell to show the distance (except for start and destination)
    const cell = document.querySelector(`[data-row="${x}"][data-col="${y}"]`);
    if (x !== start[0] || y !== start[1]) {
      cell.innerText = dist;  // Set the distance in the cell
    }

    if (x === destination[0] && y === destination[1]) {
      reconstructPath(parents, x, y);
      return;
    }

    for (const [dx, dy] of directions) {
      const nx = x + dx, ny = y + dy;

      if (nx >= 0 && nx < maze.length && ny >= 0 && ny < maze[0].length &&
          maze[nx][ny] === 0 && !visited[nx][ny]) {
        visited[nx][ny] = true;
        queue.push([nx, ny, dist + 1]);  // Add the new position with an incremented distance
        parents[nx][ny] = [x, y];
      }
    }
  }

  alert("No path found.");
}


function reconstructPath(parents, x, y) {
  const path = []; // Array to store the path
  while (parents[x][y]) {
    path.push([x, y]); // Add the current cell to the path
    [x, y] = parents[x][y]; // Move to the parent cell
  }
  path.reverse(); // Reverse the path to start from the beginning

  // Animate the path with a delay

  path.forEach((cell, index) => {

    //animate until the last cell
    if (index < path.length - 1) { 
    setTimeout(() => {
      const [row, col] = cell;
      const cellElement = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
      cellElement.classList.add("path");
    }, index * 150); // Delay each cell by 150ms
  }
  });
}

function clearMaze() {
  maze = Array.from({ length: maze.length }, () => Array(maze[0].length).fill(0));
  start = null;
  destination = null;
  renderMaze(maze.length, maze[0].length);
  document.getElementById("simulate").disabled = true;
}

function toggleObstacleMode() {
  customObstacleMode = !customObstacleMode;

  // Disable/Enable the Set Start and Set End buttons based on obstacle mode state
  document.getElementById("setStart").disabled = customObstacleMode;
  document.getElementById("setEnd").disabled = customObstacleMode;

  // alert(customObstacleMode ? "Custom Obstacle Mode Enabled. Click on cells to toggle obstacles. Click again to disable. Then set start and end points." 
  //                          : "Custom Obstacle Mode Disabled. You can set Start and End points.");
}

function setStart() {
  settingStart = true;
  //alert("Click on a cell to set the start point.");
}

function setEnd() {
  settingEnd = true;
  //alert("Click on a cell to set the destination point.");
}
