import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys

# Configuration
G_TOLERANCE_MIN = 0.9  # Minimum acceleration magnitude in g
G_TOLERANCE_MAX = 1.1  # Maximum acceleration magnitude in g

def parse_flysight2_sensor(filename):
    """Parse FlySight 2 SENSOR.CSV file and extract IMU data."""
    
    # Read the file
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Find the $DATA marker
    data_start = None
    for i, line in enumerate(lines):
        if line.strip() == '$DATA':
            data_start = i + 1
            break
    
    if data_start is None:
        raise ValueError("No $DATA marker found in file")
    
    # Extract IMU data
    imu_data = []
    
    for line in lines[data_start:]:
        parts = line.strip().split(',')
        if parts[0] == '$IMU':
            # Parse IMU message: time, wx, wy, wz, ax, ay, az, temperature
            time = float(parts[1])
            ax = float(parts[5])
            ay = float(parts[6])
            az = float(parts[7])
            imu_data.append([time, ax, ay, az])
    
    # Convert to numpy array
    imu_array = np.array(imu_data)
    
    return imu_array

def filter_by_magnitude(imu_data, min_g=G_TOLERANCE_MIN, max_g=G_TOLERANCE_MAX):
    """Filter acceleration vectors by magnitude."""
    
    # Extract acceleration components
    acc_vectors = imu_data[:, 1:4]
    
    # Calculate magnitudes
    magnitudes = np.linalg.norm(acc_vectors, axis=1)
    
    # Filter by magnitude
    mask = (magnitudes >= min_g) & (magnitudes <= max_g)
    
    filtered_data = imu_data[mask]
    filtered_magnitudes = magnitudes[mask]
    
    return filtered_data, filtered_magnitudes

def normalize_vectors(vectors):
    """Normalize vectors to unit length."""
    magnitudes = np.linalg.norm(vectors, axis=1)
    # Avoid division by zero
    magnitudes[magnitudes == 0] = 1
    return vectors / magnitudes[:, np.newaxis]

def create_sphere_visualization(imu_data, magnitudes):
    """Create interactive 3D sphere visualization of acceleration vectors."""
    
    # Extract and normalize acceleration vectors
    acc_vectors = imu_data[:, 1:4]
    normalized_vectors = normalize_vectors(acc_vectors)
    
    # Extract time for coloring
    times = imu_data[:, 0]
    
    # Create the figure
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Acceleration Vectors on Unit Sphere', 'Magnitude Distribution'),
        specs=[[{'type': 'scatter3d'}, {'type': 'histogram'}]],
        column_widths=[0.7, 0.3]
    )
    
    # Add the sphere wireframe
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 20)
    x_sphere = np.outer(np.cos(u), np.sin(v))
    y_sphere = np.outer(np.sin(u), np.sin(v))
    z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))
    
    # Add sphere surface (semi-transparent)
    fig.add_trace(
        go.Surface(
            x=x_sphere, y=y_sphere, z=z_sphere,
            opacity=0.1,
            colorscale='Gray',
            showscale=False,
            hoverinfo='skip'
        ),
        row=1, col=1
    )
    
    # Add acceleration vectors as points
    fig.add_trace(
        go.Scatter3d(
            x=normalized_vectors[:, 0],
            y=normalized_vectors[:, 1],
            z=normalized_vectors[:, 2],
            mode='markers',
            marker=dict(
                size=3,
                color=times,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(
                    title="Time (s)",
                    x=0.65
                )
            ),
            text=[f"Time: {t:.1f}s<br>Mag: {m:.3f}g<br>ax: {ax:.3f}<br>ay: {ay:.3f}<br>az: {az:.3f}" 
                  for t, m, ax, ay, az in zip(times, magnitudes, acc_vectors[:, 0], acc_vectors[:, 1], acc_vectors[:, 2])],
            hoverinfo='text',
            name='Acceleration Vectors'
        ),
        row=1, col=1
    )
    
    # Add magnitude histogram
    fig.add_trace(
        go.Histogram(
            x=magnitudes,
            nbinsx=50,
            name='Magnitude Distribution',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': f"FlySight 2 Acceleration Analysis (|a| ∈ [{G_TOLERANCE_MIN:.1f}, {G_TOLERANCE_MAX:.1f}]g)",
            'x': 0.5,
            'xanchor': 'center'
        },
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectmode='cube',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        showlegend=False,
        height=700,
        width=1200
    )
    
    # Update histogram axes
    fig.update_xaxes(title_text="Magnitude (g)", row=1, col=2)
    fig.update_yaxes(title_text="Count", row=1, col=2)
    
    return fig

def analyze_clusters(normalized_vectors):
    """Analyze potential clusters in the data."""
    
    # Calculate pairwise dot products to see how aligned vectors are
    dot_products = np.dot(normalized_vectors, normalized_vectors.T)
    
    # Find vectors that are highly aligned (dot product close to 1)
    aligned_threshold = 0.95
    aligned_pairs = np.sum(dot_products > aligned_threshold) - len(normalized_vectors)  # Subtract diagonal
    
    # Find vectors that are anti-aligned (dot product close to -1)
    antialigned_threshold = -0.95
    antialigned_pairs = np.sum(dot_products < antialigned_threshold)
    
    total_pairs = len(normalized_vectors) * (len(normalized_vectors) - 1) / 2
    
    print(f"\nCluster Analysis:")
    print(f"Total vectors: {len(normalized_vectors)}")
    print(f"Highly aligned pairs (dot > {aligned_threshold}): {aligned_pairs/2:.0f} ({aligned_pairs/2/total_pairs*100:.1f}%)")
    print(f"Anti-aligned pairs (dot < {antialigned_threshold}): {antialigned_pairs/2:.0f} ({antialigned_pairs/2/total_pairs*100:.1f}%)")
    
    # Calculate mean vector and its magnitude (concentration measure)
    mean_vector = np.mean(normalized_vectors, axis=0)
    concentration = np.linalg.norm(mean_vector)
    print(f"Concentration (|mean vector|): {concentration:.3f} (1=all aligned, 0=uniform)")

def main(filename):
    """Main function to process FlySight 2 sensor data and create visualization."""
    
    print(f"Reading FlySight 2 sensor data from: {filename}")
    
    # Parse the file
    imu_data = parse_flysight2_sensor(filename)
    print(f"Found {len(imu_data)} IMU samples")
    
    # Filter by magnitude
    filtered_data, magnitudes = filter_by_magnitude(imu_data)
    print(f"Filtered to {len(filtered_data)} samples with magnitude in [{G_TOLERANCE_MIN}, {G_TOLERANCE_MAX}]g")
    
    if len(filtered_data) == 0:
        print("No data points within magnitude tolerance!")
        return
    
    # Analyze clusters
    acc_vectors = filtered_data[:, 1:4]
    normalized_vectors = normalize_vectors(acc_vectors)
    analyze_clusters(normalized_vectors)
    
    # Create visualization
    fig = create_sphere_visualization(filtered_data, magnitudes)
    
    # Save the plot to HTML file with CDN
    output_file = "flysight_sphere_visualization.html"
    fig.write_html(output_file, include_plotlyjs='cdn')
    print(f"\nVisualization saved to: {output_file}")
    
    # Also save a minimal standalone version
    output_file_minimal = "flysight_sphere_minimal.html"
    fig.write_html(output_file_minimal, 
                   include_plotlyjs='cdn',
                   config={'displayModeBar': False},  # Hide toolbar for cleaner look
                   div_id="flysight-sphere")
    print(f"Minimal version saved to: {output_file_minimal}")
    
    # Try to open in browser
    import webbrowser
    import os
    file_path = os.path.abspath(output_file)
    webbrowser.open(f"file://{file_path}")
    
    print("\nVisualization should open in your browser! You can:")
    print("- Rotate the sphere by clicking and dragging")
    print("- Zoom with scroll wheel")
    print("- Hover over points to see details")
    print("- The color represents time progression")
    
    # Save the data as JSON for web integration
    import json
    
    # Extract the plot data
    plot_data = {
        'data': fig.to_dict()['data'],
        'layout': fig.to_dict()['layout']
    }
    
    json_file = "flysight_sphere_data.json"
    with open(json_file, 'w') as f:
        json.dump(plot_data, f)
    print(f"\nPlot data saved to: {json_file}")
    
    # Create a sample HTML template for embedding
    html_template = '''<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        #flysight-sphere { width: 100%; height: 700px; }
    </style>
</head>
<body>
    <div id="flysight-sphere"></div>
    <script>
        // Load the data via fetch or embed directly
        fetch('flysight_sphere_data.json')
            .then(response => response.json())
            .then(plotData => {
                Plotly.newPlot('flysight-sphere', plotData.data, plotData.layout);
            });
    </script>
</body>
</html>'''
    
    with open("flysight_sphere_template.html", 'w') as f:
        f.write(html_template)
    print("HTML template saved to: flysight_sphere_template.html")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python flysight_sphere.py SENSOR.CSV")
        sys.exit(1)
    
    main(sys.argv[1])

