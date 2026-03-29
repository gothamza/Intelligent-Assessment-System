from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import os

def load_quality_classifier(model_path: str = "models/camembert_quality_classifier", binary: bool = False):
    """
    Loads the fine-tuned CamemBERT model and tokenizer for answer quality classification.

    Args:
        model_path (str): Path to the saved model directory.
        binary (bool): If True, loads binary classifier (2 classes), else 3-class classifier.

    Returns:
        A transformers pipeline for text classification.
    """
    try:
        # Try loading with use_fast=False to avoid SentencePiece conversion issues
        tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        
        # Set label mappings based on model type
        if binary:
            # Binary classification: 0=Correct, 1=Incorrect (includes partially correct)
            model.config.id2label = {0: "Correcte", 1: "Incorrecte"}
            model.config.label2id = {"Correcte": 0, "Incorrecte": 1}
        else:
            # 3-class classification: 0=Correct, 1=Partielle, 2=Incorrect
            model.config.id2label = {0: "Correcte", 1: "Partielle", 2: "Incorrecte"}
            model.config.label2id = {"Correcte": 0, "Partielle": 1, "Incorrecte": 2}
        
        classifier = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer
        )
        return classifier
    except Exception as e:
        print(f"Erreur lors du chargement du modèle: {e}")
        # Fallback: try loading from the base CamemBERT model
        try:
            print("Tentative de chargement avec le modèle de base CamemBERT...")
            tokenizer = AutoTokenizer.from_pretrained("camembert-base", use_fast=False)
            num_labels = 2 if binary else 3
            model = AutoModelForSequenceClassification.from_pretrained("camembert-base", num_labels=num_labels)
            
            if binary:
                model.config.id2label = {0: "Correcte", 1: "Incorrecte"}
            else:
                model.config.id2label = {0: "Correcte", 1: "Partielle", 2: "Incorrecte"}
            
            classifier = pipeline(
                "text-classification",
                model=model,
                tokenizer=tokenizer
            )
            print("⚠️ Modèle de base chargé - les prédictions peuvent être moins précises")
            return classifier
        except Exception as e2:
            print(f"Erreur critique: Impossible de charger le modèle: {e2}")
            return None

def classify_answer(classifier, question: str, answer: str):
    """
    Classifies the quality of a student's answer using the loaded model.

    Args:
        classifier: The classification pipeline.
        question (str): The question text.
        answer (str): The student's answer text.

    Returns:
        A dictionary with the predicted label and score.
    """
    # CamemBERT uses <s> and </s> as special tokens for sequence separation
    text_to_classify = f"{question} </s> {answer}"
    return classifier(text_to_classify)[0]