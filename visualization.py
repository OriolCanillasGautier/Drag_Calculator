# visualization.py
import numpy as np
import pyvista as pv

def draw_tunnel(plotter, tunnel_dims):
    length = tunnel_dims.get("length", 20)
    width  = tunnel_dims.get("width", 10)
    height = tunnel_dims.get("height", 10)
    bounds = (-length/2, length/2, -width/2, width/2, 0, height)
    tunnel = pv.Box(bounds=bounds)
    plotter.add_mesh(tunnel, color="#00BFFF", opacity=0.3,
                       style='wireframe', line_width=2, name='tunnel')

def add_wind_direction_indicator(plotter):
    arrow = pv.Arrow(direction=(1, 0, 0), tip_length=0.25, tip_radius=0.1, shaft_radius=0.03)
    plotter.add_mesh(arrow, color='gray', opacity=0.5,
                       name='wind_direction', show_edges=False)

def update_pressure_on_object(mesh, velocity, density):
    """
    Compute a pressure field on the object's surface.
    """
    wind = np.array([1, 0, 0])
    if "Normals" not in mesh.point_data:
        mesh = mesh.compute_normals(auto_orient_normals=True)
    normals = mesh.point_data["Normals"]
    dot_prod = np.abs((normals * wind).sum(axis=1))
    pressure = 0.5 * density * (velocity ** 2) * (1 - dot_prod)
    mesh["Pressure"] = pressure

def update_streamlines(plotter, tunnel_dims, velocity, turbulence_active):
    length = tunnel_dims.get("length", 20)
    width  = tunnel_dims.get("width", 10)
    height = tunnel_dims.get("height", 10)
    bounds = (-length/2, length/2, -width/2, width/2, 0, height)
    nx, ny, nz = 30, 20, 15
    x = np.linspace(bounds[0], bounds[1], nx)
    y = np.linspace(bounds[2], bounds[3], ny)
    z = np.linspace(bounds[4], bounds[5], nz)
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
    points = np.column_stack((X.ravel(), Y.ravel(), Z.ravel()))
    grid = pv.StructuredGrid()
    grid.points = points
    grid.dimensions = (nx, ny, nz)

    U = velocity * np.ones_like(X)
    V = 0.15 * velocity * np.tanh(Y)
    W = 0.15 * velocity * np.tanh(Z)
    vectors = np.column_stack((U.ravel(), V.ravel(), W.ravel()))
    if turbulence_active:
        turbulence = 0.2 * velocity * np.random.randn(vectors.shape[0], 3)
        vectors += turbulence
    grid["vectors"] = vectors

    # Seed points at the inlet of the tunnel
    seed_points_array = np.array([
        [bounds[0], y_val, z_val]
        for y_val in np.linspace(-width/3, width/3, 10)
        for z_val in np.linspace(height/4, 3*height/4, 10)
    ])
    seed_points = pv.PolyData(seed_points_array)
    
    streamlines = grid.streamlines(
        vectors='vectors',
        source=seed_points,
        n_points=1000,
        max_time=1000,
        integration_direction='forward',
        initial_step_length=0.1,
        terminal_speed=1e-5
    )
    return streamlines

def update_tunnel_pressure(plotter, tunnel_dims, velocity, density):
    length = tunnel_dims.get("length", 20)
    width  = tunnel_dims.get("width", 10)
    height = tunnel_dims.get("height", 10)
    nx = ny = nz = 20
    x = np.linspace(-length/2, length/2, nx)
    y = np.linspace(-width/2, width/2, ny)
    z = np.linspace(0, height, nz)
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
    points = np.column_stack((X.ravel(), Y.ravel(), Z.ravel()))
    grid = pv.StructuredGrid()
    grid.points = points
    grid.dimensions = (nx, ny, nz)
    
    d = X.ravel() + (length/2)
    pressure_values = 0.5 * density * velocity**2 * np.exp(- (d**2) / (length**2))
    grid["pressure"] = pressure_values
    pressure_volume = grid.threshold([pressure_values.min()*1.01, pressure_values.max()])
    
    plotter.add_mesh(
        pressure_volume,
        scalars="pressure",
        cmap="jet",
        opacity=0.3,
        clim=[pressure_values.min(), pressure_values.max()],
        name='tunnel_pressure'
    )
    return pressure_volume
