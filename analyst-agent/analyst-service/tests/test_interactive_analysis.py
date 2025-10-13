# ABOUTME: Interactive test script for the Data Analyst Agent with user queries
# ABOUTME: Tests the core functionality of processing user analysis questions

# Set matplotlib backend before any other imports to prevent macOS GUI threading issues
import matplotlib
matplotlib.use('Agg')

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Configure logging for testing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def list_available_datasets():
    """List available CSV files in the datasets directory."""
    datasets_dir = Path(__file__).parent.parent / "datasets"
    csv_files = list(datasets_dir.glob("*.csv"))

    if not csv_files:
        print("❌ No CSV files found in datasets/ folder")
        return []

    print("\n📁 Available datasets:")
    for i, csv_file in enumerate(csv_files, 1):
        print(f"  {i}. {csv_file.name}")

    return csv_files


def get_user_input():
    """Get user query and dataset selection."""
    print("\n" + "="*60)
    print("🤖 DATA ANALYST AGENT - INTERACTIVE TEST")
    print("="*60)

    # Show available datasets
    csv_files = list_available_datasets()
    if not csv_files:
        return None, None

    # Get dataset selection
    while True:
        try:
            choice = input(f"\nSelect dataset (1-{len(csv_files)}): ")
            dataset_index = int(choice) - 1
            if 0 <= dataset_index < len(csv_files):
                selected_dataset = csv_files[dataset_index]
                break
            else:
                print(f"Please enter a number between 1 and {len(csv_files)}")
        except ValueError:
            print("Please enter a valid number")

    print(f"\n✅ Selected dataset: {selected_dataset.name}")

    # Get user query
    print("\n💬 Enter your analysis question:")
    print("Examples:")
    print("  • What are the key patterns in this data?")
    print("  • Show me the correlation between different variables")
    print("  • What insights can you provide about trends over time?")
    print("  • Identify any outliers or anomalies in the data")

    user_query = input("\n🔍 Your question: ").strip()

    if not user_query:
        print("❌ Query cannot be empty")
        return None, None

    return user_query, str(selected_dataset)


def save_interactive_results(result, user_query, dataset_name, timestamp):
    """Save the interactive analysis results."""
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    # Create safe filename from user query (first 50 chars, alphanumeric only)
    safe_query = "".join(c for c in user_query[:50] if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_query = safe_query.replace(' ', '_')

    # Save comprehensive results
    result_file = results_dir / f"interactive_{safe_query}_{dataset_name}_{timestamp}.md"

    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(f"# Interactive Analysis Results\n\n")
        f.write(f"**User Query**: {user_query}\n")
        f.write(f"**Dataset**: {dataset_name}\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        f.write("## Analysis Report\n\n")
        f.write(result.analysis_report)
        f.write("\n\n")

        f.write("## Metrics\n\n")
        for i, metric in enumerate(result.metrics, 1):
            f.write(f"{i}. {metric}\n")
        f.write("\n")

        f.write("## Visualization Files\n\n")
        f.write(f"- **HTML**: {result.image_html_path}\n")
        f.write(f"- **PNG**: {result.image_png_path}\n\n")

        f.write("## Conclusion\n\n")
        f.write(result.conclusion)

    return result_file


def run_interactive_test():
    """Run interactive test with user-provided query."""
    try:
        # Get user input
        user_query, dataset_path = get_user_input()
        if not user_query or not dataset_path:
            return False

        print(f"\n🚀 Starting analysis...")
        print(f"📊 Query: {user_query}")
        print(f"📁 Dataset: {Path(dataset_path).name}")

        # Import and run the agent
        from src.analyst_agent import run_full_agent

        # Execute the analysis
        result = run_full_agent(user_query, dataset_path)

        # Display results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print(f"\n{'='*60}")
        print("📈 ANALYSIS COMPLETED SUCCESSFULLY!")
        print('='*60)

        print(f"\n📊 ANALYSIS REPORT:")
        print("-" * 40)
        print(result.analysis_report)

        print(f"\n📈 METRICS ({len(result.metrics)} total):")
        print("-" * 40)
        for i, metric in enumerate(result.metrics, 1):
            print(f"  {i}. {metric}")

        print(f"\n🖼️  VISUALIZATIONS:")
        print("-" * 40)
        print(f"  HTML: {result.image_html_path}")
        print(f"  PNG:  {result.image_png_path}")

        print(f"\n📝 CONCLUSION:")
        print("-" * 40)
        print(result.conclusion)

        # Save results
        result_file = save_interactive_results(
            result, user_query, Path(dataset_path).stem, timestamp
        )

        print(f"\n💾 Results saved to: {result_file}")
        print(f"\n✅ Interactive test completed successfully!")

        # Ask if user wants to run another test
        another = input(f"\n❓ Run another analysis? (y/n): ").strip().lower()
        if another in ['y', 'yes']:
            return run_interactive_test()

        return True

    except KeyboardInterrupt:
        print(f"\n\n👋 Test cancelled by user")
        return False

    except Exception as e:
        print(f"\n❌ Interactive test failed: {str(e)}")
        logger.error(f"Interactive test error: {str(e)}")
        return False


if __name__ == "__main__":
    print("🔬 Starting Interactive Data Analyst Agent Test")
    success = run_interactive_test()

    if success:
        print(f"\n🎉 All tests completed!")
    else:
        print(f"\n💥 Test session ended")

    sys.exit(0 if success else 1)