import tkinter as tk
from tkinter import ttk, filedialog
import pyvista as pv
from pyvistaqt import BackgroundPlotter
import numpy as np
from ttkthemes import ThemedTk
# Removed unused imports: PyQt5 and sys

class WindTunnelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Wind Tunnel")
        self.setup_main_window()
        self.setup_visualization()
        self.setup_controls()
        self.setup_physics()
        self.setup_object_controls()

    def setup_main_window(self):
        self.root.geometry("1400x800")
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Configure grid layout
        self.main_frame.columnconfigure(0, weight=0)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

    def setup_visualization(self):
        # Create Qt frame for 3D visualization
        self.qt_frame = ttk.Frame(self.main_frame)
        self.qt_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Create PyVista plotter and show the plotter window
        self.plotter = BackgroundPlotter(show=True)
        self.plotter.set_background('white')
        # Add permanent wind direction indicator
        self.add_wind_direction_indicator()
        
        # Set default camera position
        self.plotter.camera_position = 'yz'
        self.plotter.camera.azimuth = 30
        self.plotter.camera.elevation = 30

    def add_wind_direction_indicator(self):
        # Create arrow showing wind direction
        arrow = pv.Arrow(direction=(1, 0, 0), tip_length=0.25, tip_radius=0.1, shaft_radius=0.03)
        self.plotter.add_mesh(
            arrow, 
            color='gray', 
            opacity=0.5, 
            name='wind_direction',
            show_edges=False
        )

    def setup_controls(self):
        control_frame = ttk.LabelFrame(self.main_frame, text="Simulation Controls")
        control_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Tunnel dimensions
        ttk.Label(control_frame, text="Tunnel Dimensions (m):").grid(row=0, column=0, sticky="w")
        self.tunnel_vars = {
            'length': tk.DoubleVar(value=20),
            'width': tk.DoubleVar(value=10),
            'height': tk.DoubleVar(value=10)
        }
        
        for i, (name, var) in enumerate(self.tunnel_vars.items(), 1):
            ttk.Label(control_frame, text=name.capitalize()).grid(row=i, column=0, sticky="w")
            ttk.Entry(control_frame, textvariable=var).grid(row=i, column=1)

        # Flow parameters
        ttk.Label(control_frame, text="\nFlow Parameters:").grid(row=4, column=0, sticky="w", pady=10)
        self.flow_vars = {
            'velocity': tk.DoubleVar(value=20),
            'density': tk.DoubleVar(value=1.225),
            'viscosity': tk.DoubleVar(value=1.8e-5)
        }
        
        for i, (name, var) in enumerate(self.flow_vars.items(), 5):
            ttk.Label(control_frame, text=name.capitalize()).grid(row=i, column=0, sticky="w")
            ttk.Entry(control_frame, textvariable=var).grid(row=i, column=1)

        # Object controls
        ttk.Button(control_frame, text="Load STL", command=self.load_stl).grid(row=8, column=0, columnspan=2, pady=10)
        ttk.Button(control_frame, text="Run Simulation", command=self.run_simulation).grid(row=9, column=0, columnspan=2)

        # Results display
        self.result_var = tk.StringVar()
        ttk.Label(control_frame, textvariable=self.result_var, wraplength=250).grid(row=10, column=0, columnspan=2)

    def setup_object_controls(self):
        control_frame = ttk.LabelFrame(self.main_frame, text="Object Position Controls")
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        # Position presets
        ttk.Button(control_frame, text="Center", command=lambda: self.move_object(0,0,0)).grid(row=0, column=0)
        ttk.Button(control_frame, text="Floor", command=lambda: self.move_object(z=-4.5)).grid(row=0, column=1)
        ttk.Button(control_frame, text="Left", command=lambda: self.move_object(x=-4)).grid(row=1, column=0)
        ttk.Button(control_frame, text="Right", command=lambda: self.move_object(x=4)).grid(row=1, column=1)

        # Camera controls
        ttk.Label(control_frame, text="Camera Views:").grid(row=2, column=0, columnspan=2)
        views = [
            ('Front', 'xy'), ('Top', 'xz'), 
            ('Left', 'yz'), ('Isometric', 'iso')
        ]
        for i, (text, pos) in enumerate(views):
            ttk.Button(control_frame, text=text, 
                      command=lambda p=pos: self.set_camera_view(p)).grid(row=3+i//2, column=i%2)

    def setup_physics(self):
        self.drag_coefficient = 0.3
        self.object_position = [0, 0, 0]
        self.current_stl = None

    def load_stl(self):
        file_path = filedialog.askopenfilename(filetypes=[("STL Files", "*.stl")])
        if file_path:
            self.current_stl = pv.read(file_path)
            self.center_and_place_object()
            self.plotter.add_mesh(self.current_stl, color='lightgray', name='object')
            self.plotter.reset_camera()

    def center_and_place_object(self):
        # Center object and place on floor
        bounds = self.current_stl.bounds
        self.current_stl.translate([
            - (bounds[0] + bounds[1])/2,
            - (bounds[2] + bounds[3])/2,
            - bounds[4]  # Place on floor
        ])
        self.object_position = [0, 0, 0]

    def move_object(self, x=0, y=0, z=0):
        if self.current_stl:
            self.current_stl.translate([x, y, z])
            self.object_position = [a+b for a,b in zip(self.object_position, [x,y,z])]
            self.plotter.update()

    def set_camera_view(self, position):
        views = {
            'xy': {'position': 'xy', 'azimuth': 0, 'elevation': 0},
            'xz': {'position': 'xz', 'azimuth': 0, 'elevation': 90},
            'yz': {'position': 'yz', 'azimuth': 90, 'elevation': 0},
            'iso': {'position': 'iso', 'azimuth': 45, 'elevation': 30}
        }
        self.plotter.camera_position = views[position]['position']
        self.plotter.camera.azimuth = views[position]['azimuth']
        self.plotter.camera.elevation = views[position]['elevation']
        self.plotter.update()

    def run_simulation(self):
        try:
            velocity = self.flow_vars['velocity'].get()
            density = self.flow_vars['density'].get()
            
            # Calculate frontal area
            bounds = self.current_stl.bounds if self.current_stl else [0]*6
            frontal_area = (bounds[3]-bounds[2]) * (bounds[5]-bounds[4])
            
            # Calculate drag force
            drag_force = 0.5 * density * (velocity ** 2) * frontal_area * self.drag_coefficient
            
            # Update results
            self.result_var.set(
                f"Drag Force: {drag_force:.2f} N\n"
                f"Velocity: {velocity} m/s\n"
                f"Frontal Area: {frontal_area:.2f} m²"
            )
            
            # Update flow visualization
            self.visualize_flow(velocity)
            
        except Exception as e:
            self.result_var.set(f"Error: {str(e)}")

    def visualize_flow(self, velocity):
        # Remove previous flow visualization
        self.plotter.remove_actor('flow_arrows')
        
        # Create flow vectors
        grid = pv.ImageData(
            dimensions=(10, 10, 10),
            spacing=(2, 2, 2),
            origin=(-10, -5, -5)
        )
        grid['vectors'] = np.zeros((grid.n_points, 3))
        grid['vectors'][:, 0] = velocity  # X-direction flow
        
        # Create arrows
        arrows = grid.glyph(orient='vectors', scale=False, factor=1)
        self.plotter.add_mesh(
            arrows, 
            color='red', 
            opacity=0.3, 
            name='flow_arrows',
            show_edges=False
        )

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = WindTunnelApp(root)
    root.mainloop()