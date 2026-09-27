# AI-Assisted Cybersecurity Incident Intelligence System

This repository contains the implementation of my CM3020 Final Project at the University of London.

The project investigates how multiple AI and machine-learning components can be orchestrated to analyse different forms of cybersecurity evidence and generate structured incident intelligence.

## System overview

The system supports three evidence-analysis pathways:

- **Email analysis** – uses a pre-trained DistilBERT model to classify email content as phishing or legitimate.
- **Screenshot analysis** – uses EasyOCR to extract text from screenshots before passing the extracted text to the phishing classifier.
- **Security-log analysis** – uses TF-IDF event-sequence features and a Logistic Regression classifier to identify normal or anomalous HDFS log sequences.

The outputs from these components are converted into a common `EvidenceResult` representation and combined by an `IncidentOrchestrator`.

The resulting structured incident context is supplied to a locally executed **Llama 3.2 1B** model through Ollama, which generates an incident intelligence report containing:

- Incident summary
- Evidence description
- Severity assessment
- Recommended investigation actions
- Limitations and uncertainty

A Streamlit interface allows individual or multiple evidence types to be analysed within the same workflow.

## Project structure

```text
├── src/             # Core analysis and orchestration components
├── scripts/         # Data processing, training and evaluation scripts
├── tests/           # Automated tests
├── data/            # Evaluation/sample data where included
├── models/          # Trained log-analysis model files
├── results/         # Evaluation results
├── app.py           # Streamlit application
├── requirements.txt # Python dependencies
└── README.md
```

## Requirements

The project requires Python and the dependencies listed in `requirements.txt`.

The LLM report-generation component also requires Ollama and the `llama3.2:1b` model.

## How to run

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install the Llama model using Ollama

```bash
ollama pull llama3.2:1b
```

### 3. Start Ollama

```bash
ollama serve
```

### 4. Start the Streamlit application

```bash
streamlit run app.py
```

Open the local Streamlit URL displayed in the terminal.

## Using the application

The interface supports:

1. Email text
2. Screenshot evidence
3. Security-log evidence

Evidence types can be analysed individually or combined within a single incident analysis.

After analysis, the system displays the individual component results, the overall severity assessment and the generated incident intelligence report.

## Models and technologies

The main technologies used are:

- Python
- Streamlit
- DistilBERT / Hugging Face Transformers
- EasyOCR
- scikit-learn
- TF-IDF
- Logistic Regression
- Ollama
- Llama 3.2 1B

A rule-based phishing detector and Isolation Forest implementation are also included as baseline approaches used during evaluation.

## Datasets

The project uses publicly available datasets for evaluation:

- `zefang-liu/phishing-email-dataset` for phishing-classification evaluation.
- HDFS log data from LogHub for security-log analysis.
- A small manually prepared screenshot set for OCR evaluation.

Large public datasets are not necessarily included directly in this repository.

## Evaluation

The project evaluates the individual analytical components as well as the complete orchestration workflow.

The evaluation includes:

- Phishing classification using accuracy, precision, recall and F1-score
- Comparison with a rule-based phishing baseline
- OCR evaluation using Character Error Rate (CER) and Word Error Rate (WER)
- Comparison of Isolation Forest and supervised Logistic Regression for HDFS log analysis
- Functional end-to-end testing of individual and combined evidence pathways

## Limitations

This system is a research prototype and is not intended to replace professional cybersecurity tools or human analyst judgement.

Model classifications, OCR extraction and LLM-generated reports may contain errors. The generated incident intelligence should therefore be treated as decision-support information rather than an autonomous cybersecurity verdict.

## Academic project

Developed for:

**CM3020 Final Project**  
**University of London**

Project template:

**Artificial Intelligence – Project Idea 4.1: Orchestrating AI Models to Achieve a Goal**