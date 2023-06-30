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
 - git clone git@git.rwth-aachen.de:rhensen/pads-x-celonis-ocpm.git
2. Install the required dependencies:
   - pip install -r requirements.txt
3. [Optional] Set up the database and configure connection settings in `src\preferences.json'.

## Usage
1. Prepare your process data in the required format.
2. Change directory to the Src folder:
 - cd src\
3. Run the application:
 - python main.py
4. Upload Your Event Log, and follow the Instructions appearing on screen.
   
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
    - python main.py
3. Analyze the process variants, identify trends, and assess performance metrics.

## License
This project is licensed under the Celonis / RWTH-Aachen Licence.

## Acknowledgements
- Thanks to the [`OCPA`](https://github.com/ocpm/ocpa/blob/main/README.md) for inspiration and valuable insights.
## Repository Structure

*TODO*

## References

[^opera]: Gyunam Park, Jan Niklas Adams, Wil. M. P. van der Aalst (2022). OPerA: Object-Centric Performance Analysis, arXiv:2204.10662.
 - You can download the research paper [here](instructions\OPerA Paper Review.pdf).
  
[^cases_and_variants]: Jan Niklas Adams, Daniel Schuster, Seth Schmitz, Günther Schuh, Wil M.P. van der Aalst (2022). Defining Cases and Variants for Object-Centric Event Data, Defining Cases and Variants for Object-Centric Event Data, arXiv:2208.03235.