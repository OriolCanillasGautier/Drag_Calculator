import tkinter as tk
from tkinter import ttk, filedialog
import pyvista as pv
from pyvistaqt import BackgroundPlotter
import numpy as np
from ttkthemes import ThemedTk

class WindTunnelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Wind Tunnel")
        self.setup_main_window()
        self.setup_visualization()
        self.setup_controls()
        self.setup_orientation_controls()
        self.setup_physics()
        self.setup_object_controls()
        self.setup_object_dimensions()  # New: controls for STL dimensions

    def setup_main_window(self):
        self.root.geometry("1400x800")
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Configure grid layout
        self.main_frame.columnconfigure(0, weight=0)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=0)
        self.main_frame.rowconfigure(2, weight=0)
        self.main_frame.rowconfigure(3, weight=0)  # New row for object dimensions

    def setup_visualization(self):
        # Create Qt frame for 3D visualization
        self.qt_frame = ttk.Frame(self.main_frame)
        self.qt_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Create PyVista plotter and show the plotter window
        self.plotter = BackgroundPlotter(show=True)
        self.plotter.set_background('white')
        self.add_wind_direction_indicator()

        # Draw tunnel (electric blue with blue edges and reduced opacity)
        self.draw_tunnel()

        # Set default camera position
        self.plotter.camera_position = 'yz'
        self.plotter.camera.azimuth = 30
        self.plotter.camera.elevation = 30

    def draw_tunnel(self):
        # Use default tunnel dimensions (length, width, height) as in control defaults
        length = 20
        width = 10
        height = 10
        # Tunnel bounds: centered along X; Y and Z from -width/2 to width/2 and 0 to height respectively
        bounds = (-length/2, length/2, -width/2, width/2, 0, height)
        # Create a box outlining the tunnel (wireframe)
        tunnel = pv.Box(bounds=bounds)
        self.plotter.add_mesh(
            tunnel,
            color="#00BFFF",
            opacity=0.3,
            style='wireframe',
            line_width=2,
            name='tunnel'
        )

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
        # Button to visualize pressure on the object
        ttk.Button(control_frame, text="Visualitza Pressió", command=self.visualize_pressure).grid(row=10, column=0, columnspan=2, pady=5)
        # Button to save screenshot
        ttk.Button(control_frame, text="Exporta Captura", command=self.save_screenshot).grid(row=11, column=0, columnspan=2, pady=5)

        # Results display
        self.result_var = tk.StringVar()
        ttk.Label(control_frame, textvariable=self.result_var, wraplength=250).grid(row=12, column=0, columnspan=2)

    def setup_orientation_controls(self):
        orient_frame = ttk.LabelFrame(self.main_frame, text="Controls d'Orientació")
        orient_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        # Buttons for 15° rotations on X, Y, and Z axes
        ttk.Button(orient_frame, text="Rotar X+", command=lambda: self.rotate_object('x', 15)).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(orient_frame, text="Rotar X-", command=lambda: self.rotate_object('x', -15)).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(orient_frame, text="Rotar Y+", command=lambda: self.rotate_object('y', 15)).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(orient_frame, text="Rotar Y-", command=lambda: self.rotate_object('y', -15)).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(orient_frame, text="Rotar Z+", command=lambda: self.rotate_object('z', 15)).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(orient_frame, text="Rotar Z-", command=lambda: self.rotate_object('z', -15)).grid(row=2, column=1, padx=5, pady=5)

    def setup_object_controls(self):
        control_frame = ttk.LabelFrame(self.main_frame, text="Object Position Controls")
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        # Position presets
        ttk.Button(control_frame, text="Center", command=lambda: self.move_object(0, 0, 0)).grid(row=0, column=0)
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

    def setup_object_dimensions(self):
        # New controls to scale the object dimensions
        dims_frame = ttk.LabelFrame(self.main_frame, text="Object Dimensions")
        dims_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        self.scale_vars = {
            'scale_x': tk.DoubleVar(value=1.0),
            'scale_y': tk.DoubleVar(value=1.0),
            'scale_z': tk.DoubleVar(value=1.0)
        }

        ttk.Label(dims_frame, text="Scale X:").grid(row=0, column=0, sticky="w")
        ttk.Entry(dims_frame, textvariable=self.scale_vars['scale_x']).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(dims_frame, text="Scale Y:").grid(row=1, column=0, sticky="w")
        ttk.Entry(dims_frame, textvariable=self.scale_vars['scale_y']).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(dims_frame, text="Scale Z:").grid(row=2, column=0, sticky="w")
        ttk.Entry(dims_frame, textvariable=self.scale_vars['scale_z']).grid(row=2, column=1, padx=5, pady=2)

        ttk.Button(dims_frame, text="Apply Scale", command=self.scale_object).grid(row=3, column=0, columnspan=2, pady=5)

    def setup_physics(self):
        self.drag_coefficient = 0.3
        self.object_position = [0, 0, 0]
        self.current_stl = None

    def load_stl(self):
        file_path = filedialog.askopenfilename(filetypes=[("STL Files", "*.stl")])
        if file_path:
            self.current_stl = pv.read(file_path)
            # Compute normals for pressure calculation
            self.current_stl = self.current_stl.compute_normals(auto_orient_normals=True)
            self.center_and_place_object()
            self.plotter.add_mesh(self.current_stl, color='lightgray', name='object')
            self.plotter.reset_camera()

    def center_and_place_object(self):
        # Center object and place on floor
        bounds = self.current_stl.bounds
        self.current_stl.translate([
            - (bounds[0] + bounds[1]) / 2,
            - (bounds[2] + bounds[3]) / 2,
            - bounds[4]  # Place on floor
        ])
        self.object_position = [0, 0, 0]

    def move_object(self, x=0, y=0, z=0):
        if self.current_stl:
            self.current_stl.translate([x, y, z])
            self.object_position = [a + b for a, b in zip(self.object_position, [x, y, z])]
            self.plotter.update()

    def scale_object(self):
        # Helper function to safely get float values even if a comma is used as decimal separator
        def safe_get(var):
            try:
                return var.get()
            except tk.TclError:
                val = var._tk.globalgetvar(var._name)
                return float(val.replace(",", "."))
        
        # Apply non-uniform scaling using the entered values
        if self.current_stl:
            sx = safe_get(self.scale_vars['scale_x'])
            sy = safe_get(self.scale_vars['scale_y'])
            sz = safe_get(self.scale_vars['scale_z'])
            self.current_stl.scale([sx, sy, sz], inplace=True)
            self.plotter.update()
        else:
            self.result_var.set("No STL object loaded to scale.")

    def rotate_object(self, axis, angle):
        if self.current_stl:
            if axis.lower() == 'x':
                self.current_stl.rotate_x(angle, point=(0, 0, 0), inplace=True)
            elif axis.lower() == 'y':
                self.current_stl.rotate_y(angle, point=(0, 0, 0), inplace=True)
            elif axis.lower() == 'z':
                self.current_stl.rotate_z(angle, point=(0, 0, 0), inplace=True)
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
            
            # Calculate frontal area using object's bounds
            bounds = self.current_stl.bounds if self.current_stl else [0]*6
            frontal_area = (bounds[3] - bounds[2]) * (bounds[5] - bounds[4])
            
            # Calculate drag force
            drag_force = 0.5 * density * (velocity ** 2) * frontal_area * self.drag_coefficient
            
            # Update results text
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
        # Remove previous flow visualization if exists
        self.plotter.remove_actor('flow_arrows')
        
        # Create flow vectors
        grid = pv.ImageData(
            dimensions=(10, 10, 10),
            spacing=(2, 2, 2),
            origin=(-10, -5, -5)
        )
        grid['vectors'] = np.zeros((grid.n_points, 3))
        grid['vectors'][:, 0] = velocity  # Flow in X direction
        
        # Create arrows for flow visualization
        arrows = grid.glyph(orient='vectors', scale=False, factor=1)
        self.plotter.add_mesh(
            arrows, 
            color='red', 
            opacity=0.3, 
            name='flow_arrows',
            show_edges=False
        )

    def visualize_pressure(self):
        if self.current_stl is None:
            self.result_var.set("No object loaded for pressure visualization.")
            return

        # Obtain flow parameters for pressure calculation
        velocity = self.flow_vars['velocity'].get()
        density = self.flow_vars['density'].get()
        wind = np.array([1, 0, 0])
        
        # Make sure normals exist
        if "Normals" not in self.current_stl.point_data:
            self.current_stl = self.current_stl.compute_normals(auto_orient_normals=True)
            
        normals = self.current_stl.point_data["Normals"]
        # Simplified pressure: higher on surfaces facing away from wind direction
        dot_prod = np.abs(np.sum(normals * wind, axis=1))
        pressure = 0.5 * density * (velocity ** 2) * (1 - dot_prod)
        self.current_stl["Pressure"] = pressure
        
        # Remove previous pressure visualization if exists
        try:
            self.plotter.remove_actor('object_pressure')
        except Exception:
            pass

        # Add mesh with pressure scalars, colormap "jet" and vertical scalar bar
        self.plotter.add_mesh(
            self.current_stl,
            scalars="Pressure",
            cmap="jet",
            opacity=0.7,
            scalar_bar_args={"vertical": True},
            name="object_pressure"
        )

    def save_screenshot(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG Files", "*.png")])
        if file_path:
            self.plotter.screenshot(file_path)
            self.result_var.set(f"Screenshot saved to: {file_path}")

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = WindTunnelApp(root)
    root.mainloop()