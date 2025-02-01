import tkinter as tk
from tkinter import ttk, filedialog
import pyvista as pv
import numpy as np
from ttkthemes import ThemedTk
import os
import sys
import warnings

# Suppress VTK warnings
warnings.filterwarnings("ignore", category=UserWarning)

# VTK library path handling
if os.name == "nt":
    try:
        import vtkmodules.all as vtk
        from vtkmodules.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor
        vtk_path = os.path.join(os.path.dirname(vtk.__file__), '..', 'Lib', 'site-packages', 'vtkmodules')
        os.environ['PATH'] += os.pathsep + os.path.abspath(vtk_path)
    except ImportError:
        print("VTK modules not found - 3D visualization disabled")
        pv = None  # Disable PyVista functionality

class VirtualWindTunnel:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Wind Tunnel")
        self.root.geometry("1400x900")
        
        # Initialize state
        self.current_stl = None
        self.tunnel_bounds = [10, 10, 10]
        self.plotter = None
        
        self.setup_gui()
        self.setup_physics()
        self.setup_visualization()

    def setup_gui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control Panel
        control_frame = ttk.LabelFrame(main_frame, text="Simulation Controls")
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)

        # Tunnel Parameters
        ttk.Label(control_frame, text="Tunnel Dimensions (m)").grid(row=0, column=0, sticky=tk.W)
        self.tunnel_vars = {
            'width': tk.DoubleVar(value=10),
            'height': tk.DoubleVar(value=10),
            'length': tk.DoubleVar(value=20)
        }
        
        for i, (dim, var) in enumerate(self.tunnel_vars.items(), 1):
            ttk.Label(control_frame, text=dim.capitalize()).grid(row=i, column=0, sticky=tk.W)
            ttk.Entry(control_frame, textvariable=var).grid(row=i, column=1, padx=5, pady=2)

        # Flow Parameters
        ttk.Label(control_frame, text="Flow Settings").grid(row=4, column=0, sticky=tk.W)
        self.flow_vars = {
            'velocity': tk.DoubleVar(value=20),
            'density': tk.DoubleVar(value=1.225),
            'viscosity': tk.DoubleVar(value=1.8e-5)
        }
        
        for i, (param, var) in enumerate(self.flow_vars.items(), 5):
            ttk.Label(control_frame, text=param.capitalize()).grid(row=i, column=0, sticky=tk.W)
            ttk.Entry(control_frame, textvariable=var).grid(row=i, column=1, padx=5, pady=2)

        # Object Controls
        ttk.Button(control_frame, text="Load 3D Model", command=self.load_stl).grid(row=8, column=0, columnspan=2, pady=10)
        self.calculate_btn = ttk.Button(control_frame, text="Run Simulation", command=self.calculate_drag)
        self.calculate_btn.grid(row=9, column=0, columnspan=2, pady=5)

        # Results Display
        self.result_var = tk.StringVar()
        ttk.Label(control_frame, textvariable=self.result_var, wraplength=250).grid(row=10, column=0, columnspan=2)

        # Visualization Frame
        self.vis_frame = ttk.Frame(main_frame)
        self.vis_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky=tk.NSEW)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=0)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

    def setup_visualization(self):
        if pv is None:
            return
            
        try:
            self.plotter = pv.Plotter()
            self.plotter.set_background('white')
            
            # Create Tkinter VTK interactor
            self.tk_vtk = vtkTkRenderWindowInteractor(
                self.vis_frame,
                width=800,
                height=600
            )
            self.tk_vtk.Initialize()
            self.tk_vtk.Start()
            
            # Add render window to Tkinter
            self.plotter.ren_win = self.tk_vtk.GetRenderWindow()
            self.plotter.iren = self.tk_vtk.GetRenderWindow().GetInteractor()
            
            self.tk_vtk.pack(fill=tk.BOTH, expand=True)
            self.plotter.add_axes()
            self.plotter.show(auto_close=False)
            
        except Exception as e:
            print(f"3D visualization unavailable: {str(e)}")
            self.plotter = None

    def setup_physics(self):
        self.drag_coefficient = 0.3
        self.reference_area = 1.0

    def load_stl(self):
        if self.plotter is None:
            return
            
        file_path = filedialog.askopenfilename(filetypes=[("STL Files", "*.stl")])
        if file_path:
            try:
                self.current_stl = pv.read(file_path)
                self.plotter.clear()
                self.plotter.add_mesh(self.current_stl, color='lightgray', show_edges=True)
                self.auto_scale_object()
                self.update_tunnel_visualization()
                self.estimate_reference_area()
                self.plotter.iren.Render()
            except Exception as e:
                self.result_var.set(f"Error loading STL: {str(e)}")

    def auto_scale_object(self):
        if self.current_stl:
            bounds = self.current_stl.bounds
            size = [bounds[1]-bounds[0], bounds[3]-bounds[2], bounds[5]-bounds[4]]
            max_dim = max(size)
            self.current_stl.scale(5/max_dim, inplace=True)

    def update_tunnel_visualization(self):
        if self.plotter is None:
            return
            
        length = self.tunnel_vars['length'].get()
        width = self.tunnel_vars['width'].get()
        height = self.tunnel_vars['height'].get()
        
        tunnel = pv.Box(bounds=[
            0, length,
            -width/2, width/2,
            -height/2, height/2
        ])
        self.plotter.add_mesh(tunnel, color='lightblue', opacity=0.1, name='tunnel')
        self.plotter.add_mesh(tunnel.extract_feature_edges(), color='blue', line_width=2)
        self.plotter.iren.Render()

    def estimate_reference_area(self):
        if self.current_stl:
            bounds = self.current_stl.bounds
            self.reference_area = (bounds[3]-bounds[2]) * (bounds[5]-bounds[4])
            self.result_var.set(f"Estimated frontal area: {self.reference_area:.2f} m²")

    def calculate_drag(self):
        try:
            velocity = self.flow_vars['velocity'].get()
            density = self.flow_vars['density'].get()
            
            dynamic_pressure = 0.5 * density * velocity**2
            drag_force = dynamic_pressure * self.reference_area * self.drag_coefficient
            
            result_text = (
                f"Drag Force: {drag_force:.2f} N\n"
                f"Dynamic Pressure: {dynamic_pressure:.2f} Pa\n"
                f"Reynolds Number: {self.calculate_reynolds():.2e}"
            )
            self.result_var.set(result_text)
            self.visualize_flow()
        except Exception as e:
            self.result_var.set(f"Error: {str(e)}")

    def calculate_reynolds(self):
        velocity = self.flow_vars['velocity'].get()
        density = self.flow_vars['density'].get()
        viscosity = self.flow_vars['viscosity'].get()
        char_length = (self.reference_area)**0.5
        return (density * velocity * char_length) / viscosity

    def visualize_flow(self):
        if self.plotter is None or self.current_stl is None:
            return
            
        try:
            self.plotter.remove_actor('flow')
            self.plotter.remove_actor('flow_text')
            
            velocity = self.flow_vars['velocity'].get()
            length = self.tunnel_vars['length'].get()
            width = self.tunnel_vars['width'].get()
            height = self.tunnel_vars['height'].get()
            
            grid = pv.UniformGrid(
                dims=(10, 10, 10),
                spacing=(length/10, width/10, height/10)
            )
            grid.vectors = np.zeros((grid.n_points, 3))
            grid.vectors[:, 0] = velocity
            
            arrows = grid.glyph(orient="vectors", scale=False, factor=1)
            self.plotter.add_mesh(arrows, color='red', lighting=False, name='flow')
            self.plotter.add_text(
                f"Flow Velocity: {velocity} m/s",
                position='upper_right',
                font_size=12,
                name='flow_text'
            )
            self.plotter.iren.Render()
        except Exception as e:
            self.result_var.set(f"Visualization error: {str(e)}")

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = VirtualWindTunnel(root)
    root.mainloop()