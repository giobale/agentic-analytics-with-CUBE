# ABOUTME: Simple test runner for system prompt generation
# ABOUTME: Direct execution script to test the LLM integration system

import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import modules directly
from context_preparation.context_manager import ContextManager, ContextManagerError


def main():
    """Test the system prompt generation with the current YML file."""
    print("🚀 Testing LLM Integration System\n")

    try:
        # Initialize context manager - go up one level from tests directory
        base_path = Path(__file__).parent.parent
        manager = ContextManager(str(base_path))

        print(f"📂 Base path: {base_path}")
        print(f"📁 Views path: {manager.views_path}")

        # Check YML files
        yml_files = list(manager.views_path.glob("*.yml")) + list(manager.views_path.glob("*.yaml"))
        print(f"📄 Found {len(yml_files)} YML files: {[f.name for f in yml_files]}")

        if not yml_files:
            print("❌ No YML files found in my-cube-views directory")
            return False

        # Generate system prompt
        print("\n🤖 Generating system prompt...")
        result = manager.generate_system_prompt()

        system_prompt = result['system_prompt']
        metadata = result['metadata']

        print("✅ System prompt generated successfully!")
        print(f"📊 Metadata: {metadata}")
        print(f"📏 Prompt length: {len(system_prompt)} characters")

        # Save to results directory (now in same directory as script)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)

        output_file = results_dir / f"system_prompt_{timestamp}.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# SYSTEM PROMPT GENERATION TEST\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Metadata: {metadata}\n")
            f.write("\n" + "="*80 + "\n")
            f.write("# GENERATED SYSTEM PROMPT\n")
            f.write("="*80 + "\n\n")
            f.write(system_prompt)

        print(f"💾 System prompt saved to: {output_file}")

        # Print first few lines of the prompt
        print(f"\n📋 PROMPT PREVIEW (first 500 chars):")
        print("-" * 50)
        print(system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt)
        print("-" * 50)

        print(f"\n🎉 Test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)