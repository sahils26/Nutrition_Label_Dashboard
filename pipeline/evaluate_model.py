"""
Model Evaluation Runner Script
Evaluates AI model correctness based on human feedback annotations
"""

from model_evaluator import ModelEvaluator
from pathlib import Path


def run_model_evaluation():
    """
    Run AI model evaluation on feedback files.
    """
    
    print("\n" + "="*70)
    print("  AI MODEL CORRECTNESS EVALUATION")
    print("="*70 + "\n")
    
    # ========================================================================
    # STEP 1: Specify your feedback files
    # ========================================================================
    # These should be the SAME files you used for IAA
    # Each file contains AI predictions (LLM fields) and human judgments (feedback fields)
    
    feedback_files = [
        '../feedback_data/llm-feedback-export-2026-02-09.json',       # Annotator 1
        '../feedback_data/llm-feedback-export-2026-02-09 (1).json',   # Annotator 2
        # Add more annotator files here as you collect them
        # '../feedback_data/annotator3.json',
    ]
    
    print("📂 Checking feedback files...")
    print("-" * 70)
    
    # Check if files exist
    existing_files = []
    missing_files = []
    
    for filepath in feedback_files:
        full_path = Path(__file__).parent / filepath
        if full_path.exists():
            file_size = full_path.stat().st_size
            print(f"  ✅ {filepath} ({file_size:,} bytes)")
            existing_files.append(str(full_path))
        else:
            print(f"  ❌ {filepath} (NOT FOUND)")
            missing_files.append(filepath)
    
    print("-" * 70)
    
    if missing_files:
        print(f"\n❌ ERROR: {len(missing_files)} file(s) not found.")
        print("\n💡 SETUP INSTRUCTIONS:")
        print("-" * 70)
        print("1. Use the same feedback files from IAA analysis")
        print("2. Files should contain both LLM predictions and human feedback")
        print("3. Update the file paths in this script")
        print("-" * 70)
        return
    
    if len(existing_files) < 2:
        print("\n⚠️  WARNING: Need at least 2 annotators for consensus.")
        print("   Currently found:", len(existing_files))
        return
    
    # ========================================================================
    # STEP 2: Initialize the evaluator
    # ========================================================================
    print(f"\n🔧 Initializing Model Evaluator...")
    evaluator = ModelEvaluator()
    
    # ========================================================================
    # STEP 3: Evaluate model
    # ========================================================================
    print(f"📊 Evaluating AI model performance...\n")
    
    try:
        results = evaluator.evaluate_model(existing_files)
    except Exception as e:
        print(f"\n❌ ERROR during evaluation: {str(e)}")
        print("\n💡 Common issues:")
        print("  • LLM fields missing in JSON (need llmTheme, llmSentiment, etc.)")
        print("  • Feedback fields missing (need positive/negative judgments)")
        print("  • JSON format doesn't match expected structure")
        import traceback
        traceback.print_exc()
        return
    
    # ========================================================================
    # STEP 4: Display results
    # ========================================================================
    evaluator.print_results(results)
    
    # ========================================================================
    # STEP 5: Export results
    # ========================================================================
    print("\n📤 Exporting results...")
    print("-" * 70)
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / 'results'
    output_dir.mkdir(exist_ok=True)
    
    # Export summary results
    summary_file = output_dir / 'model_evaluation.json'
    evaluator.export_results(results, str(summary_file))
    
    # Export detailed per-post report
    detail_file = output_dir / 'evaluation_details.json'
    evaluator.export_detailed_report(results, str(detail_file))
    
    print("-" * 70)
    
    # ========================================================================
    # STEP 6: Identify problem areas
    # ========================================================================
    print("\n" + "="*70)
    print("  PROBLEM POST ANALYSIS")
    print("="*70)
    
    problem_posts = evaluator.identify_problem_posts(results)
    
    if problem_posts:
        print(f"\n⚠️  Found {len(problem_posts)} posts where AI made multiple errors:\n")
        for post in problem_posts[:10]:  # Show top 10
            print(f"   • Post {post['postId']}: {post['errors']}/{post['total']} "
                  f"categories wrong ({post['error_rate']*100:.1f}% error rate)")
        
        if len(problem_posts) > 10:
            print(f"\n   ... and {len(problem_posts) - 10} more posts with issues")
        
        print("\n💡 Recommendation: Review these posts to identify patterns in AI errors")
    else:
        print("\n✅ No problematic posts found! AI performs consistently well.")
    
    print("="*70)
    
    # ========================================================================
    # STEP 7: Next steps guidance
    # ========================================================================
    print("\n" + "="*70)
    print("  NEXT STEPS")
    print("="*70)
    
    overall_acc = results['overall_metrics']['overall_accuracy']
    
    if overall_acc >= 0.90:
        print("\n🎉 OUTSTANDING PERFORMANCE!")
        print(f"\nYour AI model shows excellent accuracy ({overall_acc*100:.1f}%).")
        print("\n✅ What to do next:")
        print("  1. Document the evaluation methodology")
        print("  2. Analyze the few errors to understand edge cases")
        print("  3. Consider deploying with monitoring")
        print("  4. Scale to 100+ posts for publication-ready results")
        
    elif overall_acc >= 0.80:
        print("\n✅ STRONG PERFORMANCE!")
        print(f"\nYour AI model shows good accuracy ({overall_acc*100:.1f}%).")
        print("\n📋 Recommended actions:")
        print("  1. Review the error cases in evaluation_details.json")
        print("  2. Identify patterns in incorrect predictions")
        print("  3. Consider category-specific improvements")
        print("  4. Collect more data for robust statistics (aim for 100+ posts)")
        
    elif overall_acc >= 0.70:
        print("\n⚠️  FAIR PERFORMANCE")
        print(f"\nYour AI model shows acceptable accuracy ({overall_acc*100:.1f}%).")
        print("\n🔧 Improvement needed:")
        print("  1. Focus on weakest categories (check results above)")
        print("  2. Analyze problem posts for common patterns")
        print("  3. Consider retraining or fine-tuning the model")
        print("  4. Review and update classification guidelines")
        
    else:
        print("\n❌ NEEDS SIGNIFICANT IMPROVEMENT")
        print(f"\nYour AI model accuracy is below threshold ({overall_acc*100:.1f}%).")
        print("\n🔧 Critical actions:")
        print("  1. Review all error cases systematically")
        print("  2. Identify if errors are in specific categories")
        print("  3. Consider model retraining with feedback data")
        print("  4. Validate that annotation guidelines are clear")
        print("  5. Check if the task itself is well-defined")
    
    # Sample size check
    n_posts = results['n_posts']
    if n_posts < 30:
        print(f"\n⚠️  SAMPLE SIZE WARNING:")
        print(f"   Current: {n_posts} posts")
        print(f"   Minimum recommended: 30 posts for exploratory analysis")
        print(f"   Publication standard: 100+ posts")
        print(f"   Action: Collect {100 - n_posts} more posts for robust conclusions")
    
    print("\n" + "="*70)
    print(f"  Evaluation complete!")
    print(f"  Results saved to: {output_dir}")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_model_evaluation()

