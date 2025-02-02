# gui.py
import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
import matplotlib.pyplot as plt
import json
import csv
import pyvista as pv
from pyvistaqt import BackgroundPlotter

from simulation import calculate_drag, calculate_power
from visualization import (
    draw_tunnel, add_wind_direction_indicator, update_pressure_on_object,
    update_streamlines, update_tunnel_pressure
)
from config_manager import save_config_file, load_config_file

class WindTunnelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Wind Tunnel")
        self.range_data = None
        self.setup_main_window()
        self.setup_ui_columns()
        self.setup_physics()

        # Visualization states
        self.streamlines = None
        self.pressure_volume = None
        self.turbulence_active = False
        
        self.setup_visualization()

    def setup_main_window(self):
        self.root.geometry("1400x900")
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.columnconfigure(0, weight=0)
        self.main_frame.columnconfigure(1, weight=0)
        self.main_frame.columnconfigure(2, weight=1)
        
        self.left_panel = ttk.Frame(self.main_frame)
        self.left_panel.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
        self.right_panel = ttk.Frame(self.main_frame)
        self.right_panel.grid(row=0, column=1, sticky="ns", padx=10, pady=10)
        self.qt_frame = ttk.Frame(self.main_frame)
        self.qt_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

    def setup_visualization(self):
        self.plotter = BackgroundPlotter(show=True)
        self.plotter.set_background('white')
        add_wind_direction_indicator(self.plotter)
        draw_tunnel(self.plotter, self.get_tunnel_dimensions())
        self.plotter.camera_position = 'yz'
        self.plotter.camera.azimuth = 30
        self.plotter.camera.elevation = 30

    def setup_ui_columns(self):
        # LEFT PANEL
        sim_frame_left = ttk.LabelFrame(self.left_panel, text="Simulation Controls")
        sim_frame_left.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(sim_frame_left, text="Tunnel Dimensions (m):").grid(row=0, column=0, sticky="w", columnspan=2)
        self.tunnel_vars = {
            'length': tk.DoubleVar(value=20),
            'width': tk.DoubleVar(value=10),
            'height': tk.DoubleVar(value=10)
        }
        ttk.Label(sim_frame_left, text="Length").grid(row=1, column=0, sticky="w")
        ttk.Entry(sim_frame_left, textvariable=self.tunnel_vars['length'], width=10).grid(row=1, column=1)
        ttk.Label(sim_frame_left, text="Width").grid(row=2, column=0, sticky="w")
        ttk.Entry(sim_frame_left, textvariable=self.tunnel_vars['width'], width=10).grid(row=2, column=1)
        ttk.Label(sim_frame_left, text="Height").grid(row=3, column=0, sticky="w")
        ttk.Entry(sim_frame_left, textvariable=self.tunnel_vars['height'], width=10).grid(row=3, column=1)
        ttk.Button(sim_frame_left, text="Apply Tunnel Dimensions", command=self.update_tunnel_dimensions).grid(row=4, column=0, columnspan=2, pady=5)
        
        ttk.Label(sim_frame_left, text="Flow Parameters:").grid(row=5, column=0, sticky="w", pady=(10,0))
        self.flow_vars = {
            'velocity': tk.DoubleVar(value=20),
            'density': tk.DoubleVar(value=1.225),
            'viscosity': tk.DoubleVar(value=1.8e-5)
        }
        ttk.Label(sim_frame_left, text="Velocity").grid(row=6, column=0, sticky="w")
        ttk.Entry(sim_frame_left, textvariable=self.flow_vars['velocity'], width=10).grid(row=6, column=1)
        ttk.Label(sim_frame_left, text="Density").grid(row=7, column=0, sticky="w")
        ttk.Entry(sim_frame_left, textvariable=self.flow_vars['density'], width=10).grid(row=7, column=1)
        ttk.Label(sim_frame_left, text="Viscosity").grid(row=8, column=0, sticky="w")
        ttk.Entry(sim_frame_left, textvariable=self.flow_vars['viscosity'], width=10).grid(row=8, column=1)
        ttk.Button(sim_frame_left, text="Load STL", command=self.load_stl).grid(row=9, column=0, columnspan=2, pady=5)
        ttk.Button(sim_frame_left, text="Run Simulation", command=self.run_simulation).grid(row=10, column=0, columnspan=2)
        ttk.Button(sim_frame_left, text="Visualize Pressure", command=self.visualize_pressure).grid(row=11, column=0, columnspan=2, pady=5)
        
        # Object Position Controls
        obj_ctrl_frame = ttk.LabelFrame(self.left_panel, text="Object Position Controls")
        obj_ctrl_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(obj_ctrl_frame, text="Step Size (m):").grid(row=0, column=0, sticky="w")
        self.move_step = tk.DoubleVar(value=0.5)
        ttk.Entry(obj_ctrl_frame, textvariable=self.move_step, width=8).grid(row=0, column=1)
        ttk.Button(obj_ctrl_frame, text="⟲", command=self.reset_object_position, width=3).grid(row=2, column=1, padx=2, pady=2)
        ttk.Button(obj_ctrl_frame, text="↑", command=lambda: self.move_object(y=self.move_step.get()), width=3).grid(row=1, column=1, padx=2, pady=2)
        ttk.Button(obj_ctrl_frame, text="↓", command=lambda: self.move_object(y=-self.move_step.get()), width=3).grid(row=3, column=1, padx=2, pady=2)
        ttk.Button(obj_ctrl_frame, text="←", command=lambda: self.move_object(x=-self.move_step.get()), width=3).grid(row=2, column=0, padx=2, pady=2)
        ttk.Button(obj_ctrl_frame, text="→", command=lambda: self.move_object(x=self.move_step.get()), width=3).grid(row=2, column=2, padx=2, pady=2)
        ttk.Button(obj_ctrl_frame, text="⭮", command=lambda: self.move_object(z=self.move_step.get()), width=3).grid(row=1, column=2, padx=2, pady=2)
        ttk.Button(obj_ctrl_frame, text="⭯", command=lambda: self.move_object(z=-self.move_step.get()), width=3).grid(row=3, column=0, padx=2, pady=2)
        
        ttk.Label(obj_ctrl_frame, text="Camera Views:").grid(row=4, column=0, columnspan=3)
        views = [('Front', 'xy'), ('Top', 'xz'), ('Left', 'yz'), ('Isometric', 'iso')]
        for i, (text, pos) in enumerate(views):
            ttk.Button(obj_ctrl_frame, text=text, command=lambda p=pos: self.set_camera_view(p)).grid(row=5+i//2, column=i%2, padx=2, pady=2)
        
        # Velocity Range Analysis
        analysis_frame = ttk.LabelFrame(self.left_panel, text="Velocity Range Analysis")
        analysis_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(analysis_frame, text="Start Velocity (m/s):").grid(row=0, column=0, sticky="w")
        self.vel_start_var = tk.StringVar(value="0.0")
        ttk.Entry(analysis_frame, textvariable=self.vel_start_var, width=10).grid(row=0, column=1)
        ttk.Label(analysis_frame, text="End Velocity (m/s):").grid(row=1, column=0, sticky="w")
        self.vel_end_var = tk.StringVar(value="30.0")
        ttk.Entry(analysis_frame, textvariable=self.vel_end_var, width=10).grid(row=1, column=1)
        ttk.Label(analysis_frame, text="Step (m/s):").grid(row=2, column=0, sticky="w")
        self.vel_step_var = tk.StringVar(value="0.1")
        ttk.Entry(analysis_frame, textvariable=self.vel_step_var, width=10).grid(row=2, column=1)
        ttk.Button(analysis_frame, text="Run Range Analysis", command=self.run_range_analysis).grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Button(analysis_frame, text="Export Range Data", command=self.export_range_data).grid(row=4, column=0, columnspan=2, pady=5)
        
        # A label to show messages
        self.result_var = tk.StringVar()
        ttk.Label(sim_frame_left, textvariable=self.result_var, wraplength=250).grid(row=12, column=0, columnspan=2, pady=5)
        
        # RIGHT PANEL (Additional controls)
        sim_frame_right = ttk.LabelFrame(self.right_panel, text="Additional Controls")
        sim_frame_right.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        ttk.Button(sim_frame_right, text="Export Screenshot", command=self.save_screenshot).grid(row=0, column=0, columnspan=2, pady=5)
        ttk.Button(sim_frame_right, text="Export Results", command=self.export_single_data).grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(sim_frame_right, text="Save Config", command=self.save_config).grid(row=2, column=0, columnspan=2, pady=5)
        ttk.Button(sim_frame_right, text="Load Config", command=self.load_config).grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Button(sim_frame_right, text="Show Streamlines", command=self.visualize_streamlines).grid(row=4, column=0, columnspan=2, pady=5)
        ttk.Button(sim_frame_right, text="Show Tunnel Pressure", command=self.visualize_tunnel_pressure).grid(row=5, column=0, columnspan=2, pady=5)
        ttk.Button(sim_frame_right, text="Toggle Turbulence", command=self.toggle_turbulence).grid(row=6, column=0, columnspan=2, pady=5)
        
        orient_frame = ttk.LabelFrame(self.right_panel, text="Orientation Controls")
        orient_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        ttk.Button(orient_frame, text="Rotate X+", command=lambda: self.rotate_object('x', 15)).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(orient_frame, text="Rotate X-", command=lambda: self.rotate_object('x', -15)).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(orient_frame, text="Rotate Y+", command=lambda: self.rotate_object('y', 15)).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(orient_frame, text="Rotate Y-", command=lambda: self.rotate_object('y', -15)).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(orient_frame, text="Rotate Z+", command=lambda: self.rotate_object('z', 15)).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(orient_frame, text="Rotate Z-", command=lambda: self.rotate_object('z', -15)).grid(row=2, column=1, padx=5, pady=5)
        
        dims_frame = ttk.LabelFrame(self.right_panel, text="Object Dimensions")
        dims_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.scale_vars = {
            'scale_x': tk.DoubleVar(value=1.0),
            'scale_y': tk.DoubleVar(value=1.0),
            'scale_z': tk.DoubleVar(value=1.0)
        }
        ttk.Label(dims_frame, text="Scale X:").grid(row=0, column=0, sticky="w")
        ttk.Entry(dims_frame, textvariable=self.scale_vars['scale_x'], width=10).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(dims_frame, text="Scale Y:").grid(row=1, column=0, sticky="w")
        ttk.Entry(dims_frame, textvariable=self.scale_vars['scale_y'], width=10).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(dims_frame, text="Scale Z:").grid(row=2, column=0, sticky="w")
        ttk.Entry(dims_frame, textvariable=self.scale_vars['scale_z'], width=10).grid(row=2, column=1, padx=5, pady=2)
        ttk.Button(dims_frame, text="Apply Scale", command=self.scale_object).grid(row=3, column=0, columnspan=2, pady=5)

    def setup_physics(self):
        self.drag_coefficient = 0.3
        self.object_position = [0, 0, 0]
        self.current_stl = None
        self.original_stl = None  # To allow reset

    def get_tunnel_dimensions(self):
        return {
            "length": self.tunnel_vars['length'].get(),
            "width": self.tunnel_vars['width'].get(),
            "height": self.tunnel_vars['height'].get()
        }

    def update_tunnel_dimensions(self):
        try:
            self.plotter.remove_actor('tunnel')
            if self.pressure_volume:
                self.plotter.remove_actor('tunnel_pressure')
                self.pressure_volume = None
            draw_tunnel(self.plotter, self.get_tunnel_dimensions())
            self.plotter.render()
        except Exception as e:
            self.result_var.set(f"Error updating tunnel: {str(e)}")

    def center_and_place_object(self):
        if self.current_stl:
            bounds = self.current_stl.bounds
            # Center the object and place it at the tunnel entrance
            self.current_stl.translate([
                -(bounds[0] + bounds[1]) / 2,
                -(bounds[2] + bounds[3]) / 2,
                -bounds[4]
            ], inplace=True)
            self.object_position = [0, 0, 0]

    def reset_object_position(self):
        if self.current_stl and self.original_stl:
            self.current_stl = self.original_stl.copy()
            self.center_and_place_object()
            self.plotter.remove_actor('object')
            self.plotter.add_mesh(self.current_stl, color='lightgray', name='object')
            self.plotter.render()
            self.result_var.set("Object reset to original position.")

    def move_object(self, x=0, y=0, z=0):
        if self.current_stl:
            tunnel = self.get_tunnel_dimensions()
            new_pos = [
                self.object_position[0] + x,
                self.object_position[1] + y,
                self.object_position[2] + z
            ]
            if (abs(new_pos[0]) > tunnel["length"]/2 or
                abs(new_pos[1]) > tunnel["width"]/2 or
                new_pos[2] < 0 or new_pos[2] > tunnel["height"]):
                self.result_var.set("Movement blocked: Object would exit tunnel bounds")
                return
            self.current_stl.translate([x, y, z], inplace=True)
            self.object_position = new_pos
            self.plotter.remove_actor('object')
            self.plotter.add_mesh(self.current_stl, color='lightgray', name='object')
            self.plotter.render()

    def load_stl(self):
        file_path = filedialog.askopenfilename(filetypes=[("STL Files", "*.stl")])
        if file_path:
            self.current_stl = pv.read(file_path)
            self.current_stl = self.current_stl.compute_normals(auto_orient_normals=True)
            self.center_and_place_object()
            self.original_stl = self.current_stl.copy()
            self.plotter.add_mesh(self.current_stl, color='lightgray', name='object')
            self.plotter.reset_camera()
            self.plotter.render()

    def scale_object(self):
        def safe_get(var):
            try:
                return var.get()
            except tk.TclError:
                return float(var._tk.globalgetvar(var._name).replace(",", "."))
        if self.current_stl:
            sx = safe_get(self.scale_vars['scale_x'])
            sy = safe_get(self.scale_vars['scale_y'])
            sz = safe_get(self.scale_vars['scale_z'])
            self.current_stl.scale([sx, sy, sz], inplace=True)
            self.plotter.render()
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
            self.plotter.render()

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
        self.plotter.render()

    def run_simulation(self):
        try:
            velocity = self.flow_vars['velocity'].get()
            density = self.flow_vars['density'].get()
            if self.current_stl:
                bounds = self.current_stl.bounds
            else:
                bounds = [0]*6
            frontal_area = (bounds[3] - bounds[2]) * (bounds[5] - bounds[4])
            drag = calculate_drag(density, velocity, frontal_area, self.drag_coefficient)
            power = calculate_power(drag, velocity)
            self.result_var.set(
                f"Drag Force: {drag:.2f} N\n"
                f"Power: {power:.2f} W\n"
                f"Velocity: {velocity} m/s\n"
                f"Frontal Area: {frontal_area:.2f} m²"
            )
            self.visualize_pressure()
            self.visualize_streamlines()
            self.visualize_tunnel_pressure()
        except Exception as e:
            self.result_var.set(f"Simulation error: {str(e)}")

    def visualize_pressure(self):
        if self.current_stl is None:
            self.result_var.set("No object loaded for pressure visualization.")
            return
        velocity = self.flow_vars['velocity'].get()
        density = self.flow_vars['density'].get()
        update_pressure_on_object(self.current_stl, velocity, density)
        try:
            self.plotter.remove_actor('object_pressure')
        except Exception:
            pass
        self.plotter.add_mesh(self.current_stl, scalars="Pressure", cmap="jet",
                              opacity=0.7, smooth_shading=True,
                              scalar_bar_args={"vertical": True},
                              name="object_pressure")
        self.plotter.render()

    def visualize_streamlines(self):
        try:
            if self.streamlines:
                self.plotter.remove_actor('streamlines')
            self.streamlines = update_streamlines(
                self.plotter, self.get_tunnel_dimensions(), self.flow_vars['velocity'].get(), self.turbulence_active
            )
            if self.streamlines.n_points > 0:
                self.plotter.add_mesh(self.streamlines, color='white', line_width=2, name='streamlines')
                self.result_var.set("Streamlines visualization updated")
            else:
                self.result_var.set("No streamlines to display")
            self.plotter.render()
        except Exception as e:
            self.result_var.set(f"Streamlines error: {str(e)}")

    def visualize_tunnel_pressure(self):
        try:
            if self.pressure_volume:
                self.plotter.remove_actor('tunnel_pressure')
            self.pressure_volume = update_tunnel_pressure(
                self.plotter, self.get_tunnel_dimensions(), self.flow_vars['velocity'].get(), self.flow_vars['density'].get()
            )
            self.plotter.render()
            self.result_var.set("Tunnel pressure visualization updated")
        except Exception as e:
            self.result_var.set(f"Pressure volume error: {str(e)}")

    def toggle_turbulence(self):
        self.turbulence_active = not self.turbulence_active
        status = "ON" if self.turbulence_active else "OFF"
        self.result_var.set(f"Turbulence simulation {status}")
        if self.streamlines:
            self.visualize_streamlines()

    def save_screenshot(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG Files", "*.png")])
        if file_path:
            self.plotter.screenshot(file_path)
            self.result_var.set(f"Screenshot saved to: {file_path}")

    def run_range_analysis(self):
        try:
            vs = float(self.vel_start_var.get())
            ve = float(self.vel_end_var.get())
            step = float(self.vel_step_var.get())
            if step <= 0 or vs >= ve:
                raise ValueError("Invalid velocity range or step.")
            density = self.flow_vars['density'].get()
            if self.current_stl:
                bounds = self.current_stl.bounds
            else:
                bounds = [-10, 10, -5, 5, 0, 10]
            frontal_area = (bounds[3] - bounds[2]) * (bounds[5] - bounds[4])
            velocities = np.arange(vs, ve+step/2, step)
            drag_forces = 0.5 * density * (velocities ** 2) * frontal_area * self.drag_coefficient
            powers = drag_forces * velocities
            self.range_data = {
                "velocities": velocities.tolist(),
                "drag_forces": drag_forces.tolist(),
                "powers": powers.tolist()
            }
            plt.figure("Drag and Power vs Velocity")
            plt.clf()
            plt.plot(velocities, drag_forces, label="Drag Force (N)")
            plt.plot(velocities, powers, label="Power (W)")
            plt.xlabel("Velocity (m/s)")
            plt.ylabel("Value")
            plt.title("Velocity Range Analysis")
            plt.legend()
            plt.grid(True)
            plt.show()
            self.result_var.set("Range analysis completed. See plot window.")
        except Exception as e:
            self.result_var.set(f"Range analysis error: {str(e)}")

    def export_single_data(self):
        try:
            velocity = self.flow_vars['velocity'].get()
            density = self.flow_vars['density'].get()
            bounds = self.current_stl.bounds if self.current_stl else [0]*6
            frontal_area = (bounds[3] - bounds[2]) * (bounds[5] - bounds[4])
            drag_force = 0.5 * density * (velocity ** 2) * frontal_area * self.drag_coefficient
            power = drag_force * velocity
            data = {
                "velocity": velocity,
                "drag_force_N": drag_force,
                "power_W": power,
                "frontal_area": frontal_area
            }
            file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                     filetypes=[("JSON Files", "*.json"),
                                                                ("CSV Files", "*.csv")])
            if file_path:
                if file_path.endswith(".json"):
                    with open(file_path, "w") as f:
                        json.dump(data, f, indent=4)
                else:
                    with open(file_path, "w", newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=data.keys())
                        writer.writeheader()
                        writer.writerow(data)
                self.result_var.set(f"Single run data exported to: {file_path}")
        except Exception as e:
            self.result_var.set(f"Export error: {str(e)}")

    def export_range_data(self):
        try:
            if self.range_data is None:
                self.result_var.set("No range analysis data to export.")
                return
            file_path = filedialog.asksaveasfilename(parent=self.root,
                                                     defaultextension=".json",
                                                     filetypes=[("JSON Files", "*.json"),
                                                                ("CSV Files", "*.csv")])
            if file_path:
                if file_path.endswith(".json"):
                    metadata = {
                        "tunnel": {k: v.get() for k, v in self.tunnel_vars.items()},
                        "flow": {k: v.get() for k, v in self.flow_vars.items()},
                        "scale": {k: v.get() for k, v in self.scale_vars.items()},
                        "object_position": self.object_position
                    }
                    export_data = {"metadata": metadata, "data": self.range_data}
                    with open(file_path, "w") as f:
                        json.dump(export_data, f, indent=4)
                else:
                    with open(file_path, "w", newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=["velocity", "drag_force_N", "power_W"])
                        writer.writeheader()
                        for v, d, p in zip(self.range_data["velocities"],
                                           self.range_data["drag_forces"],
                                           self.range_data["powers"]):
                            writer.writerow({"velocity": v, "drag_force_N": d, "power_W": p})
                self.result_var.set(f"Range data exported to: {file_path}")
        except Exception as e:
            self.result_var.set(f"Export error: {str(e)}")

    def save_config(self):
        save_config_file(self, self.tunnel_vars, self.flow_vars, self.scale_vars, self.object_position, self.result_var)

    def load_config(self):
        load_config_file(self, self.tunnel_vars, self.flow_vars, self.scale_vars, self.object_position, self.update_tunnel_dimensions, self.result_var)
