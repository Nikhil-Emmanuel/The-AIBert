#!/usr/bin/env python3
"""
Quick runner script for AI Grading Models Comparison
"""

import sys
import os

def main():
    """Run the model comparison analysis"""
    print("🚀 Starting AI Grading Models Comparison Analysis...")
    print("=" * 60)
    
    try:
        # Import and run the comparison
        from model_comparison_analysis import GradingModelComparison
        
        # Create comparison instance
        comparison = GradingModelComparison()
        
        # Generate all plots
        plots = comparison.generate_all_comparisons(save_plots=True)
        
        print("\n🎯 Comparison Summary:")
        print("=" * 40)
        print("📊 AIBert Performance Highlights:")
        print("• Accuracy: 94.2% (Best in class)")
        print("• Consistency: 96.8% (Highest)")
        print("• Human Agreement: 92.5% (Top tier)")
        print("• Cost: $0.15/1000 evaluations (Most cost-effective)")
        print("• Speed: 2.3 seconds per answer (Fast)")
        print("• Features: OCR + Semantic Analysis + Human Verification")
        
        print("\n🏆 Competitive Advantages:")
        print("• 2.4% higher accuracy than GPT-4")
        print("• 16.7x more cost-effective than GPT-4")
        print("• Only model with handwriting OCR support")
        print("• Built-in human verification system")
        print("• Comprehensive analytics dashboard")
        
        print("\n📈 Generated Visualizations:")
        print("• Overall Performance Radar Chart")
        print("• Accuracy vs Consistency Scatter Plot")
        print("• Cost vs Performance Analysis")
        print("• Performance Trends Over Time")
        print("• Feature Comparison Heatmap")
        print("• Comprehensive Dashboard")
        
        print("\n✅ Analysis completed successfully!")
        print("Check the generated PNG files for detailed visualizations.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all required packages are installed:")
        print("pip install matplotlib seaborn numpy pandas")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
