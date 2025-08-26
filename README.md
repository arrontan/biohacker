[comment]: < ![logo](URL from githubassets) >
# Biohacker
*"Just start here"*

As of 2025, there exists more than 20,000 bioinformatic tools, with more tools coming out each year.

These programs are written by biologists, and are often not user-friendly, often with prohibitively complex installations and implementations, taking the user through multiple file formats. Combined with a culture of "publish and forget", many programs out there only cater to the specific needs of the research group. With a lack of support, documentation, and given such a wide range of programs, hard-coding and integrating them all manually is unrealistic and unscaleable.

Biohacker addresses this issue by leveraging the available literature to provide a convenient frontend agent, together with a scalable backend suite of agents. Together we get you through the myriad of programs whilst maintaining flexibility, reliability, and reproducibility in your analyses. 

## TODO
- logo
- src
- req.txt file
- streamlit/react webapp
- 10 slides and 5min video

## Features
- **Tool integration**: 
<br>Get an overview of the tools suitable for your data, ask Biohacker about each tool's functionality, and seamlessly add them into your workflow
<br>
- **Real-time execution and monitoring**: 
<br>Let Biohacker run your workflows automatically, whilst keeping you in the loop. Manually set parameters if needed
<br>
- **Reproducibility**: 
<br>Keep a log of your workflow, execute it using different data sets to ensure reproducibility

<br>

**Upcoming features:**
- Interactive workflow map with tool integration
- Sharing and collaboration for workflows
- Benchmarking against existing methods

**Current agents:**
- Bioconductor (Suite of data analysis and visualisation packages for different -omics data)
- GROMACS (Molecular simulation)
- ImageJ (Image analysis)

**Upcoming agents:**
- Samtools (SNV identification in WGS data)
- BEDTools (ChIPseq data)
- GATK, DNAnexus, Illumina (Variant discovery in sequencing data)
- Autodock, Vina (Molecular docking simulations)
- And many more!


**Other bioinformatic tool databases that may be helpful:**
- [Bio tools](bio.tools)
- [NAR Database](https://www.oxfordjournals.org/nar/database/c/)
- [OBRC](https://www.hsls.pitt.edu/obrc/)
- [Startbioinfo](startbioinfo.org)

---
## Installation

### Prerequisites
Make sure you have the following installed:
- Python 3
- pip

### Setup

1. Clone the repository at https://github.com/arrontan/biohacker/
```bash
git clone https://github.com/arrontan/biohacker/
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

> **Note:** Ensure that you have the required API keys configured in your environment before using the tool.

#### Linux/MacOS (bash)
```bash
export AWS_ACCESS_KEY_ID="your_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key"
export AWS_BEARER_TOKEN_BEDROCK="your_bedrock_api_key"
```

#### Windows (PowerShell)
```powershell
$env:AWS_ACCESS_KEY_ID="your_access_key_id"
$env:AWS_SECRET_ACCESS_KEY="your_secret_access_key"
$env:AWS_BEARER_TOKEN_BEDROCK="your_bedrock_api_key"
```

#### Windows (cmd)
```cmd
set AWS_ACCESS_KEY_ID=your_access_key_id
set AWS_SECRET_ACCESS_KEY=your_secret_access_key
set AWS_SESSION_TOKEN=your_session_token # Optional
```
## Usage
To start using the project, run the following command in the terminal:
```bash
python agent.py
```
We are currently working on a friendlier web-app, as well as a downloadable application, so do stay tuned!

## License
This project is licensed under the [Apache 2.0](https://github.com/arrontan/biohacker/blob/main/LICENSE) license.

## Contributing 
WIP

## References
WIP
