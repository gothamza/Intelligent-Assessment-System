# 🎯 Binary Classification Model Integration

## Overview

The binary CamemBERT model has been successfully integrated into the classification system, allowing for comparison between different classification approaches.

## Model Characteristics

### Binary Model (`camembert_binary_classifier`)
- **Classes:** 2 (Correct vs Incorrect)
- **Mapping:**
  - 0 = **Correcte** (Completely correct answers)
  - 1 = **Incorrecte** (Completely incorrect answers)
- **Training:** Fine-tuned on labeled dataset with **only labels 0 and 2**
  - Partial answers (label 1) are **excluded** from training
  - Result: Perfectly balanced 50/50 dataset

### 3-Class Model (`camembert_quality_classifier`)
- **Classes:** 3 (Correct, Partial, Incorrect)
- **Mapping:**
  - 0 = **Correcte** (Completely correct)
  - 1 = **Partielle** (Partially correct)
  - 2 = **Incorrecte** (Incorrect)

## Key Changes

### 1. Answer Quality Classifier (`src/Answer_Quality_Classifier.py`)
- Added `binary` parameter to `load_quality_classifier()` function
- Automatically sets label mappings based on model type
- Updated label2id and id2label configurations

### 2. Model Configuration (`models/camembert_binary_classifier/config.json`)
- Added `num_labels: 2`
- Added proper `id2label` and `label2id` mappings

### 3. Classification Page (`pages/2_🔍_Classification_de_Réponses.py`)
- Loads both binary and 3-class models simultaneously
- Added checkboxes to select which models to use
- Side-by-side comparison of all selected models
- Consensus detection when multiple models agree
- Note about binary model treating "Partielle" as "Incorrecte"

## Usage

### Manual Classification
1. Open the Classification page
2. Select which models to use:
   - ☑️ Modèle Binaire
   - ☑️ Modèle 3-classes
   - ☑️ LLM (Groq)
3. Enter question and answer
4. Click "Classifier la Réponse"
5. View results side-by-side
6. See consensus or disagreement summary

### Important Notes

⚠️ **Binary Model Behavior:**
- The binary model **purposely** classifies "Partielle" responses as "Incorrecte"
- This is by design, as the model was trained on binary labels
- Use the 3-class model if you need to distinguish between partial and incorrect answers

### When to Use Each Model

**Binary Model:**
- ✅ Faster training (simpler task)
- ✅ Higher accuracy on binary decisions
- ✅ Good for pass/fail scenarios
- ❌ Cannot distinguish partial vs incorrect

**3-Class Model:**
- ✅ More nuanced classification
- ✅ Distinguishes partial correctness
- ✅ Better for pedagogical feedback
- ❌ More complex to train

**LLM:**
- ✅ Provides reasoning/explanation
- ✅ Context-aware understanding
- ✅ Handles edge cases well
- ❌ Slower and requires API key

## Model Loading

Both models are loaded automatically when the Classification page opens:

```python
# 3-class model
classifier, classify_func, model_path, error_msg = load_classifier()

# Binary model
classifier_binary, classify_func_binary, model_path_binary, error_msg_binary = load_classifier(binary=True)
```

## Expected Behavior

When a response is "Partielle":
- **Binary Model:** Predicts "Incorrecte" (trained only on pure correct/incorrect)
- **3-Class Model:** Predicts "Partielle"
- **LLM:** Predicts "Partielle" (with reasoning)

When a response is purely Correct or Incorrect:
- **Binary Model:** Very accurate (trained specifically on these cases)
- **3-Class Model:** Accurate
- **LLM:** Accurate with reasoning

When comparing models:
- If all models agree → Green success message
- If models disagree → Warning with individual predictions
- Note about binary model behavior is shown

## Files Modified

1. `src/Answer_Quality_Classifier.py` - Added binary model support
2. `models/camembert_binary_classifier/config.json` - Added label mappings
3. `pages/2_🔍_Classification_de_Réponses.py` - Integrated binary model UI

## Testing

To test the integration:
1. Open the Streamlit app
2. Navigate to "Classification de Réponses"
3. Select all three models
4. Try different examples:
   - Completely correct answer
   - Partially correct answer
   - Incorrect answer
5. Observe the comparisons and consensus detection

## Future Enhancements

- Add batch comparison statistics
- Export comparison results to CSV
- Add accuracy metrics for each model
- Visualize disagreements in confusion matrix

