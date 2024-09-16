# InsightStreamAI

InsightStreamAI is an intuitive, secure business intelligence platform that empowers non-technical users to interact with their data through natural language queries. It provides a user-friendly interface for exploring data, generating insights, and making data-driven decisions without requiring coding skills.

## Features

- **Natural Language Data Interaction**: Ask business questions in plain language
- **Secure Data Connections**: Supports Google Sheets and PostgreSQL databases
- **AI-Powered Analysis**: Generate insights, spot trends, and answer complex business questions
- **Interactive Visualizations**: Automatically generate and interact with relevant charts and graphs
- **Dashboard Integration**: High-level dashboard with seamless transition to detailed analysis
- **Data Security**: Keep sensitive data within your control, mitigating risks of data leakage

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/insightstreamai.git
   cd insightstreamai
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service_account.json
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run main.py
   ```

2. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

3. In the sidebar:
   - Enter your OpenAI API key (if not set in .env file)
   - Provide Google Sheet ID and Sheet Name, or PostgreSQL connection details
   - Click "Connect to Sheet" or "Connect to Database"

4. Navigate through the tabs:
   - **Home**: Overview and quick start guide
   - **Analysis**: Ask questions about your data and view insights
   - **Dashboard**: View high-level metrics and visualizations

## Configuration

- **Google Sheets**: Ensure your Google Service Account JSON file is correctly set up and has access to the desired Google Sheets.
- **PostgreSQL**: Make sure you have the necessary credentials and network access to connect to your PostgreSQL database.

## Security Notes

- This application processes data locally and does not send your raw data to external services (except for the natural language processing through OpenAI's API).
- Ensure that your OpenAI API key and database credentials are kept secure and not shared publicly.

## Contributing

Contributions to InsightStreamAI are welcome! Please refer to our [Contributing Guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please file an issue on the GitHub issue tracker.

---

Built with ❤️ using Streamlit, OpenAI GPT, and Python.
