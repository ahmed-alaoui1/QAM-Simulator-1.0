import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
import math

def generate_qam_constellation(M, exclude_points):
    """
    Generates the QAM constellation points.
      M: The size of the QAM constellation.
      exclude_points: The number of points to exclude from the corners.
    """
    side_len = int(np.sqrt(M))

    # Adjust side length for specific cases to ensure correct constellation shape
    if M == 32:
        side_len_x = 6
        side_len_y = 6
    elif M == 128:
        side_len_x = 12
        side_len_y = 12
    elif M == 512:
        side_len_x = 24
        side_len_y = 24
    elif M == 2048:
        side_len_x = 46
        side_len_y = 46
    else:
        side_len_x = side_len
        side_len_y = side_len

    # Generate all possible points within the grid
    points = np.array([(x, y) for x in range(-side_len_x + 1, side_len_x, 2)
                       for y in range(-side_len_y + 1, side_len_y, 2)])

    # Remove any point at the origin (0, 0)
    points = points[~np.any(points == 0, axis=1)]

    excluded_points = []
    if exclude_points > 0:
        # Calculate the size of the square of points to exclude from each corner
        square_size = int(np.sqrt(exclude_points // 4))

        # Calculate the coordinates of the points to be excluded
        for i in range(square_size):
            for j in range(square_size):
                excluded_points.extend([
                    (side_len_x - 1 - 2 * i, side_len_y - 1 - 2 * j),
                    (-side_len_x + 1 + 2 * i, side_len_y - 1 - 2 * j),
                    (side_len_x - 1 - 2 * i, -side_len_y + 1 + 2 * j),
                    (-side_len_x + 1 + 2 * i, -side_len_y + 1 + 2 * j)
                ])
        excluded_points = np.array(excluded_points)

        # Remove the excluded points from the list of all points
        mask = np.ones(len(points), dtype=bool)
        for excluded_point in excluded_points:
            mask &= ~np.all(points == excluded_point, axis=1)
        points = points[mask]

    return points, excluded_points

def add_noise(points, intensity, noise_scope):
    """
    Adds white noise points around the original constellation points.
      points: Array of constellation points.
      intensity: Intensity of the noise.
    """
    new_noise_points = []
    noise_scaling_factor = 0.25  # Smaller scaling factor to keep noise points close

    for x, y in points:
        if noise_scope == 'amplitude':
            offsets = np.random.normal(0, intensity, size=(10, 2)) * noise_scaling_factor
            new_noise_points.extend([(x + dx, y + dy) for dx, dy in offsets])

        elif noise_scope == 'phase':
            magnitude = np.sqrt(x ** 2 + y ** 2)
            phase = np.arctan2(y, x)
            offsets = np.random.normal(0, intensity, size=10) * noise_scaling_factor
            new_noise_points.extend([(magnitude * np.cos(phase + dp), magnitude * np.sin(phase + dp))
                                      for dp in offsets])

    return np.array(new_noise_points)


def calculate_snr_bnr(points, noise_points):
    """
    Calculate Signal-to-Noise Ratio (SNR) and Bit-to-Noise Ratio (BNR).
    """
    signal_power = np.mean(np.sum(points ** 2, axis=1))

    # Reshape noise points to group by original points
    noise_points = noise_points.reshape(len(points), -1, 2)
    noise_power = np.mean(np.sum((noise_points - points[:, np.newaxis, :]) ** 2, axis=2))

    snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else np.inf
    bnr = snr / 2  # Assuming QAM, the BNR is typically half the SNR

    return snr, bnr

def evaluate_snr(snr):
    """
    Evaluates if the SNR value is good.
    """
    if snr >= 30:
        return "Excellent"
    elif snr >= 20:
        return "Good"
    elif snr >= 10:
        return "Fair"
    else:
        return "Poor"

def plot_qam_constellation(M, intensity=0, noise_scope=None):
    # Define the number of points to exclude for specific QAM sizes
    exclusions = {32: 4, 128: 16, 512: 64, 2048: 196}
    exclude_points = exclusions.get(M, 0)  # Get the exclusion count for the given M, default to 0

    # Generate the constellation points
    points, excluded_points = generate_qam_constellation(M, exclude_points)

    # Generate noise points if specified
    noise_points = None
    if intensity > 0 and noise_scope:
        noise_points = add_noise(points, intensity,noise_scope)

    # Calculate SNR and BNR
    if noise_points is not None:
        snr, bnr = calculate_snr_bnr(points, noise_points)
        snr_evaluation = evaluate_snr(snr)
        print(f"SNR: {snr:.2f} dB ({snr_evaluation})")
        print(f"BNR: {bnr:.2f} dB")

    # Calculate energy and phase of each symbol
    energy = np.sqrt(points[:, 0] ** 2 + points[:, 1] ** 2)
    phase = np.arctan2(points[:, 1], points[:, 0])
    phase = (phase + 2 * np.pi) % (2 * np.pi)  # Ensure phase is within [0, 2pi)
    phase_pi = phase / np.pi

    # Sort points by phase for the table
    sort_indices = np.argsort(phase)
    points = points[sort_indices]
    energy = energy[sort_indices]
    phase_pi = phase_pi[sort_indices]

    # Assign symbol numbers starting from 0
    symbol_numbers = np.arange(0, len(points))

    # --- Constellation Plot ---
    plt.figure(figsize=(8, 6))  # Set figure size
    for symbol, (x, y) in zip(symbol_numbers, points):
        plt.text(x, y - 0.4, str(symbol), fontsize=6, ha='center', va='center', color='blue')
    plt.scatter(points[:, 0], points[:, 1], color='blue', label='Included Symbols')  # Plot included symbols
    if noise_points is not None:
        plt.scatter(noise_points[:, 0], noise_points[:, 1], color='#FF4500', alpha=0.5, s=10, label='Noise Points')  # Solar orange and smaller size
    if len(excluded_points) > 0:
        plt.scatter(excluded_points[:, 0], excluded_points[:, 1], color='red', marker='x',
                    label='Excluded Symbols')  # Plot excluded symbols if any
    plt.grid(True)  # Add grid
    plt.title(f'{M}-QAM Constellation Diagram')  # Set title
    plt.xlabel('In-Phase (I)')  # Set x-axis label
    plt.ylabel('Quadrature (Q)')  # Set y-axis label
    plt.gca().set_aspect('equal', adjustable='box')  # Ensure equal aspect ratio
    plt.legend()  # Show legend

    # Set axis ticks
    max_val = np.max(np.abs(points)) + 2
    ticks = np.arange(-max_val, max_val + 1, 2)
    plt.xticks(ticks[ticks != 0])
    plt.yticks(ticks[ticks != 0])

    # Add axes lines
    plt.axhline(0, color='black', linewidth=1.2)
    plt.axvline(0, color='black', linewidth=1.2)

    # Save the plot to a PDF file on the desktop
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    pdf_filename = os.path.join(desktop_path, f'{M}-QAM_constellation.pdf')
    with PdfPages(pdf_filename) as pdf:
        pdf.savefig()
    plt.close()

    # --- Table Plot ---
    chunk_size = 20  # Number of rows per table page
    num_chunks = math.ceil(len(points) / chunk_size)  # Calculate the number of table pages

    # Save the table to a PDF file on the desktop
    table_pdf_filename = os.path.join(desktop_path, f'{M}-QAM_table.pdf')
    with PdfPages(table_pdf_filename) as pdf:
        for i in range(num_chunks):  # Iterate over the chunks to create multiple pages
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, len(points))
            fig_table = plt.figure(figsize=(8, 6))
            ax_table = fig_table.add_subplot(1, 1, 1)
            ax_table.axis('off')

            # Prepare table data
            table_data = [[num, q, i, f"{e:.2f}", f"{p:.2f}π"] for num, (q, i), e, p in
                          zip(symbol_numbers[start_idx:end_idx], points[start_idx:end_idx],
                              energy[start_idx:end_idx], phase_pi[start_idx:end_idx])]

            # Create the table
            table = ax_table.table(cellText=table_data,
                                   colLabels=["Symbol", "Q", "I", "Energy", "Phase (rad)"],
                                   loc="center", cellLoc="center", colWidths=[0.2, 0.2, 0.2, 0.2, 0.2])
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.2, 1.2)

            pdf.savefig(fig_table)  # Save the table to the PDF
            plt.close(fig_table)



M = int(input("Enter the size of QAM (4, 16, 32, 64, 128, 512, 1024, 2048, 4096): "))
valid_sizes = [4, 16, 32, 64, 128, 512, 1024, 2048, 4096]
if M in valid_sizes:
    noise_option = input("Do you want to add noise? (yes/no): ").strip().lower()
    if noise_option == 'yes':
        noise_scope = input("Do you want to add noise to amplitude or phase? (amplitude/phase): ").strip().lower()
        intensity = float(input("Enter noise intensity (e.g., 0.1 for low, 1 for high): "))
        print("Generating QAM constellation with noise. Exporting to PDF...")
        plot_qam_constellation(M, intensity, noise_scope)
    else:
        print("Generating QAM constellation without noise. Exporting to PDF...")
        plot_qam_constellation(M)
    print("PDF files generated successfully to your Desktop!")  # Confirmation message
else:
    print(f"Invalid QAM size. Please choose from: {valid_sizes}.")
