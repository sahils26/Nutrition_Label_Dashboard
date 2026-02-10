"""
AI Model Correctness Evaluator
Evaluates AI predictions against human consensus feedback (thumbs up/down)
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter


class ModelEvaluator:
    """
    Evaluate AI model performance based on human correctness feedback.
    
    Feedback Schema:
    - "positive" = AI prediction was CORRECT (👍)
    - "negative" = AI prediction was WRONG (👎)
    """
    
    def __init__(self):
        self.feedback_categories = [
            # 'overall',
             'theme', 'objects', 'sentiment', 
            'contentQuality', 'contentIntent'
        ]
        
        # Mapping for feedback interpretation
        self.feedback_mapping = {
            'positive': 1,   # AI was correct
            'negative': 0,   # AI was wrong
            None: -1         # No feedback provided
        }
    
    def load_feedback_json(self, filepath: str) -> Dict:
        """Load a feedback JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_evaluations(self, feedback_files: List[str]) -> pd.DataFrame:
        """
        Extract AI predictions and human evaluations from feedback files.
        
        Args:
            feedback_files: List of paths to feedback JSON files (one per annotator)
            
        Returns:
            DataFrame with AI predictions and human correctness judgments
        """
        all_evaluations = []
        
        for annotator_idx, filepath in enumerate(feedback_files):
            data = self.load_feedback_json(filepath)
            annotator_name = f"Annotator_{annotator_idx + 1}"
            
            for post in data.get('posts', []):
                post_id = post['postId']
                llm_predictions = post.get('llm', {})
                feedback = post.get('feedback', {})
                
                for category in self.feedback_categories:
                    # Get AI prediction
                    # Create proper camelCase field names
                    field_name_map = {
                        'overall': 'llmOverall',  # Note: this field doesn't exist in your JSON
                        'theme': 'llmTheme',
                        'objects': 'llmObjects',
                        'sentiment': 'llmSentiment',
                        'contentQuality': 'llmContentQuality',  # Fixed!
                        'contentIntent': 'llmContentIntent'      # Fixed!
                    }
                    ai_prediction = llm_predictions.get(field_name_map.get(category))
                    if ai_prediction is None:
                        print(f"⚠️  Warning: Missing {field_name_map.get(category)} for post {post_id}")
                    if category == 'objects' and isinstance(ai_prediction, list):
                        ai_prediction = ai_prediction[0] if ai_prediction else None

                    # Get human judgment (was AI correct?)
                    correctness_judgment = feedback.get(category)
                    correctness_numeric = self.feedback_mapping.get(correctness_judgment, -1)
                    
                    all_evaluations.append({
                        'postId': post_id,
                        'annotator': annotator_name,
                        'category': category,
                        'ai_prediction': ai_prediction,
                        'human_judgment': correctness_judgment,
                        'is_correct': correctness_numeric,
                        'judgment_label': correctness_judgment
                    })
        
        return pd.DataFrame(all_evaluations)
    
    def build_consensus(self, df: pd.DataFrame, category: str, post_id: str) -> Tuple[str, float, List]:
        """
        Build consensus from multiple annotators' judgments.
        
        Args:
            df: DataFrame with evaluations
            category: Category to evaluate
            post_id: Post ID
            
        Returns:
            Tuple of (consensus_judgment, confidence, individual_votes)
        """
        # Get all judgments for this post and category
        mask = (df['category'] == category) & (df['postId'] == post_id) & (df['is_correct'] != -1)
        judgments = df[mask]['is_correct'].tolist()
        
        if not judgments:
            return 'no_data', 0.0, []
        
        # Count votes
        correct_votes = sum(1 for j in judgments if j == 1)
        incorrect_votes = sum(1 for j in judgments if j == 0)
        total_votes = len(judgments)
        
        # Determine consensus
        if correct_votes > incorrect_votes:
            consensus = 'correct'
            confidence = correct_votes / total_votes
        elif incorrect_votes > correct_votes:
            consensus = 'incorrect'
            confidence = incorrect_votes / total_votes
        else:
            consensus = 'uncertain'
            confidence = 0.5
        
        return consensus, confidence, judgments
    
    def evaluate_category(self, df: pd.DataFrame, category: str) -> Dict:
        """
        Evaluate AI performance for a specific category.
        
        Args:
            df: DataFrame with evaluations
            category: Category to evaluate
            
        Returns:
            Dictionary with performance metrics
        """
        category_data = df[df['category'] == category]
        post_ids = category_data['postId'].unique()
        
        correct_count = 0
        incorrect_count = 0
        uncertain_count = 0
        no_data_count = 0
        
        consensus_details = []
        
        for post_id in post_ids:
            consensus, confidence, votes = self.build_consensus(df, category, post_id)
            
            if consensus == 'correct':
                correct_count += 1
            elif consensus == 'incorrect':
                incorrect_count += 1
            elif consensus == 'uncertain':
                uncertain_count += 1
            else:
                no_data_count += 1
            
            consensus_details.append({
                'postId': post_id,
                'consensus': consensus,
                'confidence': round(confidence, 4),
                'votes': votes
            })
        
        # Calculate metrics
        total_evaluated = correct_count + incorrect_count
        accuracy = correct_count / total_evaluated if total_evaluated > 0 else 0
        error_rate = incorrect_count / total_evaluated if total_evaluated > 0 else 0
        
        return {
            'correct': correct_count,
            'incorrect': incorrect_count,
            'uncertain': uncertain_count,
            'no_data': no_data_count,
            'total_posts': len(post_ids),
            'total_evaluated': total_evaluated,
            'accuracy': round(accuracy, 4),
            'error_rate': round(error_rate, 4),
            'consensus_details': consensus_details
        }
    
    def evaluate_model(self, feedback_files: List[str]) -> Dict:
        """
        Main method to evaluate AI model performance.
        
        Args:
            feedback_files: List of paths to feedback JSON files
            
        Returns:
            Dictionary with comprehensive evaluation results
        """
        # Extract all evaluations
        df = self.extract_evaluations(feedback_files)
        
        # Get number of annotators
        n_annotators = df['annotator'].nunique()
        n_posts = df['postId'].nunique()
        
        print(f"\n{'='*70}")
        print(f"AI MODEL CORRECTNESS EVALUATION")
        print(f"{'='*70}")
        print(f"Number of annotators: {n_annotators}")
        print(f"Number of posts: {n_posts}")
        print(f"Categories evaluated: {', '.join(self.feedback_categories)}")
        print(f"{'='*70}\n")
        
        # Evaluate each category
        category_results = {}
        for category in self.feedback_categories:
            print(f"Evaluating {category}...")
            category_results[category] = self.evaluate_category(df, category)
        
        # Calculate overall metrics
        total_correct = sum(r['correct'] for r in category_results.values())
        total_incorrect = sum(r['incorrect'] for r in category_results.values())
        total_uncertain = sum(r['uncertain'] for r in category_results.values())
        total_evaluated = total_correct + total_incorrect
        
        overall_accuracy = total_correct / total_evaluated if total_evaluated > 0 else 0
        overall_error_rate = total_incorrect / total_evaluated if total_evaluated > 0 else 0
        
        results = {
            'n_annotators': n_annotators,
            'n_posts': n_posts,
            'category_results': category_results,
            'overall_metrics': {
                'total_correct': total_correct,
                'total_incorrect': total_incorrect,
                'total_uncertain': total_uncertain,
                'total_evaluated': total_evaluated,
                'overall_accuracy': round(overall_accuracy, 4),
                'overall_error_rate': round(overall_error_rate, 4)
            },
            'raw_data': df
        }
        
        return results
    
    def print_results(self, results: Dict):
        """Print formatted evaluation results."""
        print(f"\n{'='*70}")
        print(f"EVALUATION RESULTS")
        print(f"{'='*70}\n")
        
        print("Category-wise Performance:")
        print("-" * 70)
        print(f"{'Category':<20} {'Correct':<10} {'Wrong':<10} {'Uncertain':<10} {'Accuracy':<10}")
        print("-" * 70)
        
        for category, metrics in results['category_results'].items():
            accuracy_pct = metrics['accuracy'] * 100
            print(f"{category:<20} {metrics['correct']:<10} {metrics['incorrect']:<10} "
                  f"{metrics['uncertain']:<10} {accuracy_pct:>6.2f}%")
        
        print("\n" + "=" * 70)
        print("OVERALL MODEL PERFORMANCE")
        print("=" * 70)
        overall = results['overall_metrics']
        print(f"Total Evaluations:  {overall['total_evaluated']}")
        print(f"Correct:            {overall['total_correct']}")
        print(f"Incorrect:          {overall['total_incorrect']}")
        print(f"Uncertain:          {overall['total_uncertain']}")
        print(f"\nOverall Accuracy:   {overall['overall_accuracy']*100:.2f}%")
        print(f"Overall Error Rate: {overall['overall_error_rate']*100:.2f}%")
        print("=" * 70)
        
        # Provide insights
        self._print_insights(results)
    
    def _print_insights(self, results: Dict):
        """Print insights and recommendations based on results."""
        print(f"\n{'='*70}")
        print("INSIGHTS & RECOMMENDATIONS")
        print("=" * 70)
        
        # Find best and worst performing categories
        category_accuracies = {
            cat: metrics['accuracy'] 
            for cat, metrics in results['category_results'].items() 
            if metrics['total_evaluated'] > 0
        }
        
        if category_accuracies:
            best_category = max(category_accuracies, key=category_accuracies.get)
            worst_category = min(category_accuracies, key=category_accuracies.get)
            
            print(f"\n✅ STRONGEST AREA:")
            print(f"   {best_category}: {category_accuracies[best_category]*100:.1f}% accuracy")
            
            print(f"\n⚠️  NEEDS IMPROVEMENT:")
            print(f"   {worst_category}: {category_accuracies[worst_category]*100:.1f}% accuracy")
            
            # Overall assessment
            overall_acc = results['overall_metrics']['overall_accuracy']
            if overall_acc >= 0.9:
                print(f"\n🎉 EXCELLENT: Model shows outstanding performance (>90% accuracy)")
            elif overall_acc >= 0.8:
                print(f"\n✅ GOOD: Model shows strong performance (80-90% accuracy)")
            elif overall_acc >= 0.7:
                print(f"\n⚠️  FAIR: Model shows acceptable performance (70-80% accuracy)")
            else:
                print(f"\n❌ POOR: Model needs significant improvement (<70% accuracy)")
            
            # Sample size warning
            n_posts = results['n_posts']
            if n_posts < 30:
                print(f"\n⚠️  WARNING: Sample size ({n_posts} posts) is too small for robust conclusions.")
                print(f"   Recommendation: Collect at least 100 posts for reliable statistics.")
        
        print("=" * 70 + "\n")
    
    def export_results(self, results: Dict, output_path: str):
        """Export evaluation results to JSON file."""
        export_data = {
            'n_annotators': results['n_annotators'],
            'n_posts': results['n_posts'],
            'category_results': {},
            'overall_metrics': results['overall_metrics']
        }
        
        # Export category results (without raw consensus details for cleaner output)
        for category, metrics in results['category_results'].items():
            export_data['category_results'][category] = {
                'correct': metrics['correct'],
                'incorrect': metrics['incorrect'],
                'uncertain': metrics['uncertain'],
                'total_evaluated': metrics['total_evaluated'],
                'accuracy': metrics['accuracy'],
                'error_rate': metrics['error_rate']
            }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results exported to: {output_path}")
    
    def export_detailed_report(self, results: Dict, output_path: str):
        """Export detailed per-post evaluation report."""
        detailed_data = []
        
        for category, metrics in results['category_results'].items():
            for detail in metrics['consensus_details']:
                detailed_data.append({
                    'category': category,
                    'postId': detail['postId'],
                    'consensus': detail['consensus'],
                    'confidence': detail['confidence'],
                    'n_votes': len(detail['votes']),
                    'votes': detail['votes']
                })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(detailed_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Detailed report exported to: {output_path}")
    
    def identify_problem_posts(self, results: Dict) -> List[Dict]:
        """
        Identify posts where AI consistently performs poorly.
        
        Returns:
            List of problem posts with error counts
        """
        df = results['raw_data']
        post_ids = df['postId'].unique()
        
        problem_posts = []
        
        for post_id in post_ids:
            errors_in_post = 0
            total_categories = 0
            
            for category in self.feedback_categories:
                consensus, _, _ = self.build_consensus(df, category, post_id)
                if consensus == 'incorrect':
                    errors_in_post += 1
                if consensus in ['correct', 'incorrect']:
                    total_categories += 1
            
            if total_categories > 0:
                error_rate = errors_in_post / total_categories
                if error_rate > 0.5:  # More than 50% errors
                    problem_posts.append({
                        'postId': post_id,
                        'errors': errors_in_post,
                        'total': total_categories,
                        'error_rate': round(error_rate, 4)
                    })
        
        return sorted(problem_posts, key=lambda x: x['error_rate'], reverse=True)


def main():
    """
    Example usage of the ModelEvaluator.
    """
    print("\n" + "="*70)
    print("MODEL EVALUATOR - AI Correctness Assessment")
    print("="*70 + "\n")
    
    # Example: List your feedback files here
    feedback_files = [
        'feedback_annotator1.json',
        'feedback_annotator2.json',
    ]
    
    # Check if files exist
    missing_files = [f for f in feedback_files if not Path(f).exists()]
    if missing_files:
        print("❌ Missing feedback files:")
        for f in missing_files:
            print(f"   - {f}")
        print("\nPlease provide the correct paths to your feedback JSON files.")
        return
    
    # Initialize evaluator
    evaluator = ModelEvaluator()
    
    # Evaluate model
    results = evaluator.evaluate_model(feedback_files)
    
    # Print results
    evaluator.print_results(results)
    
    # Export results
    evaluator.export_results(results, 'model_evaluation.json')
    evaluator.export_detailed_report(results, 'evaluation_details.json')
    
    # Identify problem posts
    problem_posts = evaluator.identify_problem_posts(results)
    if problem_posts:
        print(f"\n⚠️  Found {len(problem_posts)} posts with high error rates:")
        for post in problem_posts[:5]:  # Show top 5
            print(f"   {post['postId']}: {post['errors']}/{post['total']} errors "
                  f"({post['error_rate']*100:.1f}%)")


if __name__ == "__main__":
    main()

