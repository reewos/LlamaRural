# LlamaRural - Coverage Analysis in Peru

LlamaRural is a web application developed using Streamlit that allows users to analyze mobile service coverage in rural areas of Peru. The application provides insights into telecommunications infrastructure using official data from major mobile operators in the country.

## Table of Contents

- [Problem](#problem)
- [Solution](#solution)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Future Work](#future-work)
- [Contributing](#contributing)
- [License](#license)

## Problem

Rural areas in Peru face significant limitations in mobile coverage, affecting access to essential telecommunications services. The distribution of antennas is uneven across different operators, which can lead to connectivity issues. Without coverage, there is also a lack of internet access, making it difficult for communities to access vital information on first aid, education, and health.

## Solution

LlamaRural aims to address these issues by providing:

- **Coverage Analysis**: Interactive maps displaying coverage by operator and technology (2G, 3G, 4G, 5G) based on user-selected locations.
- **Optimus Llama Chatbot**: An interactive chatbot that assists users with real-time inquiries related to mobile coverage and connectivity issues.

## Features

- Enter geographic coordinates to visualize nearby base stations within a customizable radius.
- Interactive maps with operator clusters and statistical graphs.
- Detailed metrics on technology availability, connection speeds, and services (voice, SMS, MMS).
- Chatbot interaction for real-time assistance and troubleshooting.

## Technology Stack

- **Programming Language**: Python
- **Frontend Framework**: Streamlit
- **Language Models**: 
  - Llama 3.1 405B (for complex tasks)
  - Llama 3.2 3B (for general tasks)
- **Libraries**: 
  - Folium (for interactive maps)

## Installation

To run LlamaRural locally, follow these steps:

1. Clone this repository:
   ```bash
   https://github.com/reewos/LlamaRural.git
   cd LlamaRural
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables. Create a `.env` file in the root directory with your API key:
   ```plaintext
   AIML_API_KEY=your_api_key_here
   ```

4. Run the application:
   ```bash
   streamlit run Home.py
   ```

## Usage

1. Open your web browser and go to `http://localhost:8501`.
2. Enter geographic coordinates to analyze coverage in your desired location.
3. Interact with the *Optimus Llama Chatbot* for assistance.

## Future Work

- Develop a mobile app to enhance accessibility.
- Implement the Llama 3.2 3B model for offline basic functions.
- Add a no-coverage alert system to report connectivity issues to regulatory authorities.

## Resources

- [Mobile Service Coverage by Operator Company](https://www.datosabiertos.gob.pe/dataset/cobertura-de-servicio-m%C3%B3vil-por-empresa-operadora)

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any changes or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---