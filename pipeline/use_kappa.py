"""
Kappa Calculator Runner
Run inter-annotator agreement analysis on feedback data
"""

from kappa_calculator import KappaCalculator
from pathlib import Path


def run_kappa_analysis():
    """
    Run Kappa analysis on your feedback files.
    """
    
    print("\n" + "="*70)
    print("  INTER-ANNOTATOR AGREEMENT CALCULATOR")
    print("="*70 + "\n")
    
    # ========================================================================
    # STEP 1: Specify your feedback files
    # ========================================================================
    # Update these paths to point to your actual feedback JSON files
    # Each file should be from a different annotator rating the SAME posts
    
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
        print("1. Collect feedback JSON exports from each annotator")
        print("2. Place them in the ../feedback_data/ folder")
        print("3. Update the file paths in this script")
        print("4. Make sure all annotators rated the SAME posts")
        print("-" * 70)
        return
    
    if len(existing_files) < 2:
        print("\n⚠️  WARNING: Need at least 2 annotators for Kappa calculation.")
        print("   Currently found:", len(existing_files))
        return
    
    # ========================================================================
    # STEP 2: Initialize the calculator
    # ========================================================================
    print(f"\n🔧 Initializing Kappa Calculator...")
    calculator = KappaCalculator()
    
    # ========================================================================
    # STEP 3: Calculate agreement
    # ========================================================================
    print(f"📊 Calculating inter-annotator agreement...\n")
    
    try:
        results = calculator.calculate_agreement(existing_files)
    except Exception as e:
        print(f"\n❌ ERROR during calculation: {str(e)}")
        print("\n💡 Common issues:")
        print("  • Annotators rated different posts (need same post IDs)")
        print("  • JSON format doesn't match expected structure")
        print("  • Missing feedback data in some posts")
        import traceback
        traceback.print_exc()
        return
    
    # ========================================================================
    # STEP 4: Display results
    # ========================================================================
    calculator.print_results(results)
    
    # ========================================================================
    # STEP 5: Export results
    # ========================================================================
    print("\n📤 Exporting results...")
    print("-" * 70)
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / 'results'
    output_dir.mkdir(exist_ok=True)
    
    # Export Kappa scores
    output_file = output_dir / 'kappa_results.json'
    calculator.export_results(results, str(output_file))
    
    # Export disagreement report
    disagreement_file = output_dir / 'disagreements.json'
    calculator.generate_disagreement_report(results, str(disagreement_file))
    
    print("-" * 70)
    
    # ========================================================================
    # STEP 6: Next steps guidance
    # ========================================================================
    print("\n" + "="*70)
    print("  NEXT STEPS")
    print("="*70)
    
    kappa = results['overall_kappa']
    
    if kappa and kappa >= 0.6:
        print("\n🎉 EXCELLENT NEWS!")
        print("\nYour annotators show substantial agreement (Kappa ≥ 0.6).")
        print("\n✅ Ready for Phase 4: Model Evaluation")
        print("\nWhat to do next:")
        print("  1. Review disagreements to understand edge cases")
        print("  2. Use majority voting to create consensus labels")
        print("  3. Calculate final model metrics (Accuracy, Error Rate)")
        print("  4. Prepare your findings for the professor")
        
    elif kappa and kappa >= 0.4:
        print("\n⚠️  MODERATE AGREEMENT")
        print("\nYour annotators show moderate agreement (0.4 ≤ Kappa < 0.6).")
        print("\n📋 Recommended actions:")
        print("  1. Review disagreements carefully")
        print("  2. Identify posts causing confusion")
        print("  3. Refine annotation guidelines")
        print("  4. Consider a discussion round with annotators")
        print("  5. Re-annotate ambiguous cases")
        
    else:
        print("\n❌ LOW AGREEMENT")
        print("\nYour annotators show low agreement (Kappa < 0.4).")
        print("\n🔧 Required actions:")
        print("  1. Review disagreements to find patterns")
        print("  2. Clarify annotation instructions with examples")
        print("  3. Conduct annotator training session")
        print("  4. Re-annotate with improved guidelines")
        print("  5. Consider simplifying the task")
    
    print("\n" + "="*70)
    print(f"  Analysis complete!")
    print(f"  Results saved to: {output_dir}")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_kappa_analysis()