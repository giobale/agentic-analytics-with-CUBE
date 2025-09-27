import streamlit as st
import pandas as pd
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
import asyncio
import base64
from typing import Optional, List, Dict, Any
import plotly.express as px
import json
import uuid
import logging
import time

# Add the analyst-service directory to Python path for imports
# Get the absolute path to the project root, then navigate to analyst-service
current_file_dir = os.path.dirname(os.path.abspath(__file__))  # frontend directory
project_root = os.path.dirname(current_file_dir)  # PoC-V1-CSV-Analyzer directory
analyst_service_root = os.path.join(project_root, 'analyst-service')
analyst_service_src = os.path.join(analyst_service_root, 'src')

# Add both paths to handle relative imports correctly
if analyst_service_root not in sys.path:
    sys.path.insert(0, analyst_service_root)
if analyst_service_src not in sys.path:
    sys.path.insert(0, analyst_service_src)

# Import from modular analyst service
from analyst_agent import run_full_agent

# Setup frontend logging
def setup_frontend_logging():
    """Setup logging for the Streamlit frontend with configuration from analyst service."""
    try:
        # Import config from analyst service
        sys.path.insert(0, os.path.join(os.path.dirname(current_file_dir), 'analyst-service', 'src'))
        from config import config

        # Get frontend configuration
        frontend_config = config.get_frontend_config()

        # Configure root logger to capture ALL logs (agent, tools, API calls)
        root_logger = logging.getLogger()

        # Only configure if not already configured
        if not root_logger.handlers:
            # Create formatter with component identification
            formatter = logging.Formatter(
                '[%(name)s] %(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # Create console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)

            # Set log level for root logger to capture everything
            log_level = getattr(logging, frontend_config['log_level'], logging.INFO)
            root_logger.setLevel(log_level)
            console_handler.setLevel(log_level)

            # Add handler to root logger
            root_logger.addHandler(console_handler)

            if frontend_config['debug']:
                root_logger.info(f"[FRONTEND] Root logging initialized with level: {frontend_config['log_level']}")
                root_logger.debug(f"[FRONTEND] Frontend configuration: {frontend_config}")

        # Configure specific logger for frontend messages
        frontend_logger = logging.getLogger('FRONTEND')
        frontend_logger.setLevel(getattr(logging, frontend_config['log_level'], logging.INFO))

        return frontend_logger, frontend_config
    except Exception as e:
        # Fallback logging setup
        root_logger = logging.getLogger()
        if not root_logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('[%(name)s] %(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            root_logger.addHandler(handler)
            root_logger.setLevel(logging.INFO)

        frontend_logger = logging.getLogger('FRONTEND')
        frontend_logger.warning(f"Failed to load analyst service config, using fallback logging: {str(e)}")
        return frontend_logger, {'debug': False, 'log_level': 'INFO', 'show_progress': False, 'log_request_ids': False}

# Initialize frontend logging
frontend_logger, frontend_config = setup_frontend_logging()

# for plot formating
import plotly.io as pio
pio.templates["custom"] = pio.templates["seaborn"]
pio.templates.default = "custom"
pio.templates["custom"].layout.autosize = True

# Page configuration
st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide"
)

def get_available_datasets():
    """Scan the analyst-service/datasets directory and return list of available CSV files"""
    frontend_logger.debug("Scanning for available datasets")
    try:
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_file_dir)
        datasets_dir = os.path.join(project_root, 'analyst-service', 'datasets')

        frontend_logger.debug(f"Checking datasets directory: {datasets_dir}")

        if not os.path.exists(datasets_dir):
            frontend_logger.warning("Datasets directory does not exist")
            return []

        # Get all CSV files, sorted by modification time (newest first)
        csv_files = []
        for file in os.listdir(datasets_dir):
            if file.endswith('.csv'):
                file_path = os.path.join(datasets_dir, file)
                # Get file modification time for sorting
                mod_time = os.path.getmtime(file_path)
                csv_files.append((file, mod_time))
                frontend_logger.debug(f"Found dataset: {file} (modified: {datetime.fromtimestamp(mod_time)})")

        # Sort by modification time (newest first)
        csv_files.sort(key=lambda x: x[1], reverse=True)

        # Return just the filenames
        dataset_list = [file[0] for file in csv_files]
        frontend_logger.info(f"Found {len(dataset_list)} datasets: {dataset_list}")
        return dataset_list

    except Exception as e:
        frontend_logger.error(f"Error scanning datasets directory: {str(e)}")
        st.error(f"Error scanning datasets directory: {str(e)}")
        return []

def get_dataset_info(dataset_filename):
    """Get basic information about a dataset file"""
    try:
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_file_dir)
        file_path = os.path.join(project_root, 'analyst-service', 'datasets', dataset_filename)

        if os.path.exists(file_path):
            # Get file size and modification time
            size = os.path.getsize(file_path)
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))

            # Try to get basic CSV info
            try:
                df = pd.read_csv(file_path, nrows=0)  # Just read headers
                columns = len(df.columns)
                return {
                    'size': size,
                    'modified': mod_time,
                    'columns': columns
                }
            except:
                return {
                    'size': size,
                    'modified': mod_time,
                    'columns': 'Unknown'
                }
        return None
    except Exception:
        return None


def get_history_file_path() -> str:
    """Get the path to the persistent history file"""
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_file_dir)
    history_dir = os.path.join(project_root, 'analyst-service', 'history')
    os.makedirs(history_dir, exist_ok=True)
    return os.path.join(history_dir, 'analysis_history.json')


def save_history_to_file(history_data: List[Dict[str, Any]]) -> None:
    """Save analysis history to persistent JSON file"""
    frontend_logger.debug(f"Saving {len(history_data)} analyses to history file")
    try:
        history_file = get_history_file_path()
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2, default=str)  # default=str handles datetime serialization
        frontend_logger.debug(f"History saved successfully to {history_file}")
    except Exception as e:
        frontend_logger.error(f"Error saving history: {str(e)}")
        st.error(f"Error saving history: {str(e)}")


def load_history_from_file() -> List[Dict[str, Any]]:
    """Load analysis history from persistent JSON file"""
    frontend_logger.debug("Loading analysis history from file")
    try:
        history_file = get_history_file_path()
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            frontend_logger.info(f"Loaded {len(history_data)} analyses from history")
            return history_data
        else:
            frontend_logger.debug("No history file found, starting with empty history")
            return []
    except Exception as e:
        frontend_logger.error(f"Error loading history: {str(e)}")
        st.warning(f"Error loading history: {str(e)}")
        return []


def analysis_to_dict(analysis, dataset_name: str, query: str) -> Dict[str, Any]:
    """Convert analysis result to dictionary for JSON serialization"""
    return {
        'id': str(uuid.uuid4()),  # Unique ID for each analysis
        'timestamp': datetime.now().isoformat(),
        'dataset_name': dataset_name,
        'query': query,
        'analysis_report': analysis.analysis_report,
        'metrics': analysis.metrics,
        'image_html_path': analysis.image_html_path,
        'image_png_path': analysis.image_png_path,
        'conclusion': analysis.conclusion
    }


def delete_analysis_from_history(analysis_id: str) -> None:
    """Delete a specific analysis from persistent history and its associated files"""
    frontend_logger.info(f"Deleting analysis from history: {analysis_id}")
    try:
        history_data = load_history_from_file()
        original_count = len(history_data)

        # Find the analysis to delete and get its file paths
        analysis_to_delete = None
        for analysis in history_data:
            if analysis.get('id') == analysis_id:
                analysis_to_delete = analysis
                break

        if not analysis_to_delete:
            frontend_logger.warning(f"Analysis {analysis_id} not found in history")
            return

        # Delete associated visualization files
        deleted_files = []
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_file_dir)
        analyst_service_dir = os.path.join(project_root, 'analyst-service')

        # Delete HTML file if it exists
        if analysis_to_delete.get('image_html_path'):
            html_path = os.path.join(analyst_service_dir, analysis_to_delete['image_html_path'])
            if os.path.exists(html_path):
                try:
                    os.remove(html_path)
                    deleted_files.append(f"HTML: {analysis_to_delete['image_html_path']}")
                    frontend_logger.debug(f"Deleted HTML file: {html_path}")
                except Exception as e:
                    frontend_logger.warning(f"Failed to delete HTML file {html_path}: {str(e)}")

        # Delete PNG file if it exists
        if analysis_to_delete.get('image_png_path'):
            png_path = os.path.join(analyst_service_dir, analysis_to_delete['image_png_path'])
            if os.path.exists(png_path):
                try:
                    os.remove(png_path)
                    deleted_files.append(f"PNG: {analysis_to_delete['image_png_path']}")
                    frontend_logger.debug(f"Deleted PNG file: {png_path}")
                except Exception as e:
                    frontend_logger.warning(f"Failed to delete PNG file {png_path}: {str(e)}")

        # Remove analysis from history
        updated_history = [analysis for analysis in history_data if analysis.get('id') != analysis_id]
        frontend_logger.debug(f"Removed analysis {analysis_id}, history count: {original_count} -> {len(updated_history)}")

        if deleted_files:
            frontend_logger.info(f"Deleted {len(deleted_files)} associated files: {', '.join(deleted_files)}")
        else:
            frontend_logger.debug("No associated files to delete")

        save_history_to_file(updated_history)

        # Update session state
        st.session_state.analysis_history = updated_history
        frontend_logger.info(f"Successfully deleted analysis {analysis_id} and associated files")

    except Exception as e:
        frontend_logger.error(f"Error deleting analysis {analysis_id}: {str(e)}")
        st.error(f"Error deleting analysis: {str(e)}")

# Initialize session state
frontend_logger.debug("Initializing Streamlit session state")

if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None
    frontend_logger.debug("Initialized current_analysis session state")

if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = load_history_from_file()  # Load persistent history
    frontend_logger.debug(f"Initialized analysis_history with {len(st.session_state.analysis_history)} items")
if 'uploaded_file_path' not in st.session_state:
    st.session_state.uploaded_file_path = None
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

# New session state for dataset selection
if 'available_datasets' not in st.session_state:
    st.session_state.available_datasets = get_available_datasets()
if 'selected_dataset' not in st.session_state:
    st.session_state.selected_dataset = None
if 'datasets_refreshed' not in st.session_state:
    st.session_state.datasets_refreshed = False

# Default dataset selection logic: select latest dataset if none selected and datasets exist
if not st.session_state.selected_dataset and st.session_state.available_datasets:
    st.session_state.selected_dataset = st.session_state.available_datasets[0]  # First is newest due to sorting

def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file to analyst-service/datasets directory and return path"""
    frontend_logger.info(f"Starting file upload: {uploaded_file.name} ({uploaded_file.size} bytes)")
    start_time = time.time()

    try:
        # Get the datasets directory path using consistent path calculation
        current_file_dir = os.path.dirname(os.path.abspath(__file__))  # frontend directory
        project_root = os.path.dirname(current_file_dir)  # PoC-V1-CSV-Analyzer directory
        datasets_dir = os.path.join(project_root, 'analyst-service', 'datasets')

        frontend_logger.debug(f"Target directory: {datasets_dir}")

        # Create datasets directory if it doesn't exist
        os.makedirs(datasets_dir, exist_ok=True)
        frontend_logger.debug("Ensured datasets directory exists")

        # Use original filename without timestamp to avoid duplication
        filename = uploaded_file.name
        file_path = os.path.join(datasets_dir, filename)

        frontend_logger.debug(f"Initial target path: {file_path}")

        # Check if file already exists and handle it
        if os.path.exists(file_path):
            frontend_logger.warning(f"File {filename} already exists, adding timestamp")
            # Only add timestamp if file with same name already exists
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            original_name = os.path.splitext(uploaded_file.name)[0]
            extension = os.path.splitext(uploaded_file.name)[1]
            filename = f"{original_name}_{timestamp}{extension}"
            file_path = os.path.join(datasets_dir, filename)
            frontend_logger.debug(f"Updated target path: {file_path}")

        # Save the file
        frontend_logger.debug("Writing file to disk")
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        upload_time = time.time() - start_time
        frontend_logger.info(f"File uploaded successfully: {filename} ({upload_time:.2f}s)")
        return filename

    except Exception as e:
        frontend_logger.error(f"Error saving file {uploaded_file.name}: {str(e)}")
        st.error(f"Error saving file: {str(e)}")
        return None

def main():
    frontend_logger.info("Starting Streamlit Data Analyst application")
    frontend_logger.debug(f"Frontend configuration: {frontend_config}")

    # Handle URL parameters from chat frontend
    query_params = st.query_params
    url_dataset = query_params.get('dataset', None)

    if url_dataset:
        frontend_logger.info(f"Received dataset from chat frontend: {url_dataset}")
        # Auto-select the dataset if it exists
        available_datasets = get_available_datasets()
        if url_dataset in available_datasets:
            st.session_state.selected_dataset = url_dataset
            frontend_logger.info(f"Auto-selected dataset: {url_dataset}")
            st.session_state.from_chat_frontend = True
        else:
            st.session_state.from_chat_frontend = False
    else:
        st.session_state.from_chat_frontend = False

    st.title("📊 AI Data Analyst")

    # Show special header if coming from chat frontend
    if st.session_state.get('from_chat_frontend', False):
        st.info(f"🔗 **Dataset loaded from Chat Frontend:** {st.session_state.selected_dataset}")
        st.markdown("---")
    else:
        st.markdown("Upload your CSV data and get comprehensive analysis with insights!")

    # Sidebar for dataset management
    with st.sidebar:
        st.header("📁 Dataset Management")

        # Upload new file section
        st.subheader("📋 Upload New File")
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="Upload your dataset in CSV format"
        )

        if uploaded_file is not None:
            # Check if this file was already processed to avoid reprocessing on rerun
            file_key = f"processed_{uploaded_file.name}_{uploaded_file.size}"
            if file_key not in st.session_state:
                frontend_logger.debug(f"Processing new file upload: {uploaded_file.name}")
                filename = save_uploaded_file(uploaded_file)
                if filename:
                    # Refresh available datasets and select the newly uploaded file
                    frontend_logger.debug("Refreshing available datasets after upload")
                    st.session_state.available_datasets = get_available_datasets()
                    st.session_state.selected_dataset = filename
                    st.session_state[file_key] = True  # Mark as processed
                    frontend_logger.info(f"File uploaded and selected: {filename}")
                    st.success(f"✅ File uploaded: {uploaded_file.name}")
                    st.rerun()  # Refresh to show new dataset in list
            else:
                frontend_logger.debug(f"File {uploaded_file.name} already processed, skipping")

        # Refresh datasets button
        if st.button("🔄 Refresh Datasets", help="Scan for new datasets"):
            st.session_state.available_datasets = get_available_datasets()
            if not st.session_state.selected_dataset and st.session_state.available_datasets:
                st.session_state.selected_dataset = st.session_state.available_datasets[0]
            st.rerun()

        st.divider()

        # Available datasets section
        st.subheader("📊 Available Datasets")

        if not st.session_state.available_datasets:
            st.info("🔍 No datasets found. Upload your first CSV file to get started!")
        else:
            st.write(f"📈 **{len(st.session_state.available_datasets)}** datasets available")

            # Dataset selection
            for dataset in st.session_state.available_datasets:
                # Create a container for each dataset
                dataset_info = get_dataset_info(dataset)
                is_selected = (dataset == st.session_state.selected_dataset)

                # Style the button differently if selected
                button_type = "primary" if is_selected else "secondary"
                button_text = f"{'✅' if is_selected else '📄'} {dataset}"

                if st.button(
                    button_text,
                    key=f"select_{dataset}",
                    type=button_type,
                    help=f"Select {dataset} for analysis" if not is_selected else "Currently selected dataset"
                ):
                    if not is_selected:
                        st.session_state.selected_dataset = dataset
                        st.session_state.current_analysis = None  # Clear previous analysis
                        st.rerun()

                # Show dataset info if selected
                if is_selected and dataset_info:
                    with st.container():
                        st.caption(f"📏 {dataset_info['columns']} columns | 📅 Modified: {dataset_info['modified'].strftime('%Y-%m-%d %H:%M')}")

        st.divider()

        # Clear selection button and history management
        if st.session_state.selected_dataset:
            col_clear, col_history = st.columns(2)
            with col_clear:
                if st.button("❌ Clear Selection", type="secondary"):
                    st.session_state.selected_dataset = None
                    st.session_state.current_analysis = None
                    st.rerun()

            with col_history:
                if st.button("🗑️ Clear All History", type="secondary", help="Delete all analysis history"):
                    if st.session_state.analysis_history:
                        # Delete all associated files for each analysis
                        deleted_files_count = 0
                        current_file_dir = os.path.dirname(os.path.abspath(__file__))
                        project_root = os.path.dirname(current_file_dir)
                        analyst_service_dir = os.path.join(project_root, 'analyst-service')

                        for analysis in st.session_state.analysis_history:
                            # Delete HTML file if it exists
                            if analysis.get('image_html_path'):
                                html_path = os.path.join(analyst_service_dir, analysis['image_html_path'])
                                if os.path.exists(html_path):
                                    try:
                                        os.remove(html_path)
                                        deleted_files_count += 1
                                        frontend_logger.debug(f"Deleted HTML file: {html_path}")
                                    except Exception as e:
                                        frontend_logger.warning(f"Failed to delete HTML file {html_path}: {str(e)}")

                            # Delete PNG file if it exists
                            if analysis.get('image_png_path'):
                                png_path = os.path.join(analyst_service_dir, analysis['image_png_path'])
                                if os.path.exists(png_path):
                                    try:
                                        os.remove(png_path)
                                        deleted_files_count += 1
                                        frontend_logger.debug(f"Deleted PNG file: {png_path}")
                                    except Exception as e:
                                        frontend_logger.warning(f"Failed to delete PNG file {png_path}: {str(e)}")

                        save_history_to_file([])  # Save empty history
                        st.session_state.analysis_history = []

                        frontend_logger.info(f"Cleared all history and deleted {deleted_files_count} associated files")
                        st.success(f"All analysis history cleared! ({deleted_files_count} files deleted)")
                        st.rerun()


    # Main interface - only show if dataset is selected
    if st.session_state.selected_dataset:
        # Show selected dataset info
        st.subheader(f"📊 Selected Dataset: {st.session_state.selected_dataset}")

        # Show dataset preview
        try:
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_file_dir)
            dataset_path = os.path.join(project_root, 'analyst-service', 'datasets', st.session_state.selected_dataset)

            if os.path.exists(dataset_path):
                dataset_preview = pd.read_csv(dataset_path, nrows=5)

                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("**📋 Dataset Preview**")
                    st.dataframe(dataset_preview, width='stretch')

                with col2:
                    dataset_info = get_dataset_info(st.session_state.selected_dataset)
                    if dataset_info:
                        st.markdown("**ℹ️ Dataset Info**")
                        st.write(f"📏 **Columns:** {dataset_info['columns']}")
                        st.write(f"📊 **Rows:** {len(pd.read_csv(dataset_path))}")
                        st.write(f"📅 **Modified:** {dataset_info['modified'].strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"💾 **Size:** {dataset_info['size']/1024:.1f} KB")

        except Exception as e:
            st.warning(f"Could not load dataset preview: {str(e)}")

        st.divider()

        # Analysis query input
        st.subheader("💬 Analysis Query")

        # Single query input field
        user_query = st.text_area(
            f"What would you like to analyze about **{st.session_state.selected_dataset}**?",
            placeholder="e.g., What are the key trends in the sales data? Show me correlations between different variables.",
            height=120,
            help="Describe what analysis you want to perform on the selected dataset"
        )

        # Analysis button
        analyze_button = st.button(
            "🔍 Analyze Data",
            type="primary",
            disabled=not user_query.strip(),
            help="Enter a query to start analysis"
        )

    else:
        # No dataset selected - show welcome message
        st.info("👈 **Select a dataset** from the sidebar to start your analysis!")

        if not st.session_state.available_datasets:
            st.markdown("""
            ### 🚀 Getting Started

            1. **Upload your first CSV file** using the sidebar
            2. **Select the dataset** you want to analyze
            3. **Write your analysis query** and let the AI do the work!

            The AI analyst can help you with:
            - 📈 Statistical analysis and insights
            - 📊 Data visualization and charts
            - 🔍 Pattern recognition and trends
            - 💡 Recommendations based on your data
            """)
        else:
            st.markdown("""
            ### 📊 Ready to Analyze!

            You have datasets available in the sidebar. Select one to:
            - 🔍 Explore your data with AI-powered analysis
            - 📈 Generate interactive visualizations
            - 💡 Discover insights and patterns
            - 📋 Get comprehensive reports
            """)

        analyze_button = False  # No analysis when no dataset selected
    
    
    if analyze_button and analyze_button is not False:
        if not st.session_state.selected_dataset:
            frontend_logger.warning("Analysis attempted without dataset selection")
            st.error("⚠️ Please select a dataset first")
        elif not user_query.strip():
            frontend_logger.warning("Analysis attempted without query")
            st.error("⚠️ Please enter an analysis query")
        else:
            # Generate request ID for correlation if enabled
            request_id = str(uuid.uuid4())[:8] if frontend_config.get('log_request_ids', False) else None
            request_info = f" [req_id: {request_id}]" if request_id else ""

            frontend_logger.info(f"Starting analysis{request_info}")
            frontend_logger.info(f"Dataset: {st.session_state.selected_dataset}")
            frontend_logger.info(f"Query: {user_query}")

            analysis_start_time = time.time()

            with st.spinner(f"🔄 Analyzing **{st.session_state.selected_dataset}**... This may take a few minutes."):
                try:
                    # Change to analyst-service directory for proper relative path handling
                    current_dir = os.getcwd()
                    current_file_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(current_file_dir)
                    analyst_service_dir = os.path.join(project_root, 'analyst-service')

                    frontend_logger.debug(f"Changing to analyst service directory: {analyst_service_dir}")

                    # Create the relative dataset path that the analyst service expects
                    dataset_relative_path = f"datasets/{st.session_state.selected_dataset}"
                    frontend_logger.debug(f"Using dataset path: {dataset_relative_path}")

                    if frontend_config.get('show_progress', False):
                        frontend_logger.info("Initiating agent analysis...")

                    try:
                        os.chdir(analyst_service_dir)
                        frontend_logger.debug("Working directory changed, calling run_full_agent")

                        # Run analysis with the relative dataset path
                        result = run_full_agent(user_query, dataset_relative_path)

                        frontend_logger.debug("Agent analysis completed")
                    finally:
                        # Always restore original directory
                        os.chdir(current_dir)
                        frontend_logger.debug("Working directory restored")

                    analysis_duration = time.time() - analysis_start_time

                    if result:
                        frontend_logger.info(f"Analysis completed successfully in {analysis_duration:.2f}s{request_info}")
                        st.session_state.current_analysis = result

                        # Convert analysis to dictionary and add to history
                        frontend_logger.debug("Converting analysis result for history storage")
                        analysis_dict = analysis_to_dict(result, st.session_state.selected_dataset, user_query)
                        st.session_state.analysis_history.append(analysis_dict)

                        # Save to persistent storage
                        frontend_logger.debug("Saving analysis to persistent history")
                        save_history_to_file(st.session_state.analysis_history)

                        frontend_logger.info(f"Analysis workflow completed{request_info}")
                        st.success(f"✅ Analysis of **{st.session_state.selected_dataset}** completed successfully!")
                    else:
                        frontend_logger.error(f"Analysis returned no result{request_info}")
                        st.error("❌ Analysis failed. Please try again.")

                except Exception as e:
                    analysis_duration = time.time() - analysis_start_time
                    frontend_logger.error(f"Analysis failed after {analysis_duration:.2f}s{request_info}: {str(e)}")
                    st.error(f"❌ Error during analysis: {str(e)}")

    st.markdown("--------------------------------")
    st.header("📊 Analysis Results")
        
    if st.session_state.current_analysis:
        analysis = st.session_state.current_analysis
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs(["📄 Report", "📈 Metrics", "🖼️ Visualizations", "💡 Conclusion"])
        
        with tab1:
            st.subheader("Analysis Report")
            if analysis.analysis_report:
                st.markdown(analysis.analysis_report)
            else:
                st.warning("No analysis report available")
        
        with tab2:
            st.subheader("Key Metrics")
            if analysis.metrics:
                for i, metric in enumerate(analysis.metrics, 1):
                    st.write(f"{i}. {metric}")
            else:
                st.warning("No metrics calculated")
        
        with tab3:
            st.subheader("Visualizations")

            # Try to display HTML first, fallback to PNG
            # Convert relative paths to absolute paths from analyst-service directory
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_file_dir)
            analyst_service_dir = os.path.join(project_root, 'analyst-service')

            if analysis.image_html_path:
                            try:
                                html_path = os.path.join(analyst_service_dir, analysis.image_html_path)
                                with open(html_path, 'r', encoding='utf-8') as f:
                                    html_content = f.read()
                                st.components.v1.html(html_content, height=500, scrolling=True)
                            except Exception as e:
                                st.error(f"Error displaying HTML: {str(e)}")

            elif analysis.image_png_path:
                png_path = os.path.join(analyst_service_dir, analysis.image_png_path)
                st.image(png_path)
            else:
                st.warning("No visualizations available")
        
        with tab4:
            st.subheader("Conclusion & Recommendations")
            if analysis.conclusion:
                st.markdown(analysis.conclusion)
            else:
                st.warning("No conclusion available")
        
        # Download options
        st.subheader("💾 Download Results")
        col_download1, col_download2 = st.columns(2)
        
        with col_download1:
            if analysis.analysis_report:
                st.download_button(
                    label="📥 Download Report (MD)",
                    data=analysis.analysis_report,
                    file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
        
        with col_download2:
            # Create a summary text for download
            file_display_name = st.session_state.selected_dataset
            summary_text = f"""
Analysis Summary
================
Query: {user_query}
File: {file_display_name}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Report:
{analysis.analysis_report}

Metrics:
{chr(10).join(f"• {metric}" for metric in analysis.metrics) if analysis.metrics else 'No metrics'}

Conclusion:
{analysis.conclusion}
"""
            st.download_button(
                label="📥 Download Summary (TXT)",
                data=summary_text,
                file_name=f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    else:
        st.info("👈 **Select a dataset** from the sidebar and **enter your analysis query** to see results here!")
        
    if st.session_state.analysis_history and len(st.session_state.analysis_history) > 0:
        st.header("📋 Analysis History")
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_file_dir)
        analyst_service_dir = os.path.join(project_root, 'analyst-service')

        # Show all analyses except current one (if it exists in history)
        history_to_show = st.session_state.analysis_history.copy()
        if (st.session_state.current_analysis and
            history_to_show and
            len(history_to_show) > 0):
            history_to_show = history_to_show[:-1]  # Remove last if it's current

        for analysis in reversed(history_to_show):  # Show newest first
            # Create header with query and delete button
            timestamp_str = datetime.fromisoformat(analysis['timestamp']).strftime('%Y-%m-%d %H:%M')

            # Create columns for title and delete button outside expander
            col_title, col_delete = st.columns([10, 1])

            with col_title:
                # Use query text as title, truncated if too long
                query_title = analysis['query']
                if len(query_title) > 80:
                    query_title = query_title[:77] + "..."
                st.markdown(f"**💬 {query_title}**")
                st.caption(f"📊 {analysis['dataset_name']} • {timestamp_str}")

            with col_delete:
                # Delete button with unique key - visible without opening expander
                if st.button("🗑️", key=f"delete_{analysis['id']}", help="Delete this analysis"):
                    delete_analysis_from_history(analysis['id'])
                    st.rerun()  # Refresh to show updated history

            # Expander for detailed content
            with st.expander("📄 View Analysis Details", expanded=False):
                st.markdown("**Analysis Report:**")
                st.markdown(analysis['analysis_report'])

                if analysis.get('metrics'):
                    st.markdown("**Metrics:**")
                    for i, metric in enumerate(analysis['metrics'], 1):
                        st.write(f"{i}. {metric}")

                if analysis.get('image_png_path'):
                    try:
                        png_path = os.path.join(analyst_service_dir, analysis['image_png_path'])
                        if os.path.exists(png_path):
                            st.image(png_path)
                    except Exception:
                        pass  # Ignore missing images

                if analysis.get('conclusion'):
                    st.markdown("**Conclusion:**")
                    st.markdown(analysis['conclusion'])

            st.divider()  # Visual separation between analyses

if __name__ == "__main__":
    main()