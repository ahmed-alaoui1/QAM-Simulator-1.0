# QAM-Simulator-1.0
Overview

QAM 2.0 is a Python-based tool for visualizing Quadrature Amplitude Modulation (QAM) constellation diagrams with advanced features like noise addition, SNR and BNR calculations, and symbol phase analysis. It generates visualizations and data tables for various QAM sizes, making it ideal for telecommunications research, education, and signal analysis.
Features

    Flexible QAM Size Support: Generate constellations for QAM sizes ranging from 4 to 4096.
    Noise Simulation: Add amplitude or phase noise with customizable intensity.
    Performance Metrics: Calculate and evaluate Signal-to-Noise Ratio (SNR) and Bit-to-Noise Ratio (BNR).
    Visual & Tabular Outputs:
        Constellation diagrams annotated with symbol indices and optional noise/exclusion points.
        Symbol energy and phase data exported as organized tables.
    Automated Export: Save results as PDF files directly to your desktop for easy access.

Technologies Used

    Python
    NumPy: Efficient numerical operations.
    Matplotlib: High-quality data visualization.
    OS Module: Desktop file handling.

How to Use

    Run the Script:
    Input a valid QAM size (e.g., 16, 64, 256).
    Choose Noise Options:
        Decide whether to add noise.
        Specify the noise type (amplitude/phase) and intensity.
    View Outputs:
        Constellation diagram PDF.
        Symbol table PDF.
    Evaluate Metrics:
        Review SNR and BNR values in the terminal output.

Applications

    Academic research in telecommunications.
    Educational tool for signal processing.
    Testing and analysis for communication systems.

Future Enhancements

    Add support for custom constellation designs.
    Integrate BER (Bit Error Rate) calculations.
    Extend noise models to include non-Gaussian noise types.
