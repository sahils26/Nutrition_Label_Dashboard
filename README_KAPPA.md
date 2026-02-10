# Inter-Annotator Agreement Calculator

This tool calculates inter-annotator agreement using Kappa statistics for your annotation assessment project.

## 🎯 What It Does

- **Cohen's Kappa**: Used when you have exactly 2 annotators
- **Fleiss' Kappa**: Used when you have 3 or more annotators
- Analyzes agreement across all feedback categories (overall, theme, objects, sentiment, contentQuality, contentIntent)
- Provides interpretation and guidance based on Kappa scores

## 📊 Kappa Score Interpretation

| Kappa Range | Agreement Level | Reliability | Action |
|-------------|----------------|-------------|--------|
| < 0.0 | Poor | Unreliable | Review methodology |
| 0.0 - 0.20 | Slight | Low | Revise guidelines |
| 0.20 - 0.40 | Fair | Moderate | Consider improvements |
| 0.40 - 0.60 | Moderate | Good | Acceptable |
| 0.60 - 0.80 | Substantial | Very Good | ✅ Proceed with confidence |
| 0.80 - 1.00 | Almost Perfect | Excellent | ✅ Excellent reliability |

## 🚀 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Your Feedback Files

You need one JSON file per annotator with the same structure as your exported feedback:

```
feedback_annotator1.json
feedback_annotator2.json
feedback_annotator3.json (optional)
```

**Important**: All annotators must rate the **same posts** for agreement calculation to work!

### 3. Run the Calculator

#### Method 1: Using the main script

```bash
python kappa_calculator.py
```

Edit the `main()` function to specify your feedback file paths.

#### Method 2: Using as a library

```python
from kappa_calculator import KappaCalculator

# Specify your feedback files
feedback_files = [
    'feedback_annotator1.json',
    'feedback_annotator2.json',
    'feedback_annotator3.json'
]

# Initialize and calculate
calculator = KappaCalculator()
results = calculator.calculate_agreement(feedback_files)

# Print results
calculator.print_results(results)

# Export results
calculator.export_results(results, 'kappa_results.json')

# Generate disagreement report
calculator.generate_disagreement_report(results, 'disagreements.json')
```

## 📁 Output Files

1. **kappa_results.json**: Contains Kappa scores for each category and overall agreement
2. **disagreements.json**: Lists all posts where annotators disagreed

## 🔍 Understanding Your Results

### High Kappa (≥ 0.6) ✅

```
"Professor, the human evaluators consistently agreed on the model's 
performance. The 'Thumbs Down' signals are reliable errors."
```

**Action**: Proceed to Phase 4 with confidence!

### Moderate Kappa (0.4 - 0.6) ⚠️

```
"The posts show reasonable agreement but some ambiguity exists."
```

**Action**: Review disagreement cases, refine guidelines if needed.

### Low Kappa (< 0.4) ❌

```
"The posts were so ambiguous that humans couldn't even agree 
if the AI was right."
```

**Action**: Clarify annotation guidelines and re-annotate.

## 📋 Example Output

```
============================================================
INTER-ANNOTATOR AGREEMENT ANALYSIS
============================================================
Number of annotators: 3
Number of posts: 100
Categories analyzed: overall, theme, objects, sentiment, contentQuality, contentIntent
============================================================

Using Fleiss' Kappa (3+ annotators)

============================================================
RESULTS - Fleiss' Kappa
============================================================

Category-wise Kappa Scores:
------------------------------------------------------------
overall             : 0.7234  (Substantial)
theme               : 0.6891  (Substantial)
objects             : 0.5432  (Moderate)
sentiment           : 0.7891  (Substantial)
contentQuality      : 0.6234  (Substantial)
contentIntent       : 0.7012  (Substantial)

============================================================
Overall Kappa Score: 0.6782
Agreement Level: Substantial
Description: Substantial agreement
Reliability: Very good reliability
============================================================

✅ HIGH AGREEMENT (Kappa ≥ 0.6)

What this means for your professor:
  • Human evaluators consistently agreed on the model's performance
  • The 'Thumbs Down' signals are reliable error indicators
  • Your evaluation methodology is sound and reproducible

Next steps:
  • Proceed with confidence to Phase 4 (Model Evaluation)
  • Use majority voting for consensus scores
```

## 🛠️ Customization

### Adding New Categories

Edit the `feedback_categories` list in `KappaCalculator.__init__()`:

```python
self.feedback_categories = [
    'overall', 'theme', 'objects', 'sentiment', 
    'contentQuality', 'contentIntent', 'newCategory'
]
```

### Changing Label Mapping

Edit the `label_mapping` dictionary:

```python
self.label_mapping = {
    'positive': 1,
    'negative': 0,
    'neutral': 2,  # Add new labels
    None: -1
}
```

## 📞 Troubleshooting

### Error: "No complete annotations found"

**Cause**: Different annotators rated different posts.

**Solution**: Ensure all annotators rate the exact same set of posts.

### Error: "Cohen's Kappa requires exactly 2 annotators"

**Cause**: You have more/less than 2 annotators but the code is using Cohen's Kappa.

**Solution**: The calculator auto-detects the number of annotators. Check your input files.

### Low Kappa scores

**Possible causes**:
1. Ambiguous posts
2. Unclear annotation guidelines
3. Insufficient annotator training
4. Genuinely difficult classification task

**Solutions**:
1. Review disagreement report
2. Clarify guidelines with examples
3. Conduct annotator training session
4. Remove ambiguous posts from evaluation set

## 📚 References

- Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. *Biometrics*, 159-174.
- Fleiss, J. L. (1971). Measuring nominal scale agreement among many raters. *Psychological Bulletin*, 76(5), 378.
- Cohen, J. (1960). A coefficient of agreement for nominal scales. *Educational and Psychological Measurement*, 20(1), 37-46.

## 🎓 For Your Professor

This tool implements industry-standard inter-annotator agreement metrics:

- **Statistical Rigor**: Uses established Kappa coefficients
- **Automatic Selection**: Cohen's for 2 annotators, Fleiss' for 3+
- **Comprehensive Analysis**: Category-level and overall agreement
- **Actionable Insights**: Clear interpretation and next steps
- **Reproducible**: All calculations are deterministic and exportable

