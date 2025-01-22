import tkinter as tk
from collections import deque
import random

class MazeSolver:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Interactive Maze Solver")
        self.root.geometry("1000x700")  # Increase the window size
        self.size_x, self.size_y = tk.IntVar(value=10), tk.IntVar(value=10)  # Default grid size (10x10)
        self.random_chance = tk.DoubleVar(value=30)  # Default random obstacle chance (30%)
        self.mode = "obstacle"  # Default mode is obstacle placement
        self.grid, self.start, self.end = [], None, None  # Initialize grid and start/end points
        self.distances = {}  # Store distances for pathfinding
        self.cell_size = 20  # Size of each cell in the grid
        self.current_path = []  # To store the calculated path
        self.create_ui()  # Initialize the UI elements
        self.init_grid()  # Initialize the grid
        self.root.mainloop()  # Run the Tkinter main loop

    def create_ui(self):
        # Frame for controls (buttons, input fields)
        ctrl = tk.Frame(self.root, pady=10, padx=10, bg="#2c3e50")
        ctrl.pack(fill="x", pady=10)

        # Size controls (input fields for grid rows and columns)
        for label, var in [("Rows:", self.size_y), ("Cols:", self.size_x)]:
            tk.Label(ctrl, text=label, font=("Helvetica", 10, "bold"), fg="white", bg="#2c3e50").pack(side="left")
            tk.Entry(ctrl, textvariable=var, width=4, font=("Helvetica", 10), justify="center").pack(side="left", padx=5)
        tk.Button(ctrl, text="Resize", command=self.init_grid, bg="#2980b9", fg="white", font=("Helvetica", 10)).pack(side="left", padx=10)

        # Random generation controls (input field for obstacle percentage)
        tk.Label(ctrl, text="Obstacles %:", font=("Helvetica", 10, "bold"), fg="white", bg="#2c3e50").pack(side="left", padx=10)
        tk.Entry(ctrl, textvariable=self.random_chance, width=4, font=("Helvetica", 10), justify="center").pack(side="left", padx=5)
        tk.Button(ctrl, text="Generate Random", command=self.random_maze, bg="#e67e22", fg="white", font=("Helvetica", 10)).pack(side="left", padx=10)

        # Mode buttons (to switch between placing obstacles, start, and end points)
        modes = [("Manual Obstacles", "obstacle", "#34495e"), ("Start", "start", "#27ae60"),
                 ("End", "end", "#c0392b")]
        for text, mode, color in modes:
            cmd = lambda m=mode: self.set_mode(m)  # Lambda function to set the mode
            tk.Button(ctrl, text=text, command=cmd, bg=color, fg="white", font=("Helvetica", 10)).pack(side="left", padx=10)

        # Clear grid button
        tk.Button(ctrl, text="Clear", command=self.init_grid, bg="#e74c3c", fg="white", font=("Helvetica", 10)).pack(side="left", padx=10)

        # Simulate button to start the pathfinding simulation
        tk.Button(ctrl, text="Simulate", command=self.simulate, bg="#2980b9", fg="white", font=("Helvetica", 10)).pack(side="left", padx=10)

        # Status label to display current mode or simulation messages
        self.status = tk.Label(self.root, text="Click to place obstacles, start, and end points", font=("Helvetica", 12), bg="#ecf0f1", fg="#2c3e50")
        self.status.pack(pady=10)

        # Canvas to draw the maze grid
        self.canvas = tk.Canvas(self.root, bg="#ecf0f1", bd=2, relief="solid")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.click)  # Bind mouse click for placing obstacles, start, and end points
        self.canvas.bind("<Configure>", lambda e: self.draw())  # Redraw the grid when the window is resized

    def set_mode(self, mode):
        """Sets the current mode (obstacle, start, end) and updates status."""
        self.mode = mode
        self.current_path = []  # Reset current path
        self.status.config(text=f"Mode: {mode.capitalize()}")

    def init_grid(self):
        """Initializes the grid based on the current size (rows x cols)."""
        self.grid = [[0] * self.size_x.get() for _ in range(self.size_y.get())]  # Create a grid with all cells set to 0 (empty)
        self.start = self.end = None  # Clear start and end points
        self.distances = {}  # Clear distance map
        self.current_path = []  # Clear any previous path
        self.draw()  # Redraw the grid

    def random_maze(self):
        """Generates a random maze with obstacles."""
        chance = self.random_chance.get() / 100  # Convert chance to a decimal (e.g., 30% becomes 0.3)
        self.grid = [[1 if random.random() < chance else 0  # 1 represents an obstacle, 0 represents empty space
                     for _ in range(self.size_x.get())] 
                     for _ in range(self.size_y.get())]
        self.start = self.end = None  # Clear start and end points
        self.current_path = []  # Clear any previous path
        self.draw()  # Redraw the grid

    def draw(self):
        """Draws the grid on the canvas."""
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()  # Get canvas width and height
        # Calculate optimal cell size based on the grid size and canvas size
        self.cell_size = min(max(4, min((w-20)//self.size_x.get(), (h-20)//self.size_y.get())), 40)
        self.canvas.delete("all")  # Clear previous drawings
        
        # Loop through the grid and draw each cell
        for y in range(len(self.grid)):
            for x in range(len(self.grid[0])):
                # Calculate coordinates to center the grid on the canvas
                x1, y1 = x * self.cell_size + (w - len(self.grid[0])*self.cell_size)//2, \
                        y * self.cell_size + (h - len(self.grid)*self.cell_size)//2
                # Determine cell color based on its value (obstacle, start, end, or path)
                fill = "#34495e" if self.grid[y][x] else "#ffffff"
                if (x, y) == self.start:
                    fill = "#27ae60"  # Green for start
                elif (x, y) == self.end:
                    fill = "#c0392b"  # Red for end
                if (x, y) in self.current_path:
                    if (x, y) != self.start and (x, y) != self.end:
                        fill = "#2980b9"  # Blue for path
                
                # Draw the rectangle for the cell
                self.canvas.create_rectangle(x1, y1, x1+self.cell_size, y1+self.cell_size,
                                            fill=fill, outline="#bdc3c7" if self.cell_size > 5 else fill)
                
                # Display distance in cells with calculated distance
                if (x, y) in self.distances and fill != "#34495e" and self.cell_size >= 12:
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2,
                                            text=str(self.distances[(x, y)]),
                                            fill="white" if fill == "#2980b9" else "#34495e",
                                            font=("Helvetica", min(self.cell_size-4, 12)))

    def click(self, event):
        """Handles mouse click for placing obstacles, start, and end points."""
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        grid_w, grid_h = len(self.grid[0])*self.cell_size, len(self.grid)*self.cell_size
        # Calculate grid position from mouse click coordinates
        x = (event.x - (w - grid_w)//2) // self.cell_size
        y = (event.y - (h - grid_h)//2) // self.cell_size
        
        if 0 <= x < len(self.grid[0]) and 0 <= y < len(self.grid):
            if self.mode == "obstacle":
                self.grid[y][x] = 1 - self.grid[y][x]  # Toggle obstacle (1 = obstacle, 0 = empty)
                self.current_path = []  # Reset the path
            elif self.mode == "start" and not self.grid[y][x]:
                self.start = (x, y)  # Set the start point
                self.current_path = []  # Reset the path
            elif self.mode == "end" and not self.grid[y][x]:
                self.end = (x, y)  # Set the end point
                self.calc_distances()  # Recalculate distances from the end
            self.draw()  # Redraw the grid

    def calc_distances(self):
        """Calculates distances from the end point to all other reachable cells."""
        if not self.end: return  # No end point set, so do nothing
        self.distances = {self.end: 0}  # Distance to the end point is 0
        queue = deque([self.end])  # BFS queue
        
        while queue:
            x, y = queue.popleft()
            # Explore neighboring cells (up, down, left, right)
            for nx, ny in [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]:
                if (0 <= nx < len(self.grid[0]) and 0 <= ny < len(self.grid) and
                    not self.grid[ny][nx] and (nx,ny) not in self.distances):
                    self.distances[(nx,ny)] = self.distances[(x,y)] + 1  # Set the distance
                    queue.append((nx,ny))  # Add the neighbor to the queue

    def simulate(self):
        """Simulates the pathfinding from start to end using the precomputed distances."""
        if not (self.start and self.end):
            self.status.config(text="Missing start or end points")
            return
        
        # Calculate the path first (greedy approach)
        path = [self.start]
        
        # Check if a valid path exists by following the minimum distance cells
        while path[-1] != self.end:
            x, y = path[-1]
            next_pos = min([(nx, ny) for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
                            if (nx, ny) in self.distances], key=lambda p: self.distances[p], default=None)
            if next_pos is None:
                self.status.config(text="No path found")  # No valid path found
                return
            path.append(next_pos)

        # Function to animate the path
        def animate_path(step_index=0):
            if step_index < len(path):
                self.current_path.append(path[step_index])
                self.status.config(text=f"Simulating Path: Step {step_index + 1} of {len(path)}")
                self.draw()  # Redraw the grid with the new path step
                self.root.after(150, animate_path, step_index + 1)  # Call the function again after 150ms delay

        # Start the animation
        self.current_path = []  # Clear previous path
        animate_path()  # Start animating the path

if __name__ == "__main__":
    MazeSolver()  # Run the maze solver