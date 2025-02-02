# config_manager.py
import json
from tkinter import filedialog

def save_config_file(app, tunnel_vars, flow_vars, scale_vars, object_position, result_var):
    try:
        config = {
            "tunnel": {k: v.get() for k, v in tunnel_vars.items()},
            "flow": {k: v.get() for k, v in flow_vars.items()},
            "scale": {k: v.get() for k, v in scale_vars.items()},
            "object_position": object_position
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, "w") as f:
                json.dump(config, f, indent=4)
            result_var.set(f"Config saved to: {file_path}")
    except Exception as e:
        result_var.set(f"Save config error: {str(e)}")

def load_config_file(app, tunnel_vars, flow_vars, scale_vars, object_position, update_tunnel_callback, result_var):
    try:
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, "r") as f:
                config = json.load(f)
            for k, var in tunnel_vars.items():
                var.set(config.get("tunnel", {}).get(k, var.get()))
            for k, var in flow_vars.items():
                var.set(config.get("flow", {}).get(k, var.get()))
            for k, var in scale_vars.items():
                var.set(config.get("scale", {}).get(k, var.get()))
            object_position[:] = config.get("object_position", object_position)
            update_tunnel_callback()
            result_var.set("Config loaded.")
        else:
            result_var.set("Config load cancelled.")
    except Exception as e:
        result_var.set(f"Load config error: {str(e)}")
