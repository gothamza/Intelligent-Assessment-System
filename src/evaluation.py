import evaluate
import numpy as np

def calculate_feedback_metrics(predictions, references):
    """
    Calculates and prints BLEU, ROUGE, and BERTScore for generated feedback.

    Args:
        predictions (list of str): The list of AI-generated feedback texts.
        references (list of str): The list of human-written reference texts.
    """
    if not all(isinstance(p, str) for p in predictions) or not all(isinstance(r, str) for r in references):
        print("Error: All items in predictions and references must be strings.")
        return

    if not predictions or not references or len(predictions) != len(references):
        print("Error: Predictions and references lists must be non-empty and of the same length.")
        return

    print("--- Loading Evaluation Metrics ---")
    bleu_metric = evaluate.load("bleu")
    rouge_metric = evaluate.load("rouge")
    bertscore_metric = evaluate.load("bertscore")
    
    print("--- Computing Scores ---")
    bleu_results = bleu_metric.compute(predictions=predictions, references=references)
    rouge_results = rouge_metric.compute(predictions=predictions, references=references)
    bertscore_results = bertscore_metric.compute(predictions=predictions, references=references, lang="fr")
    
    print("\n--- Feedback Quality Evaluation Results ---")
    print(f"\nEvaluated {len(predictions)} samples.")
    
    print(f"\nBLEU Score: {bleu_results['bleu']:.4f}")
    print(f"ROUGE-L Score: {rouge_results['rougeL']:.4f}")
    
    avg_f1 = np.mean(bertscore_results['f1'])
    print(f"BERTScore (F1): {avg_f1:.4f}")