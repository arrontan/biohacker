[comment]: < ![logo](URL from githubassets) >
# Biohacker
*"Just start here"*

As of 2025, there exists more than 20,000 bioinformatic tools, with more tools coming out each year.

These programs are written by biologists, and are often not user-friendly, often with prohibitively complex installations and implementations, taking the user through multiple file formats. Combined with a culture of "publish and forget", many programs out there only cater to the specific needs of the research group. With a lack support, documentation, and given such a wide range of programs, hard-coding and integrating them all manually is unrealistic and unscaleable.

Biohacker addresses this issue by leveraging the available literature to provide a convenient frontend agent, together with a scalable backend suite of agents. Together we get you through the myriad of programs whilst maintaining flexibility, reliability, and reproducibility in your analyses. 

## TODO
- src 
    - Madhu: 
        - [ ] data_cleaner
        - [ ] refine lit assistant prompt 
        - [ ] add scraper tools to add on to knowledge base
        - [x] add pubmed to test knowledge base
        - [x] setup faiss knowledge base
    - Arron: 
        - [ ] make UI, fix enter bug
        - [ ] make it usable on windows (maybe docker?)
        - [ ] make output stream async
        - [ ] split software_assistant, see if it runs faster
        - [ ] try agent_graph/diagram, handoff_to_user, batch, browser, use_computer, swarm,
        - [x] get all test cases working
        - [ ] get the literature agent to fact check the output of code agent
        - [x] fix software agent by breaking it up and making workflow explicit
        - [x] setup overall src structure
- req.txt file
- streamlit/react webapp
- 10 slides and 5min video
- logo

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
- Store user's input in memory
- Search with images
- Interactive workflow map with tool integration
- Sharing and collaboration for workflows
- Benchmarking against existing methods
- Download software directly to local machine

**Current software tested:**
- Bioconductor (Suite of data analysis and visualisation packages for different -omics data)
- GROMACS (Molecular simulation)
- ImageJ (Image analysis)
- PyMOL (Molecular visualisation)

**Other bioinformatic tool databases that may be helpful:**
- [Nature Methods](https://www.nature.com/nmeth/)
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/)
- [GenBank](https://www.ncbi.nlm.nih.gov/genbank/)
- [PROSITE](https://prosite.expasy.org/)
- [PubChem](https://pubchem.ncbi.nlm.nih.gov/)
- [bio.tools](https://bio.tools/)
- [NAR Database](https://www.oxfordjournals.org/nar/database/c/)
- [OBRC](https://www.hsls.pitt.edu/obrc/)
- [StartBioInfo](https://startbioinfo.org/)

---
## Installation

### Setup

> **Optionally:** Create a virtual environment to store your dependencies (activated by default with .envrc)
```bash
python -m venv .venv

# macOS / Linux: source .venv/bin/activate
# Windows (CMD): .venv\Scripts\activate.bat
# Windows (PowerShell): .venv\Scripts\Activate.ps1
```

1. Clone the repository at https://github.com/arrontan/biohacker/
```bash
git clone https://github.com/arrontan/biohacker/
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Enable Strands Console Mode (enabled by default in the .venv activation script) and run the agent.py file
```bash
export STRANDS_TOOL_CONSOLE_MODE=enabled
python3 biohacker/agent.py
```
We are currently working on a friendlier web-app, as well as a downloadable application, so do stay tuned!

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


## License
This project is licensed under the [Apache 2.0](https://github.com/arrontan/biohacker/blob/main/LICENSE) license.

## Contributing 
Contributors are welcome! Please fork this repo and create a pull request