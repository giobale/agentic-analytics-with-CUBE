# Frontend - Streamlit Data Analyst App

## Overview
This Streamlit application provides a web interface for the modular Data Analyst Agent. It allows users to upload CSV files and perform comprehensive data analysis through natural language queries.

## Features
- CSV file upload with automatic saving to `analyst-service/datasets/`
- Natural language query interface
- Comprehensive analysis reports with visualizations
- Interactive HTML charts and downloadable PNG images
- Analysis history tracking
- Download options for reports and summaries

## Setup and Running

### Prerequisites
- Python 3.8+
- Virtual environment activated from analyst-service
- All dependencies installed in analyst-service/venv (see README.md in analyst-service)

### Running the Application

1. **Activate the virtual environment** (from project root):
   ```bash
   cd analyst-service
   source venv/bin/activate
   ```

2. **Navigate to frontend directory**:
   ```bash
   cd ../frontend
   ```

3. **Run the Streamlit app**:
   ```bash
   streamlit run streamlit_analyst_app.py
   ```

4. **Access the application**:
   - Open your browser to `http://localhost:8501`
   - Upload a CSV file using the sidebar
   - Enter your analysis query
   - Click "Analyze Data" to start the analysis

## Usage Instructions

1. **Upload Data**: Use the file uploader in the sidebar to select your CSV file
2. **Enter Query**: Describe what analysis you want to perform (e.g., "Show me the correlation between sales and customer satisfaction")
3. **Run Analysis**: Click the "Analyze Data" button
4. **View Results**: Explore the results in the tabs:
   - **Report**: Comprehensive markdown analysis report
   - **Metrics**: Key calculated metrics
   - **Visualizations**: Interactive charts and graphs
   - **Conclusion**: Summary and recommendations
5. **Download**: Use the download buttons to save reports and summaries

## Architecture Integration

This frontend integrates with the modular analyst-service architecture:

- **File Storage**: Uploads are saved to `analyst-service/datasets/` with timestamped filenames
- **Analysis Engine**: Uses the modular `analyst_agent.run_full_agent()` function
- **Results**: Visualizations and outputs are generated in `analyst-service/results/`
- **Path Handling**: Automatically handles path resolution between frontend and analyst-service

## Error Handling

The application includes comprehensive error handling for:
- File upload failures
- Analysis execution errors
- Visualization rendering issues
- Path resolution problems

If you encounter import errors, ensure:
1. The virtual environment is properly activated
2. All dependencies are installed in `analyst-service/venv`
3. The analyst-service directory structure is intact

## Troubleshooting

**Import Errors**:
- Ensure you're running from the activated virtual environment
- Check that `analyst-service/src/` directory exists and contains required modules

**File Upload Issues**:
- Verify `analyst-service/datasets/` directory exists and is writable
- Check file format is CSV

**Analysis Failures**:
- Check OpenAI API key is configured in `analyst-service/.env`
- Ensure CSV file is properly formatted
- Review error messages in the Streamlit interface