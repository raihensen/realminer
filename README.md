# RealMiner

*Originally: PADS x Celonis OCPM*

A powerful tool for analyzing and visualizing object-centric process data.
This app has been developed during the lab *PADS x Celonis*, offered by the [Chair of Process and Data Science (PADS)](https://pads.rwth-aachen.de) at RWTH Aachen University, in cooperation with [celonis](https://celonis.com), in summer semester 2023.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Examples](#examples)
  - Example 1: Analyzing Purchase Order Process
  - Example 2: Analyzing a P2P process
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

## Usage
1. Prepare your process data in the required [.`jsonocel`](https://ocel-standard.org/) format
2. Change directory to the src folder:
    ```bash
    cd src\
    ```
1. Run the application:
    ```bash
    python main.py
    ```
2. Import your event log, and follow the instructions appearing on screen.

## Features
The app solves different problems in the domain of Object-centric Process Mining, including:

- Importing object-centric event logs (`.jsonocel`)
- Filtering by object types and activity names
- Discovering object-centric petri nets
- Variants and trends analysis : Computing cases (*process executions*) and variants, including displaying them as an event-object graph [^cases_and_variants]
- Computing object-centric KPIs such as pooling or lagging time [^opera], allowing for performance analysis and bottleneck identification
- Exporting analysis results in various formats

## Examples
The following examples make use of publicly available event logs from https://ocel-standard.org

### Example 1: Analyzing a recruiting processs
1. Download and extract the [recruiting dataset](https://ocel-standard.org/1.0/recruiting.jsonocel.zip)
2. Run the application:
    ```bash
    python main.py
    ``` 
3. Filter the object types and activity names as needed
4. Discover an object-centric petri net (*Petri Net* tab)
5. Generate heatmaps for lagging and pooling time (*Heatmap* tab) and identify potential bottlenecks
6. Export these heatmaps pressing `Ctrl+S` or using the *Export* button

### Example 2: Analyzing a P2P process
1. Download the [p2p dataset](https://ocel-standard.org/1.0/recruiting.jsonocel.zip)
1. Add the following lines as a new field inside the JSON root node (copy after line 1):
	```json
	"ocel:global-log": {
		"ocel:attribute-names": [],
		"ocel:object-types": [
			"PURCHORD",
			"INVOICE",
			"PURCHREQ",
			"MATERIAL",
			"GDSRCPT"
		],
		"ocel:version": [
			"1.0"
		],
		"ocel:ordering": [
			"timestamp"
		]
	},
	```
1. Run the application:
    ```bash
    python main.py
    ``` 
1. Filter the object types and activity names as needed
1. Discover the object-centric variants (*Variant Explorer* tab)
1. Export the variant graphs using `Ctrl+S` or the *Export* button


## Acknowledgements
- Thanks to Bob Luppes, Alessandro Berti and Eduardo Goulart Rocha for supervising the course, giving us valuable feedback and a lot of help providing datasets while developing the app.
- Thanks to the developers of [`ocpa`](https://github.com/ocpm/ocpa) for inspiration, valuable insights and providing awesome tools for object-centric process mining.


## Repository Structure
This repository follows a Model-View-Controller (MVC) architecture
and is primarily built using Python with a tkinter-based frontend. It is designed to provide a process mining application with various widgets specifically developed for the app. The repository structure is organized as follows:

The MVC architecture separates the application into three major components: Model, View, and Controller. The Model represents the data and business logic, the View handles the user interface and visualization, and the Controller manages the interactions between the Model and View.

The project leverages Python's flexibility and rich ecosystem of libraries to provide a powerful process mining application. The custom-developed widgets offer additional functionality and enhanced user experience within the app.

Feel free to explore the individual directories for more detailed information about each component.


## References

[^opera]: Gyunam Park, Jan Niklas Adams, Wil. M. P. van der Aalst (2022). OPerA: Object-Centric Performance Analysis, [(arXiv:2204.10662)](https://arxiv.org/abs/2204.10662).
[^cases_and_variants]: Jan Niklas Adams, Daniel Schuster, Seth Schmitz, Günther Schuh, Wil M.P. van der Aalst (2022). Defining Cases and Variants for Object-Centric Event Data, Defining Cases and Variants for Object-Centric Event Data [(arXiv:2208.03235)](https://arxiv.org/abs/2208.03235).
