## Project Structure

```
.
├── drag_calculator.py
├── gui.py
├── simulation.py
├── visualization.py
└── config_manager.py
```

### 1. **drag_calculator.py (Main Entry Point)**

- **Purpose:**  
  This file is the starting point for the application. It creates the main window using a themed Tkinter root (from the `ttkthemes` package) and instantiates the `WindTunnelApp` class (defined in `gui.py`).

- **How It Works:**  
  When you run `drag_calculator.py`, it calls the `main()` function, which creates the main window, instantiates the application, and then enters the Tkinter event loop with `root.mainloop()`. This keeps the application responsive until the user closes the window.

---

### 2. **gui.py (Graphical User Interface and Application Logic)**

- **Purpose:**  
  This module contains the primary class, `WindTunnelApp`, which builds the user interface and ties together all other functionalities. It creates the Tkinter widgets, organizes them into panels, and integrates the 3D visualization window (using PyVista and pyvistaqt).

- **What’s Inside:**  
  - **GUI Setup:**  
    The class creates three main sections:
    - **Left Panel:** Contains controls for simulation parameters, tunnel dimensions, object movement, and velocity range analysis.
    - **Right Panel:** Contains additional controls for exporting data, saving/loading configurations, and object orientation (rotations and scaling).
    - **Visualization Panel:** Hosts the PyVista background plotter that renders the 3D scene.
    
  - **Event Handling & Delegation:**  
    Methods for actions such as loading an STL file, moving or rotating the object, running the simulation, and updating visualizations are defined here.  
    Many of these methods delegate tasks to functions in the other modules:
    - **Physics Calculations:** Handled in `simulation.py`
    - **Visualization Updates:** Handled in `visualization.py`
    - **Configuration Management:** Handled in `config_manager.py`
    
  - **Integration with PyVista:**  
    The PyVista `BackgroundPlotter` is set up in this file, and methods (such as updating the tunnel, pressure fields, and streamlines) call functions from `visualization.py`.

---

### 3. **simulation.py (Physics Calculations)**

- **Purpose:**  
  This module isolates the physics formulas used by the simulation. The goal is to keep the numerical calculations (such as the drag force and power) separate from the GUI code.

- **What’s Inside:**  
  - **`calculate_drag(...)`:**  
    Computes the drag force using the formula:  
    \[
    F_d = 0.5 \times \text{density} \times \text{velocity}^2 \times \text{frontal\_area} \times \text{drag\_coefficient}
    \]
  - **`calculate_power(...)`:**  
    Computes the power required to overcome drag (simply multiplying the drag force by the velocity).

- **Why Separate It:**  
  Isolating the physics calculations makes it easier to modify or test them independently from the user interface logic.

---

### 4. **visualization.py (3D Visualization Functions)**

- **Purpose:**  
  This module holds functions that create and update visual elements in the 3D scene using PyVista. The idea is to separate out the visualization-specific code from the GUI logic.

- **What’s Inside:**  
  - **`draw_tunnel(...)`:**  
    Draws the tunnel as a wireframe box based on the current dimensions.
  - **`add_wind_direction_indicator(...)`:**  
    Adds an arrow to indicate the wind direction.
  - **`update_pressure_on_object(...)`:**  
    Computes a pressure field on the surface of the loaded STL object (by using its normals and the current flow parameters) and attaches the result as a scalar field.
  - **`update_streamlines(...)`:**  
    Generates streamlines within the tunnel. It creates a structured grid covering the tunnel, computes a flow field (optionally with turbulence), seeds streamlines at the inlet, and returns a PyVista object representing the streamlines.
  - **`update_tunnel_pressure(...)`:**  
    Computes and renders a pressure volume within the tunnel. It uses an exponential decay profile to simulate the pressure distribution.

- **Why Separate It:**  
  This modular design makes it easier to adjust the visualization logic (for example, changing the pressure profile or the streamline parameters) without affecting the rest of the application.

---

### 5. **config_manager.py (Configuration Management)**

- **Purpose:**  
  This module manages saving and loading application configurations to and from JSON files. This can include tunnel dimensions, flow parameters, object scaling, and the current object position.

- **What’s Inside:**  
  - **`save_config_file(...)`:**  
    Gathers the current settings from the GUI, formats them as JSON, and writes them to a file.
  - **`load_config_file(...)`:**  
    Reads a configuration file, sets the corresponding variables in the GUI, and calls an update callback (to refresh the tunnel visualization, for example).

- **Why Separate It:**  
  Keeping configuration management separate makes it easy to modify or extend the saving/loading mechanism without touching the rest of the GUI or simulation code.

---

## How It All Works Together

1. **Program Launch:**  
   - Running `drag_calculator.py` starts the application.
   - It creates a themed Tkinter window and instantiates `WindTunnelApp` from `gui.py`.

2. **GUI Initialization:**  
   - `WindTunnelApp` sets up the main window with three areas (left panel, right panel, and the visualization panel).
   - It initializes PyVista’s background plotter and draws the tunnel, wind direction, and other default visual elements.

3. **User Interaction:**  
   - Users can interact with various controls (e.g., entering tunnel dimensions, flow parameters, moving or rotating the object).
   - When a control is used, the corresponding method in `WindTunnelApp` is called. These methods may:
     - Call functions in **simulation.py** for drag and power calculations.
     - Call functions in **visualization.py** to update 3D visualizations.
     - Call functions in **config_manager.py** to save or load configuration data.

4. **Modular and Maintainable:**  
   - Each module has a clear, single responsibility.
   - New features or changes can be made in the appropriate module without affecting unrelated code.
   - For example, if you need to change the physics model, you update `simulation.py`; if you want to adjust the visual appearance of the tunnel, you change `visualization.py`.

---

## Summary

- **Main File:**  
  `drag_calculator.py` starts the application.
  
- **GUI and Core Logic:**  
  `gui.py` builds the user interface, manages user events, and integrates the visualization window. It delegates specific tasks to the other modules.

- **Physics Calculations:**  
  `simulation.py` contains formulas for drag and power, keeping numerical code separate from the GUI.

- **Visualization:**  
  `visualization.py` handles all aspects of 3D rendering with PyVista (drawing the tunnel, computing pressure fields, generating streamlines).

- **Configuration Management:**  
  `config_manager.py` provides functions to save and load settings from JSON files, keeping configuration code modular.