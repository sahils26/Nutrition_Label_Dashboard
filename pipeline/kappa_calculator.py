"""
Inter-Annotator Agreement Calculator using Kappa Statistics
Supports both Cohen's Kappa (2 annotators) and Fleiss' Kappa (3+ annotators)
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import warnings

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats.inter_rater import aggregate_raters, fleiss_kappa

warnings.filterwarnings('ignore')


class KappaCalculator:
    """
    Calculate inter-annotator agreement for annotation feedback data.
    """
    
    def __init__(self):
        self.feedback_categories = [
            'overall', 'theme', 'objects', 'sentiment', 
            'contentQuality', 'contentIntent'
        ]
        # Mapping for converting feedback to numeric values
        self.label_mapping = {
            'positive': 1,
            'negative': 0,
            None: -1  # For missing values
        }
    
    def load_feedback_json(self, filepath: str) -> Dict:
        """Load a single feedback JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_annotations(self, feedback_files: List[str]) -> pd.DataFrame:
        """
        Extract annotations from multiple feedback JSON files.
        
        Args:
            feedback_files: List of paths to feedback JSON files (one per annotator)
            
        Returns:
            DataFrame with columns: postId, annotator, category, rating
        """
        all_annotations = []
        
        for annotator_idx, filepath in enumerate(feedback_files):
            data = self.load_feedback_json(filepath)
            annotator_name = f"Annotator_{annotator_idx + 1}"
            
            for post in data.get('posts', []):
                post_id = post['postId']
                feedback = post.get('feedback', {})
                
                for category in self.feedback_categories:
                    rating = feedback.get(category)
                    numeric_rating = self.label_mapping.get(rating, -1)
                    
                    all_annotations.append({
                        'postId': post_id,
                        'annotator': annotator_name,
                        'category': category,
                        'rating': numeric_rating,
                        'rating_label': rating
                    })
        
        return pd.DataFrame(all_annotations)
    
    def prepare_matrix_for_cohens(self, df: pd.DataFrame, category: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for Cohen's Kappa (2 annotators).
        
        Returns:
            Two arrays of ratings from annotator 1 and annotator 2
        """
        category_data = df[df['category'] == category].copy()
        
        # Pivot to get annotators as columns
        pivot = category_data.pivot(index='postId', columns='annotator', values='rating')
        
        # Get the two annotators
        annotators = pivot.columns.tolist()
        if len(annotators) != 2:
            raise ValueError(f"Cohen's Kappa requires exactly 2 annotators, found {len(annotators)}")
        
        # Remove rows with missing values (-1)
        mask = (pivot[annotators[0]] != -1) & (pivot[annotators[1]] != -1)
        clean_data = pivot[mask]
        
        return clean_data[annotators[0]].values, clean_data[annotators[1]].values
    
    def prepare_matrix_for_fleiss(self, df: pd.DataFrame, category: str) -> np.ndarray:
        """
        Prepare data for Fleiss' Kappa (3+ annotators).
        
        Returns:
            Matrix of shape (n_items, n_categories) where each cell contains count
        """
        category_data = df[df['category'] == category].copy()
        
        # Pivot to get annotators as columns
        pivot = category_data.pivot(index='postId', columns='annotator', values='rating')
        
        # Remove rows with any missing values (-1)
        clean_data = pivot[(pivot != -1).all(axis=1)]
        
        if len(clean_data) == 0:
            raise ValueError(f"No complete annotations found for category: {category}")
        
        # Count ratings per item (row)
        # For binary classification (0 or 1), we need counts
        n_items = len(clean_data)
        n_categories = 2  # positive (1) and negative (0)
        
        # Create count matrix
        count_matrix = np.zeros((n_items, n_categories))
        
        for idx, (_, row) in enumerate(clean_data.iterrows()):
            for rating in row:
                if rating in [0, 1]:
                    count_matrix[idx, int(rating)] += 1
        
        return count_matrix
    
    def calculate_cohens_kappa(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate Cohen's Kappa for each category."""
        results = {}
        
        for category in self.feedback_categories:
            try:
                ratings1, ratings2 = self.prepare_matrix_for_cohens(df, category)
                
                # Check for perfect agreement (100% same ratings)
                if np.array_equal(ratings1, ratings2):
                    # Perfect agreement - assign Kappa = 1.0
                    results[category] = 1.0
                else:
                    kappa = cohen_kappa_score(ratings1, ratings2)
                    results[category] = round(kappa, 4)
                
            except Exception as e:
                print(f"Error calculating Cohen's Kappa for {category}: {str(e)}")
                results[category] = None
        
        return results
    
    def calculate_fleiss_kappa(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate Fleiss' Kappa for each category."""
        results = {}
        
        for category in self.feedback_categories:
            try:
                count_matrix = self.prepare_matrix_for_fleiss(df, category)
                
                if len(count_matrix) == 0:
                    results[category] = None
                    continue
                
                kappa = fleiss_kappa(count_matrix)
                results[category] = round(kappa, 4)
                
            except Exception as e:
                print(f"Error calculating Fleiss' Kappa for {category}: {str(e)}")
                results[category] = None
        
        return results
    
    def calculate_raw_agreement(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate raw percentage agreement for each category.
        
        Returns:
            Dictionary with raw agreement percentages per category
        """
        results = {}
        
        for category in self.feedback_categories:
            try:
                category_data = df[df['category'] == category].copy()
                
                # Pivot to get annotators as columns
                pivot = category_data.pivot(index='postId', columns='annotator', values='rating')
                
                # Remove rows with missing values (-1)
                clean_data = pivot[(pivot != -1).all(axis=1)]
                
                if len(clean_data) == 0:
                    results[category] = None
                    continue
                
                # Calculate agreement: how many rows have all same values
                agreements = 0
                total = len(clean_data)
                
                for _, row in clean_data.iterrows():
                    # Check if all values in the row are the same
                    if len(set(row.values)) == 1:
                        agreements += 1
                
                raw_agreement = agreements / total if total > 0 else 0
                results[category] = round(raw_agreement, 4)
                
            except Exception as e:
                print(f"Error calculating raw agreement for {category}: {str(e)}")
                results[category] = None
        
        return results
    
    
    def calculate_confusion_matrices(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Calculate confusion matrix for each category (for 2 annotators).
        
        Returns:
            Dictionary with confusion matrices per category
        """
        results = {}
        
        n_annotators = df['annotator'].nunique()
        if n_annotators != 2:
            print(f"⚠️  Confusion matrix is designed for 2 annotators. Found: {n_annotators}")
            return results
        
        for category in self.feedback_categories:
            try:
                category_data = df[df['category'] == category].copy()
                
                # Pivot to get annotators as columns
                pivot = category_data.pivot(index='postId', columns='annotator', values='rating')
                
                # Get annotator names
                annotators = pivot.columns.tolist()
                ann1, ann2 = annotators[0], annotators[1]
                
                # Remove rows with missing values (-1)
                clean_data = pivot[(pivot[ann1] != -1) & (pivot[ann2] != -1)]
                
                if len(clean_data) == 0:
                    results[category] = None
                    continue
                
                # Build confusion matrix
                # Count: (Ann1=Pos, Ann2=Pos), (Ann1=Pos, Ann2=Neg), etc.
                pos_pos = len(clean_data[(clean_data[ann1] == 1) & (clean_data[ann2] == 1)])
                pos_neg = len(clean_data[(clean_data[ann1] == 1) & (clean_data[ann2] == 0)])
                neg_pos = len(clean_data[(clean_data[ann1] == 0) & (clean_data[ann2] == 1)])
                neg_neg = len(clean_data[(clean_data[ann1] == 0) & (clean_data[ann2] == 0)])
                
                results[category] = {
                    'matrix': {
                        'positive_positive': pos_pos,
                        'positive_negative': pos_neg,
                        'negative_positive': neg_pos,
                        'negative_negative': neg_neg
                    },
                    'total_items': len(clean_data),
                    'annotator_1_positive_rate': round((pos_pos + pos_neg) / len(clean_data), 4) if len(clean_data) > 0 else 0,
                    'annotator_2_positive_rate': round((pos_pos + neg_pos) / len(clean_data), 4) if len(clean_data) > 0 else 0
                }
                
            except Exception as e:
                print(f"Error calculating confusion matrix for {category}: {str(e)}")
                results[category] = None
        
        return results
    
    
    def print_confusion_matrix(self, category: str, cm_data: Dict):
        """Pretty print a confusion matrix."""
        if cm_data is None:
            print(f"\n{category}: No data available")
            return
        
        matrix = cm_data['matrix']
        total = cm_data['total_items']
        
        print(f"\n{category.upper()} - Confusion Matrix (n={total})")
        print("─" * 50)
        print(f"                    Annotator 2")
        print(f"                    Positive    Negative")
        print(f"Annotator 1  Pos      {matrix['positive_positive']:3d}         {matrix['positive_negative']:3d}")
        print(f"             Neg      {matrix['negative_positive']:3d}         {matrix['negative_negative']:3d}")
        print("─" * 50)
        print(f"Ann1 Positive Rate: {cm_data['annotator_1_positive_rate']:.2%}")
        print(f"Ann2 Positive Rate: {cm_data['annotator_2_positive_rate']:.2%}") 
        
    def calculate_agreement(self, feedback_files: List[str]) -> Dict:
        """
        Main method to calculate inter-annotator agreement.
        
        Args:
            feedback_files: List of paths to feedback JSON files
            
        Returns:
            Dictionary with kappa scores and interpretation
        """
        # Extract all annotations
        df = self.extract_annotations(feedback_files)
        
        # Get number of annotators
        n_annotators = df['annotator'].nunique()
        print(f"\n{'='*60}")
        print(f"INTER-ANNOTATOR AGREEMENT ANALYSIS")
        print(f"{'='*60}")
        print(f"Number of annotators: {n_annotators}")
        print(f"Number of posts: {df['postId'].nunique()}")
        print(f"Categories analyzed: {', '.join(self.feedback_categories)}")
        print(f"{'='*60}\n")
        
        # Choose appropriate Kappa
        if n_annotators == 2:
            print("Using Cohen's Kappa (2 annotators)\n")
            kappa_scores = self.calculate_cohens_kappa(df)
            kappa_type = "Cohen's Kappa"
        elif n_annotators >= 3:
            print("Using Fleiss' Kappa (3+ annotators)\n")
            kappa_scores = self.calculate_fleiss_kappa(df)
            kappa_type = "Fleiss' Kappa"
        else:
            raise ValueError("Need at least 2 annotators")
        
        # Calculate overall agreement
        valid_scores = [v for v in kappa_scores.values() if v is not None]
        overall_kappa = round(np.mean(valid_scores), 4) if valid_scores else None
        print("📊 Calculating additional metrics...\n")
        # Calculate raw agreement
        raw_agreement_scores = self.calculate_raw_agreement(df)
        overall_raw_agreement = round(np.mean([v for v in raw_agreement_scores.values() if v is not None]), 4) if any(v is not None for v in raw_agreement_scores.values()) else None
        
        # Calculate confusion matrices
        confusion_matrices = self.calculate_confusion_matrices(df)
        # Interpret scores
        interpretation = self._interpret_kappa(overall_kappa)
        
        results = {
            'kappa_type': kappa_type,
            'n_annotators': n_annotators,
            'n_posts': df['postId'].nunique(),
            'category_scores': kappa_scores,
            'overall_kappa': overall_kappa,
            'raw_agreement_scores': raw_agreement_scores,           # ← NEW
            'overall_raw_agreement': overall_raw_agreement,         # ← NEW
            'confusion_matrices': confusion_matrices,               # ← NEW
            'interpretation': interpretation,
            'raw_data': df
        }
        return results
        
    
    def _interpret_kappa(self, kappa: float) -> Dict[str, str]:
        """
        Interpret Kappa score based on Landis & Koch (1977) scale.
        """
        if kappa is None:
            return {
                'level': 'Unknown',
                'description': 'Unable to calculate',
                'reliability': 'N/A'
            }
        
        if kappa < 0:
            level = 'Poor'
            description = 'Less than chance agreement'
            reliability = 'Unreliable'
        elif kappa < 0.20:
            level = 'Slight'
            description = 'Slight agreement'
            reliability = 'Low reliability'
        elif kappa < 0.40:
            level = 'Fair'
            description = 'Fair agreement'
            reliability = 'Moderate reliability'
        elif kappa < 0.60:
            level = 'Moderate'
            description = 'Moderate agreement'
            reliability = 'Good reliability'
        elif kappa < 0.80:
            level = 'Substantial'
            description = 'Substantial agreement'
            reliability = 'Very good reliability'
        else:
            level = 'Almost Perfect'
            description = 'Almost perfect agreement'
            reliability = 'Excellent reliability'
        
        return {
            'level': level,
            'description': description,
            'reliability': reliability
        }
    
    def print_results(self, results: Dict):
        """Print formatted results."""
        print(f"\n{'='*60}")
        print(f"RESULTS - {results['kappa_type']}")
        print(f"{'='*60}\n")
        
        print("Category-wise Kappa Scores:")
        print("-" * 60)
        for category, score in results['category_scores'].items():
            if score is not None:
                interpretation = self._interpret_kappa(score)
                print(f"{category:20s}: {score:6.4f}  ({interpretation['level']})")
            else:
                print(f"{category:20s}: N/A")
        print("\n" + "=" * 60)
        print("RAW AGREEMENT PERCENTAGES")
        print("=" * 60)
        for category, score in results['raw_agreement_scores'].items():
            if score is not None:
                print(f"{category:20s}: {score:6.2%}")
            else:
                print(f"{category:20s}: N/A")

        
        print("\n" + "=" * 60)
        print(f"Overall Kappa Score: {results['overall_kappa']}")
        print(f"Agreement Level: {results['interpretation']['level']}")
        print(f"Description: {results['interpretation']['description']}")
        print(f"Reliability: {results['interpretation']['reliability']}")
        print("=" * 60)

        print("\n" + "=" * 60)
        print("CONFUSION MATRICES")
        print("=" * 60)

        if results['n_annotators'] == 2:
            for category in self.feedback_categories:
                cm_data = results['confusion_matrices'].get(category)
                self.print_confusion_matrix(category, cm_data)
        else:
            print("(Confusion matrices only available for 2 annotators)")

        
        # Provide guidance
        self._print_guidance(results['overall_kappa'])
    
    def _print_guidance(self, kappa: float):
        """Print guidance based on Kappa score."""
        print(f"\n{'='*60}")
        print("GUIDANCE FOR YOUR ASSESSMENT")
        print("=" * 60)
        
        if kappa is None:
            print("❌ Unable to calculate agreement - check your data")
        elif kappa >= 0.60:
            print("✅ HIGH AGREEMENT (Kappa ≥ 0.6)")
            print("\nWhat this means for your professor:")
            print("  • Human evaluators consistently agreed on the model's performance")
            print("  • The 'Thumbs Down' signals are reliable error indicators")
            print("  • Your evaluation methodology is sound and reproducible")
            print("\nNext steps:")
            print("  • Proceed with confidence to Phase 4 (Model Evaluation)")
            print("  • Use majority voting for consensus scores")
        elif kappa >= 0.40:
            print("⚠️ MODERATE AGREEMENT (0.4 ≤ Kappa < 0.6)")
            print("\nWhat this means:")
            print("  • There is reasonable agreement, but some ambiguity")
            print("  • Some posts may be genuinely difficult to judge")
            print("  • Consider reviewing disagreement cases")
            print("\nRecommendations:")
            print("  • Identify posts with high disagreement")
            print("  • Refine annotation guidelines")
            print("  • Consider a discussion round among annotators")
        else:
            print("❌ LOW AGREEMENT (Kappa < 0.4)")
            print("\nWhat this means:")
            print("  • Posts are too ambiguous for consistent judgment")
            print("  • Annotation guidelines may need clarification")
            print("  • Human annotators couldn't reliably agree")
            print("\nAction required:")
            print("  • Review and clarify annotation instructions")
            print("  • Provide examples of edge cases")
            print("  • Consider training session for annotators")
            print("  • Re-annotate with clearer guidelines")
        
        print("=" * 60 + "\n")
    
    def export_results(self, results: Dict, output_path: str):
        """Export results to JSON file."""
        export_data = {
            'kappa_type': results['kappa_type'],
            'n_annotators': results['n_annotators'],
            'n_posts': results['n_posts'],
            'category_scores': results['category_scores'],
            'overall_kappa': results['overall_kappa'],
            'raw_agreement_scores': results['raw_agreement_scores'],       # ← NEW
            'overall_raw_agreement': results['overall_raw_agreement'],     # ← NEW
            'confusion_matrices': results['confusion_matrices'],           # ← NEW
            'interpretation': results['interpretation'],
            # 'raw_data': results['raw_data']
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results exported to: {output_path}")
    
    def generate_disagreement_report(self, results: Dict, output_path: str):
        """Generate a detailed report of disagreements between annotators."""
        df = results['raw_data']
        
        # Pivot to get annotators as columns for each category
        disagreements = []
        
        for category in self.feedback_categories:
            category_data = df[df['category'] == category].copy()
            pivot = category_data.pivot(index='postId', columns='annotator', values='rating_label')
            
            # Find rows where annotators disagree
            for post_id, row in pivot.iterrows():
                ratings = row.dropna().tolist()
                if len(set(ratings)) > 1:  # Disagreement
                    disagreements.append({
                        'postId': post_id,
                        'category': category,
                        'annotations': row.to_dict()
                    })
        
        # Export disagreements
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(disagreements, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Disagreement report exported to: {output_path}")
        print(f"   Total disagreements found: {len(disagreements)}")


def main():
    """
    Example usage of the KappaCalculator.
    """
    print("\n" + "="*60)
    print("KAPPA CALCULATOR - Inter-Annotator Agreement")
    print("="*60 + "\n")
    
    # Example: List your feedback files here
    feedback_files = [
        'feedback_annotator1.json',
        'feedback_annotator2.json',
        # 'feedback_annotator3.json',  # Uncomment if you have 3 annotators
    ]
    
    # Check if files exist
    missing_files = [f for f in feedback_files if not Path(f).exists()]
    if missing_files:
        print("❌ Missing feedback files:")
        for f in missing_files:
            print(f"   - {f}")
        print("\nPlease provide the correct paths to your feedback JSON files.")
        print("\nExpected format:")
        print("  - feedback_annotator1.json")
        print("  - feedback_annotator2.json")
        print("  - feedback_annotator3.json (optional)")
        return
    
    # Initialize calculator
    calculator = KappaCalculator()
    
    # Calculate agreement
    results = calculator.calculate_agreement(feedback_files)
    
    # Print results
    calculator.print_results(results)
    
    # Export results
    calculator.export_results(results, 'kappa_results.json')
    
    # Generate disagreement report
    calculator.generate_disagreement_report(results, 'disagreements.json')


if __name__ == "__main__":
    main()

