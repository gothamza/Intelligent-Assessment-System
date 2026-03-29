# French Text Summarization Project

## Project Overview

This project implements and compares multiple Transformer-based models for French text summarization, with a focus on educational applications. The project uses MLSUM-FR as the primary training dataset and includes support for educational domain adaptation with ALECTOR Corpus.

## Project Structure

```
abdo/
├── notebooks/
│   ├── 01_data_preparation.ipynb      # Data loading and preprocessing
│   ├── 02_mt5_small_training.ipynb    # mT5-small model training
│   ├── 03_mt5_base_training.ipynb    # mT5-base model training
│   ├── 04_bart_training.ipynb        # BART model training
│   ├── 05_model_evaluation.ipynb     # Model evaluation and metrics
│   └── 06_model_comparison.ipynb     # Comparative analysis
├── src/
│   ├── models/                        # Model wrappers and utilities
│   ├── utils/                         # Helper functions
│   └── config.py                     # Configuration settings
├── app/
│   ├── streamlit_app.py              # Main Streamlit application
│   ├── pages/                         # Streamlit pages
│   └── utils/                         # Visualization utilities
├── data/                              # Preprocessed datasets
├── models/                            # Trained model checkpoints
└── requirements.txt                   # Python dependencies
```

## Installation

1. Clone the repository or navigate to the project directory
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Data Preparation

Run the data preparation notebook first:

```bash
jupyter notebook notebooks/01_data_preparation.ipynb
```

This notebook will:
- Load MLSUM-FR dataset
- Load ALECTOR Corpus (if available)
- Preprocess data for different models
- Create train/validation/test splits
- Save preprocessed datasets

### 2. Model Training

Train models sequentially:

1. **mT5-small**: `notebooks/02_mt5_small_training.ipynb`
2. **mT5-base**: `notebooks/03_mt5_base_training.ipynb`
3. **BART**: `notebooks/04_bart_training.ipynb`

Each training notebook includes:
- Model initialization
- Training configuration
- Training loop with progress tracking
- Model checkpointing

### 3. Evaluation

Evaluate all trained models:

```bash
jupyter notebook notebooks/05_model_evaluation.ipynb
```

This generates:
- ROUGE scores (ROUGE-1, ROUGE-2, ROUGE-L)
- BLEU scores
- BERTScore metrics
- Qualitative examples

### 4. Model Comparison

Compare models comprehensively:

```bash
jupyter notebook notebooks/06_model_comparison.ipynb
```

### 5. Streamlit Application

Run the interactive Streamlit app:

```bash
streamlit run app/streamlit_app.py
```

Features:
- Text summarization with multiple models
- Side-by-side model comparison
- Performance metrics visualization
- Interactive parameter tuning

## Datasets

### MLSUM-FR
- **Source**: Hugging Face Datasets (`mlsum`, French version)
- **Size**: ~425,000 article-summary pairs
- **Domain**: French news articles
- **Usage**: Primary training dataset

### ALECTOR Corpus
- **Source**: GERAD research paper
- **Size**: 79 educational texts
- **Domain**: French educational content for children (ages 7-9)
- **Usage**: Educational domain adaptation and evaluation

## Models

### mT5-small
- **Model**: `google/mt5-small`
- **Parameters**: ~300M
- **Memory**: ~2-4GB VRAM
- **Best for**: Quick experiments, Colab free tier

### mT5-base
- **Model**: `google/mt5-base`
- **Parameters**: ~580M
- **Memory**: ~4-6GB VRAM
- **Best for**: Balanced performance and efficiency

### BART
- **Model**: `facebook/mbart-large-cc25` or `facebook/bart-large`
- **Parameters**: ~400M-600M
- **Memory**: ~4-8GB VRAM
- **Best for**: High-quality summaries

## Evaluation Metrics

- **ROUGE-1, ROUGE-2, ROUGE-L**: N-gram overlap metrics
- **BLEU**: Translation quality metric
- **BERTScore**: Semantic similarity using BERT embeddings

## Requirements

- Python 3.8+
- CUDA-capable GPU (recommended) or Google Colab
- 8GB+ RAM
- 20GB+ disk space (for datasets and models)

## Google Colab Setup

For training on Google Colab free GPU:

1. Upload notebooks to Google Colab
2. Mount Google Drive (for saving models):
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```
3. Adjust paths in notebooks to save to Drive
4. Run training notebooks (may take several hours)

## Results

Results will be saved in:
- `models/`: Trained model checkpoints
- `data/`: Evaluation results (CSV/JSON)
- Notebook outputs: Visualizations and metrics

## Future Work

- Integration of ALECTOR dataset for domain adaptation
- Fine-tuning on educational content
- Question generation capabilities
- Multi-task learning (summarization + question generation)

## License

This project is for academic/research purposes.

## Contact

For questions or issues, please refer to the project documentation or contact the project supervisor.

