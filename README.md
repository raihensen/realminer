# PADS x Celonis OCPM

A powerful tool for analyzing and visualizing process data.
This app has been developed during the lab *PADS x Celonis* in summer semester 2023.

## Table of Contents
- [PADS x Celonis OCPM](#pads-x-celonis-ocpm)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Features](#features)
  - [Examples](#examples)
    - [Example 1: Analyzing Purchase Order Process](#example-1-analyzing-purchase-order-process)
  - [License](#license)
  - [Acknowledgements](#acknowledgements)
  - [Repository Structure](#repository-structure)
  - [References](#references)

## Installation
1. Clone the repository:
    ```bash
    git clone git@git.rwth-aachen.de:rhensen/pads-x-celonis-ocpm.git
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. [Optional] Set up the database and configure connection settings in `src\preferences.json'.

## Usage
1. Prepare your process data in the required format.
2. Change directory to the Src folder:
    ```bash
    cd src\
    ```
1. Run the application:
    ```bash
    python main.py
    ```
2. Upload Your Event Log, and follow the Instructions appearing on screen.
   
## Features
The app solves different problems in the domain of Object-centric Process Mining, including:

- Importing object-centric event logs (`.jsonocel` or `.csv`)
- Filtering by object types and activity names
- Discovering object-centric petri nets
- Variants and trends analysis : Computing cases (*process executions*) and variants, including displaying them as an event-object graph [^cases_and_variants]
- Computing object-centric KPIs such as pooling or lagging time [^opera]
- Interactive process visualization
- Performance analysis and bottleneck identification
- Process conformance checking
- Exporting analysis results in various formats

## Examples
### Example 1: Analyzing Purchase Order Process
1. Prepare the purchase order data in jsonocel format.
2. Run the application:
    ```bash
    python main.py
    ``` 
4. Analyze the process variants, identify trends, and assess performance metrics.

## License
This project is licensed under the Celonis / RWTH-Aachen Licence.

## Acknowledgements
- Thanks to the [`OCPA`](https://github.com/ocpm/ocpa/blob/main/README.md) for inspiration and valuable insights.
## Repository Structure

This repository follows a Model-View-Controller (MVC) architecture and is primarily built using Python. It is designed to provide a process mining application with various widgets specifically developed for the app. The repository structure is organized as follows:

- `data/`: Holds the sample data used for testing and demonstration.
- `research/`: Includes documentation files and current research.
- `tests/` : Contains unit tests and test scripts.
- `drafts/` : Contains .ipynb notebooks to test the different functionalities. 
- `logs/` : Stores the logs accumelated throughtout the execution of the app.
- `src/`: Contains the Implementation of the MVC architecture and the widgets/ view-components mentioned above.
- `src/main.py`: Contains the "entry point" for the application's execution.

The MVC architecture separates the application into three major components: Model, View, and Controller. The Model represents the data and business logic, the View handles the user interface and visualization, and the Controller manages the interactions between the Model and View.

This project leverages Python's flexibility and rich ecosystem of libraries to provide a powerful process mining application. The custom-developed widgets offer additional functionality and enhanced user experience within the app.

Feel free to explore the individual directories for more detailed information about each component.

## References

[^opera]: Gyunam Park, Jan Niklas Adams, Wil. M. P. van der Aalst (2022). OPerA: Object-Centric Performance Analysis, arXiv:2204.10662.
  
[^cases_and_variants]: Jan Niklas Adams, Daniel Schuster, Seth Schmitz, Günther Schuh, Wil M.P. van der Aalst (2022). Defining Cases and Variants for Object-Centric Event Data, Defining Cases and Variants for Object-Centric Event Data, arXiv:2208.03235.