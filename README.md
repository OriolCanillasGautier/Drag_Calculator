# Virtual Wind Tunnel Aerodynamic Drag Calculator

A Python application for simulating aerodynamic drag forces in a virtual wind tunnel environment with 3D visualization.

> **Warning:** Not finished yet, there are some errors. If you encounter any issues, please [open an issue](https://github.com/your-repo/issues).

## Features

- **3D Visualization:** Render a virtual wind tunnel and loaded objects using PyVista.
- **STL Import Support:** Load STL files for 3D models.
- **Real-Time Drag Calculations:** Compute drag forces and power in real time.
- **Pressure Distribution Visualization:** Visualize pressure gradients on the model’s surface.
- **Interactive Object Manipulation:** Move, rotate, and scale objects interactively.
- **Screenshot Export:** Capture the current 3D view as an image.
- **Modern GUI:** Enjoy a sleek interface with theme support via `ttkthemes`.

![For instance, a funny simulation of a cow](https://github.com/user-attachments/assets/f89f39fe-6576-44ba-83b0-64dcae88b4c2)

## System Requirements

- **Python:** 3.7+
- **Operating Systems:** Windows, Linux, or macOS
- **Memory:** 4GB RAM (8GB recommended)
- **GPU:** OpenGL-capable GPU for hardware acceleration

## Installation

1. **Install Python**

   Download and install Python for your operating system from the [official website](https://www.python.org/downloads/).

2. **Install Dependencies**

   Install the required packages using pip:

   ```bash
   pip install pyvista pyvistaqt numpy ttkthemes vtk
   ```

3. **(Optional) Software Rendering**

   For systems without proper GPU support or if you prefer software rendering:

   ```bash
   pip install pyopengl
   ```

## Project Structure

```
.
├── drag_calculator.py       # Main entry point to launch the application
├── gui.py                   # GUI class (WindTunnelApp) and application logic
├── simulation.py            # Physics calculations (drag force and power)
├── visualization.py         # 3D visualization functions (drawing tunnel, streamlines, etc.)
└── config_manager.py        # Functions for saving and loading configuration files
```

- **drag_calculator.py:**  
  Starts the application by creating the main Tkinter window and initializing `WindTunnelApp` from `gui.py`.

- **gui.py:**  
  Contains the `WindTunnelApp` class which builds the UI, handles events (like loading STL files, moving objects, and running simulations), and integrates 3D visualization via PyVista. It delegates specific tasks to the other modules.

- **simulation.py:**  
  Implements the physics calculations for aerodynamic drag and power based on parameters like air density, velocity, frontal area, and drag coefficient.

- **visualization.py:**  
  Provides functions to render the tunnel, generate streamlines, and update pressure fields. These functions are called from the GUI logic.

- **config_manager.py:**  
  Manages saving and loading the application’s configuration (such as tunnel dimensions and flow parameters) in JSON format.

## Usage

1. **Run the Application**

   Start the app from your terminal:

   ```bash
   python drag_calculator.py
   ```

   *(On Windows, you can also double-click the `drag_calculator.py` file.)*

2. **Interface Overview**

   - **File Menu:**  
     Use the menu options to load STL models.

   - **Tunnel Parameters:**  
     Set tunnel dimensions (length, width, height).

   - **Flow Settings:**  
     Configure air velocity and density.

   - **Object Controls:**  
     Manipulate the object’s position, rotation, and scale using on-screen buttons.

   - **Simulation:**  
     Click "Run Simulation" to compute drag and pressure distribution.

   - **Export Options:**  
     Use the "Export Screenshot" and "Export Results" buttons to save images and data.

3. **Key Interactions**

   - **Object Movement:**  
     Use arrow buttons to reposition objects.
     
   - **Rotation:**  
     Rotate objects in 15° increments around the X, Y, or Z axes.
     
   - **Scaling:**  
     Adjust the scale using the provided XYZ factors.
     
   - **Simulation:**  
     Press "Run Simulation" to update drag/pressure analysis.
     
   - **Screenshot Export:**  
     Save a snapshot of the 3D visualization using the "Export Screenshot" button.

## Troubleshooting

- **Missing VTK DLLs (Windows):**

  ```bash
  pip install --upgrade vtk
  ```

- **Blank 3D Window:**
  1. Update your graphics drivers.
  2. Try software rendering by installing `pyopengl`:

     ```bash
     pip install pyopengl
     ```

- **STL Loading Issues:**
  - Ensure that your STL file is in binary format.
  - Verify that the model is scaled appropriately (1 unit = 1 meter).

## License

This project is licensed under the GNU General Public License v3.0 (GPLv3). See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please adhere to the following guidelines:

1. **Open an Issue:**  
   If you plan to make significant changes, open an issue first to discuss your ideas.

2. **Coding Standards:**  
   Follow [PEP8](https://www.python.org/dev/peps/pep-0008/) for Python code style.

3. **Testing:**  
   Include tests for any new features or changes.

*For best results, ensure that STL models are scaled to real-world dimensions (meters) before import.*
