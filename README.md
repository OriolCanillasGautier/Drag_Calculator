**Virtual Wind Tunnel Aerodynamic Drag Calculator**  
A Python application for simulating aerodynamic drag forces in a virtual wind tunnel environment with 3D visualization.  
*Not finished yet, there are some errors, if you encounter any, open an issue.*
**Features**  
- 3D visualization of wind tunnel and loaded objects  
- STL file import support for 3D models  
- Real-time drag force calculations  
- Pressure distribution visualization with color gradients  
- Interactive object manipulation (position, rotation, scaling)  
- Screenshot export capability  
- Modern GUI with theme support  
![For instance, a funny simulation fo a cow](https://github.com/user-attachments/assets/f89f39fe-6576-44ba-83b0-64dcae88b4c2)

**System Requirements**  
- Python 3.7+  
- Windows/Linux/macOS  
- 4GB RAM (8GB recommended)  
- OpenGL-capable GPU (for hardware acceleration)  

**Installation**  
1. Install Python:

You can download Python for you Operative System [here](https://www.python.org/downloads/)
   
3. Install dependencies:  
```bash
pip install pyvista pyvistaqt numpy ttkthemes vtk
```  

3. (Optional) For software rendering:  
```bash
pip install pyopengl
```  

**Usage**  
1. Run the application from the terminal:  
```bash
python drag_calculator.py
```
*You can run it on windows by double-clicking on the Python file*

2. Interface controls:  
   - **File Menu**: Load STL models  
   - **Tunnel Parameters**: Set dimensions (length/width/height)  
   - **Flow Settings**: Configure air velocity/density  
   - **Object Controls**: Adjust position/rotation/scale  
   - **Simulation**: Calculate drag and visualize pressure  

3. Key interactions:  
   - Use arrow buttons to position objects  
   - Rotate objects in 15° increments (X/Y/Z axes)  
   - Scale objects using XYZ factors  
   - Press "Run Simulation" for drag/pressure analysis  
   - Export screenshots via "Export Image" button  

**Troubleshooting**  
- *Missing VTK DLLs (Windows)*:  
  ```bash
  pip install --upgrade vtk
  ```  

- *Blank 3D window*:  
  1. Update graphics drivers  
  2. Try software rendering:  
  ```bash
  pip install pyopengl
  ```  

- *STL loading issues*:  
  - Ensure binary STL format  
  - Verify model scale (1 unit = 1 meter)  

**License**  
GNU General Public License v3.0 (GPLv3) - See [LICENSE](LICENSE) for details.  

**Contributing**  
This project is licensed under GPLv3. Contributions must comply with the license terms.  
1. Open an issue to discuss changes  
2. Follow PEP8 coding standards  
3. Include tests for new features  

*For accurate results: Scale models to real-world dimensions (meters) before import.*
