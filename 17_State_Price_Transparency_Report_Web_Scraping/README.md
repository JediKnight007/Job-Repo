# SPTR (State Prescription Drug Pricing Transparency) Analysis System

## Executive Summary

The SPTR Analysis System is a comprehensive Python-based automation platform designed to monitor, analyze, and visualize prescription drug pricing transparency legislation across all 50 U.S. states. The system combines web scraping, data processing, predictive analytics, and interactive visualization to provide pharmaceutical companies with critical compliance intelligence regarding state-level reporting requirements.

### Web Scraping Foundation

At the core of the system lies a sophisticated web scraping infrastructure that automatically collects legislative data from authoritative sources. The platform primarily targets the National Academy for State Health Policy (NASHP) websites, which serve as centralized repositories aggregating prescription drug pricing transparency laws from all states. This strategic choice eliminates the need to maintain 50+ individual state website scrapers, each with unique structures and authentication requirements.

The scraping engine employs BeautifulSoup for HTML parsing, navigating complex DOM structures to extract state names, bill numbers, law references, legislative links, and descriptive text from tabular data and structured content. It processes two primary NASHP resources: a comprehensive comparison chart displaying state-by-state legislation in tabular format, and an implementation page containing state-specific resources organized by headings and lists. The scraper uses intelligent pattern matching to identify legislative documents through keyword detection (bill, law, act, chapter, statute, and various legislative prefixes), validates extracted data against known state names, and resolves relative URLs to absolute references for complete traceability.

To ensure reliable operation, the scraping system implements robust error handling with configurable retry mechanisms, maintains persistent HTTP sessions to preserve authentication state, and configures realistic browser headers to avoid detection. All scraped data is immediately persisted to JSON format, enabling the system to resume from cached data if fresh scraping encounters issues, while also supporting manual data updates when needed.

### Utilization of Scraped Data

The scraped legislative data serves as the foundation for multiple downstream processes that transform raw web content into actionable business intelligence. Upon collection, the system applies sophisticated relevance scoring algorithms that analyze bill descriptions, titles, and metadata to determine how closely each piece of legislation relates to prescription drug pricing transparency. Bills are automatically categorized and filtered, with only those meeting minimum relevance thresholds (typically scoring 5.0 or higher on a 0-10 scale) proceeding to the analysis phase.

This filtered legislative data is then integrated with product pricing information and state-specific rules to create a comprehensive compliance intelligence system. The scraped bills appear in detailed reports showing which states have active legislation, what specific laws govern pricing transparency, and when reporting deadlines occur. In the interactive dashboard, users can click on any state to view all related legislative bills that were scraped, including bill numbers, descriptions, direct links to source documents, and relevance scores.

Beyond simple display, the scraped data enables strategic analysis by identifying emerging legislative trends, tracking new bill introductions, and monitoring changes in existing laws. The system maintains historical versions of scraped data, allowing users to compare legislative landscapes over time and identify states that have recently introduced or modified pricing transparency requirements. This temporal analysis helps pharmaceutical companies anticipate regulatory changes and prepare compliance strategies proactively.

The integration of scraped legislative data with product pricing calculations creates a powerful compliance determination engine. When the system identifies that a product's price increase exceeds state thresholds, it can immediately reference the scraped legislation to provide context: which specific laws apply, what reporting requirements exist, when reports are due, and what information must be included. This seamless connection between raw legislative text scraped from websites and actionable compliance intelligence eliminates manual research and reduces the risk of missing critical regulatory requirements.

### End-to-End Workflow

The platform automatically tracks legislative changes through scheduled scraping operations, calculates price increase triggers based on state-specific thresholds derived from both scraped legislation and configured state rules, identifies products requiring compliance reporting, and generates detailed visualizations and reports. The entire workflow—from web scraping through report generation—operates as an integrated pipeline, ensuring that the most current legislative information informs all compliance calculations and strategic decisions.

This end-to-end automation transforms what would otherwise require extensive manual research across 50+ state websites into a streamlined, automated process that delivers comprehensive compliance intelligence. The system serves as a complete solution for managing complex state regulatory requirements in the rapidly evolving landscape of prescription drug pricing transparency laws, where new legislation emerges frequently and existing laws are regularly amended.

---

## System Architecture

### Core Components

The system is built on a modular architecture with distinct components handling specific responsibilities:

**Data Acquisition Layer**: Responsible for web scraping legislative data from authoritative sources, primarily the National Academy for State Health Policy (NASHP) websites, which aggregate prescription drug pricing transparency laws from all states.

**Data Processing Engine**: Processes raw scraped data, filters relevant legislation, and performs complex calculations to determine which products trigger reporting requirements based on state-specific rules and thresholds.

**Calculation Module**: Implements sophisticated algorithms that compare product pricing data against state-specific thresholds, considering multiple time periods (1-year, 2-year, 3-year, and 5-year lookbacks) and various drug classifications (brand, generic, biosimilar).

**Visualization Framework**: Creates interactive choropleth maps and trend charts using Plotly, enabling users to explore data geographically and temporally through an intuitive web interface.

**Automation Pipeline**: Orchestrates the entire workflow from data collection through report generation, with scheduling capabilities for automated daily, weekly, or custom interval execution.

**Historical Data Management**: Maintains versioned copies of all outputs with timestamped metadata, enabling trend analysis and predictive forecasting over time.

---

## Web Scraping Implementation

### Primary Data Source: NASHP

The system leverages the National Academy for State Health Policy (NASHP) as its primary data source because it aggregates prescription drug pricing transparency legislation from all states in centralized locations. This approach is significantly more efficient than scraping individual state legislative websites, which would require maintaining 50+ different scraping configurations and dealing with varying website structures.

### Scraping Methodology

**HTML Parsing with BeautifulSoup**: The scraper utilizes BeautifulSoup, a powerful Python library for parsing HTML and XML documents. It navigates the Document Object Model (DOM) tree to extract structured data from web pages, handling various HTML structures and edge cases.

**HTTP Session Management**: The system employs Python's requests library with persistent session objects to maintain cookies and headers across multiple requests. This ensures proper authentication and prevents blocking by websites that detect automated access.

**User-Agent Spoofing**: To avoid detection and blocking, the scraper configures realistic browser headers, including User-Agent strings that mimic standard web browsers, ensuring compatibility with websites that filter automated traffic.

**State Data Extraction from Comparison Chart**: The scraper targets NASHP's comparison chart page, which contains tabular data with state information. It identifies HTML table elements, iterates through table rows, and extracts state names from table cells. The system then searches for hyperlinks within these rows that contain keywords indicating legislative documents (such as "bill", "law", "act", "chapter", "statute", "public", and various bill prefixes like "ld", "hb", "sb", "ab").

**Implementation Page Resource Extraction**: A secondary scraping target is NASHP's implementation page, which contains state-specific resources organized by headings. The scraper uses regular expression pattern matching to identify headings that follow the pattern "[State Name] Resources", then traverses the DOM tree to find associated list elements containing links to bills, laws, PDFs, and other relevant documents.

**Link Resolution and Validation**: All extracted links are resolved to absolute URLs using Python's urljoin functionality, ensuring that relative URLs are properly converted. The system validates state names against a comprehensive list of all 50 U.S. states to filter out false positives and navigation links.

**Deduplication Logic**: The scraper implements sophisticated deduplication algorithms that compare bills based on multiple attributes: state name, bill number, and URL. This prevents duplicate entries when the same legislation appears in multiple sources or pages.

**Error Handling and Retry Mechanisms**: The scraping system includes robust error handling with configurable retry attempts and exponential backoff delays. When a request fails, the system logs the error, waits a specified interval, and retries the operation up to a configured maximum number of attempts.

**Data Persistence**: Scraped data is immediately saved to JSON format, allowing the system to resume from existing data if scraping fails or if users prefer to use cached data. The system can merge new scraped data with existing datasets, preserving historical information while updating with fresh content.

### Fallback Configuration

While NASHP is the primary source, the system maintains configuration files for individual state legislative websites as fallback options. These configurations specify URLs, search terms, and pagination limits for each state's legislative search interface. This architecture allows the system to adapt if NASHP becomes unavailable or if users require more granular state-specific data.

---

## Data Processing Pipeline

### Legislative Bill Filtering

**Relevance Scoring Algorithm**: The system implements a sophisticated relevance scoring mechanism that analyzes bill descriptions, titles, and metadata to determine how closely they relate to prescription drug pricing transparency. The algorithm uses keyword matching, phrase detection, and contextual analysis to assign numerical relevance scores.

**Categorization**: Bills are automatically categorized based on their content, with primary focus on "prescription_drug_pricing" classification. The system filters out irrelevant legislation, keeping only bills that meet a minimum relevance threshold (typically 5.0 on a 0-10 scale).

**Metadata Extraction**: For each relevant bill, the system extracts comprehensive metadata including bill numbers, descriptions, URLs, source information, scraping timestamps, and state associations. This metadata enables traceability and audit trails for compliance purposes.

### State Rules Parsing

**Multi-Encoding Support**: The State Rules CSV file may be encoded in various formats (UTF-8, Latin-1, CP1252, ISO-8859-1). The parser attempts multiple encodings automatically, ensuring compatibility with files created in different environments or exported from various systems.

**Structured Rule Objects**: State rules are parsed into structured dataclass objects that encapsulate all relevant information: state name and acronym, drug type classifications, threshold values for different time periods, WAC (Wholesale Acquisition Cost) requirements, report types, due dates, and special notes.

**Threshold Extraction**: The parser extracts multiple threshold types from the CSV, including 1-year, 2-year, 3-year, and 5-year price increase thresholds. It also identifies minimum WAC requirements that must be met before a product becomes subject to reporting obligations.

**Reference Year Logic**: The system parses complex reference year descriptions that specify which historical periods should be used for comparison. Some states use calendar years, while others use rolling periods, and the parser handles both scenarios.

### Product Data Processing

**Flexible Column Mapping**: The product data processor handles variations in CSV structure, mapping columns with different names to standardized internal representations. It supports both "Current WAC" and "Current List Price" columns, automatically selecting the appropriate field based on availability.

**Historical Price Parsing**: The system extracts historical pricing data from multiple columns representing prices at different time points (1 year ago, 2 years ago, etc.). It handles missing data gracefully, using available historical points for calculations.

**Forecast Interpretation**: Forecast data may be provided as dollar amounts or percentages, and the system automatically detects and parses both formats. It converts percentage forecasts to absolute dollar values when necessary for calculations.

**Data Validation**: All product data undergoes validation to ensure price values are numeric, dates are properly formatted, and required fields are present. Invalid records are flagged and excluded from calculations with appropriate logging.

---

## SPTR Calculation Engine

### Trigger Determination Logic

**Multi-Period Analysis**: The calculation engine evaluates price increases across multiple time periods simultaneously. For each product-state combination, it calculates percentage increases over 1-year, 2-year, 3-year, and 5-year periods, comparing each against the corresponding state threshold.

**Threshold Comparison**: The system compares calculated price increases against state-specific thresholds, which vary by state, drug type (brand, generic, biosimilar), and time period. A product triggers a reporting requirement if its price increase exceeds the threshold for the relevant period.

**WAC Minimum Requirements**: Before evaluating price increases, the system checks whether products meet minimum WAC thresholds specified by each state. Products below the minimum WAC are excluded from reporting requirements regardless of price increase magnitude.

**Drug Type Filtering**: States often have different rules for brand drugs, generic drugs, and biosimilars. The calculation engine applies the appropriate thresholds based on product classification, ensuring accurate compliance determination.

**Calendar Year vs. Rolling Period Logic**: The system handles two different temporal calculation methods: calendar year comparisons (comparing current prices to prices on the same date in previous years) and rolling period comparisons (comparing to prices exactly N years ago regardless of calendar boundaries).

### Calculation Workflow

**State-by-State Processing**: The engine processes each state independently, loading the appropriate state rules and applying them to all products in the dataset. This ensures that state-specific nuances are properly handled.

**Product Iteration**: For each product, the system retrieves current pricing, historical pricing, and forecast data. It then calculates all relevant price increases and compares them against applicable thresholds.

**Trigger Aggregation**: When multiple triggers occur for the same product-state combination (e.g., both 1-year and 2-year thresholds are exceeded), the system aggregates these into comprehensive trigger reports, indicating which specific thresholds were exceeded.

**Result Compilation**: All trigger determinations are compiled into detailed DataFrames that include product information, state information, calculated price increases, threshold values, trigger status, and metadata about which specific rules were applied.

---

## Python Functionalities and Libraries

### Data Manipulation and Analysis

**Pandas**: The entire system is built on Pandas DataFrames for data manipulation. Pandas provides powerful capabilities for reading CSV files, filtering data, grouping and aggregating, merging datasets, and exporting results. The system leverages Pandas' vectorized operations for efficient processing of large datasets containing thousands of products and multiple states.

**NumPy**: Numerical computations, particularly for price calculations and statistical aggregations, utilize NumPy arrays and functions. NumPy's optimized mathematical operations ensure fast processing of price increase calculations across large datasets.

### Web Scraping and HTTP Requests

**Requests Library**: All HTTP interactions use the requests library, which provides a clean API for making GET and POST requests, handling cookies, managing sessions, and processing responses. The system uses persistent session objects to maintain state across multiple requests.

**BeautifulSoup4**: HTML parsing relies on BeautifulSoup4, which provides intuitive methods for navigating HTML structures, finding elements by tags, attributes, or text content, and extracting data from complex nested structures.

**Regular Expressions (re module)**: Pattern matching for state name extraction, bill number identification, and text parsing uses Python's built-in regular expression module. Regex patterns enable flexible matching of legislative document identifiers and state-specific formatting variations.

### Configuration Management

**PyYAML**: Configuration files are managed using YAML format, parsed with PyYAML. This allows human-readable configuration of scraping parameters, scheduling intervals, data source paths, and system behavior without requiring code changes.

### Scheduling and Automation

**APScheduler**: Advanced Python Scheduler (APScheduler) provides robust job scheduling capabilities, supporting cron-style scheduling, interval-based execution, and timezone-aware scheduling. The system uses APScheduler to automate daily, weekly, or custom-interval pipeline execution.

**Schedule Library**: As an alternative scheduling mechanism, the system also supports the schedule library for simpler interval-based scheduling scenarios.

### Data Visualization

**Plotly**: Interactive visualizations are created using Plotly, which generates JavaScript-based interactive charts that can be embedded in web pages or exported as static images. The system uses Plotly's choropleth map functionality to create state-level heat maps and scatter plots for trend analysis.

**Plotly Express**: For rapid chart creation, the system leverages Plotly Express, which provides high-level functions for common chart types with minimal code.

### Machine Learning and Predictive Analytics

**Scikit-learn**: When available, the system uses scikit-learn's LinearRegression and PolynomialFeatures for trend analysis and predictive forecasting. The system gracefully degrades to basic linear regression if scikit-learn is unavailable.

**NumPy for Statistical Operations**: Statistical calculations, including moving averages, standard deviations, and correlation analysis, utilize NumPy's statistical functions.

### Web Application Framework

**Streamlit**: The interactive dashboard is built on Streamlit, a Python framework that enables rapid development of web applications. Streamlit handles session state management, widget creation, layout management, and automatic reruns when user interactions occur.

**Streamlit Components**: Custom components extend Streamlit's functionality, particularly for handling Plotly chart interactions and capturing user clicks on map visualizations.

### Data Serialization

**JSON Module**: All data persistence uses JSON format, leveraging Python's built-in json module for serializing and deserializing complex data structures. JSON provides human-readable storage while maintaining compatibility with web technologies.

**CSV Handling**: While Pandas handles most CSV operations, the system also uses Python's built-in csv module for edge cases requiring fine-grained control over CSV parsing and writing.

### File System Operations

**Pathlib**: Modern file path operations use Pathlib, which provides object-oriented path manipulation that is more intuitive and cross-platform compatible than traditional string-based path operations.

**OS and Shutil Modules**: File system operations, directory creation, file copying, and cleanup tasks utilize Python's os and shutil modules for comprehensive file management.

### Logging and Error Handling

**Logging Module**: Comprehensive logging throughout the system uses Python's built-in logging module with configurable log levels, file rotation, and formatted output. Logs capture scraping activities, calculation results, errors, and system state information.

**Exception Handling**: Robust try-except blocks throughout the codebase handle network errors, parsing failures, data validation issues, and file system problems, ensuring the system continues operating even when individual components encounter issues.

### Type Hints and Data Structures

**Typing Module**: The codebase extensively uses Python's typing module for type hints, improving code readability, enabling static type checking, and providing better IDE support. Type hints specify expected parameter types, return types, and complex data structures.

**Dataclasses**: State rules and configuration objects are implemented as dataclasses, providing automatic generation of initialization methods, string representations, and comparison operators while maintaining clean, readable code.

**Collections Module**: Specialized data structures from the collections module, such as defaultdict, are used for efficient data aggregation and grouping operations.

---

## Visualization and Dashboard

### Interactive Choropleth Maps

**State-Level Heat Maps**: The system generates two primary choropleth maps: one showing active legislation by state (indicating which states have prescription drug pricing transparency laws) and another showing product price impact by state (indicating which states are affected by product price combinations).

**Color Gradient Encoding**: States are colored using gradient scales that represent quantitative values. The legislation map uses blue gradients (light to dark) based on trigger counts, while the impact map uses yellow-to-red gradients representing impact severity.

**Hover Information**: Interactive tooltips display detailed information when users hover over states, including state names, trigger counts, product counts, and specific threshold values.

**Click Interaction**: Users can click directly on states in the maps to view comprehensive state-specific information, including detailed trigger breakdowns, related bills, products impacted, state rules, and trend analysis.

### Trend Analysis Charts

**Time Series Visualization**: The system generates Plotly scatter plots showing trigger trends over time, with multiple lines representing different trigger types (Trigger 1, Trigger 2, Trigger 3, and Total Triggers).

**Forecast Visualization**: Predictive forecasts are displayed as dashed lines extending beyond historical data, providing visual indication of expected future trends.

**Dual-Axis Charts**: Some visualizations combine time series data with bar charts on secondary axes, showing both trend information and current state values simultaneously.

**Interactive Features**: All trend charts support zooming, panning, and data point inspection, allowing users to explore specific time periods and values in detail.

### Dashboard Architecture

**Tab-Based Interface**: The Streamlit dashboard organizes content into tabs, separating legislation-focused views from price impact views while maintaining shared state information.

**Session State Management**: Streamlit's session state mechanism maintains user selections, map type preferences, and data across page reruns, ensuring consistent user experience during interactions.

**Responsive Layout**: The dashboard uses Streamlit's column layout system to create responsive designs that adapt to different screen sizes, with maps and information panels arranged side-by-side.

**Real-Time Updates**: When users interact with maps (clicking states), the dashboard automatically reruns and updates displayed information, providing immediate feedback without page refreshes.

---

## Automation and Scheduling

### Pipeline Orchestration

**Sequential Workflow**: The automation pipeline executes tasks in a carefully orchestrated sequence: data scraping, bill filtering, product data loading, state rules parsing, trigger calculations, report generation, visualization creation, and data versioning.

**Dependency Management**: Each pipeline stage checks for required inputs and validates data before proceeding, ensuring that failures in early stages don't cause cascading errors in later stages.

**Progress Logging**: Throughout pipeline execution, comprehensive logging captures progress, timing information, data volumes processed, and any issues encountered, enabling troubleshooting and performance monitoring.

### Scheduling Configuration

**Flexible Intervals**: The scheduler supports multiple execution patterns: daily runs at specified times, weekly runs on specific days, hourly intervals, or custom cron-style schedules for complex timing requirements.

**Timezone Awareness**: All scheduling is timezone-aware, ensuring that jobs execute at the correct local times regardless of server location.

**Graceful Shutdown**: The scheduler handles application shutdown gracefully, allowing running jobs to complete before termination.

### Data Versioning

**Timestamped Archives**: Every pipeline execution creates timestamped directories containing all output files, enabling historical analysis and rollback capabilities.

**Metadata Tracking**: Each versioned dataset includes metadata files containing run timestamps, data volumes, processing statistics, and configuration snapshots used during that run.

**Automatic Cleanup**: The system automatically removes old data versions beyond a configurable retention period (default 30 days), preventing unlimited disk space consumption while preserving recent history.

**Version Comparison**: The system can compare data across versions to identify changes, new triggers, or data quality issues over time.

---

## Data Flow and Integration

### End-to-End Workflow

**Data Ingestion**: The system begins by loading configuration files, identifying states to process, and determining data source locations. It then initiates web scraping or loads existing scraped data based on configuration.

**Data Transformation**: Raw scraped data undergoes filtering and relevance scoring. Product data is normalized and validated. State rules are parsed into structured objects. All data is prepared for calculation processing.

**Calculation Execution**: The calculation engine processes each product-state combination, applying appropriate rules, performing price increase calculations, and determining trigger status. Results are aggregated at multiple levels: product-state detail, state summary, and overall statistics.

**Output Generation**: Multiple output formats are generated simultaneously: detailed CSV files for analysis, summary CSV files for reporting, Excel workbooks with multiple sheets, JSON files for programmatic access, and HTML visualizations for presentation.

**Historical Archiving**: All outputs are automatically copied to timestamped directories in the data history folder, preserving a complete audit trail of all system executions.

**Dashboard Updates**: The Streamlit dashboard reads from the latest output files, automatically reflecting new calculations and visualizations without requiring manual refresh or restart.

### Integration Points

**File-Based Integration**: The system integrates with external tools through standardized file formats (CSV, JSON, Excel), allowing other systems to consume outputs without direct API dependencies.

**Configuration-Driven Behavior**: All system behavior is controlled through YAML configuration files, enabling customization without code modifications and supporting multiple deployment scenarios.

**Log-Based Monitoring**: Comprehensive logging enables integration with log aggregation systems, monitoring tools, and alerting frameworks for operational visibility.

---

## Advanced Features

### Trend Analysis and Forecasting

**Historical Data Aggregation**: The trend analyzer loads data from multiple historical runs, aggregating by state and date to create time series datasets suitable for analysis.

**Statistical Modeling**: When scikit-learn is available, the system uses linear regression and polynomial features to model trends and generate forecasts. When unavailable, it falls back to simpler moving average calculations.

**Multi-Trigger Analysis**: Trend analysis considers all trigger types independently, providing separate forecasts for different trigger categories and enabling identification of emerging patterns.

**Confidence Intervals**: Forecast visualizations include confidence bands or ranges, indicating uncertainty in predictions and helping users understand forecast reliability.

### Error Recovery and Resilience

**Fallback Mechanisms**: The system includes multiple fallback strategies: if scraping fails, it uses existing data; if primary data files are missing, it attempts alternative sources; if calculations fail for specific products, it continues processing others.

**Data Validation**: Extensive validation checks ensure data quality at every stage, with clear error messages and logging when issues are detected.

**Graceful Degradation**: When optional components (like scikit-learn) are unavailable, the system continues operating with reduced functionality rather than failing completely.

### Performance Optimization

**Efficient Data Structures**: The system uses appropriate data structures (DataFrames for tabular data, dictionaries for lookups, sets for membership testing) to optimize performance for large datasets.

**Lazy Loading**: Data is loaded only when needed, and large datasets are processed in chunks when possible to minimize memory usage.

**Caching Strategies**: Scraped data and parsed state rules are cached to avoid redundant processing during the same execution or across multiple runs.

---

## System Capabilities Summary

The SPTR Analysis System represents a comprehensive solution for managing prescription drug pricing transparency compliance across all U.S. states. It combines sophisticated web scraping capabilities, complex calculation logic, predictive analytics, and intuitive visualization to provide pharmaceutical companies with actionable intelligence about regulatory requirements.

The system's modular architecture, extensive error handling, and configuration-driven design make it adaptable to changing requirements and robust in production environments. Its automation capabilities reduce manual effort while ensuring timely compliance monitoring, and its historical data management enables trend analysis and strategic planning.

By leveraging Python's rich ecosystem of libraries for data processing, web scraping, visualization, and automation, the system delivers enterprise-grade functionality while maintaining code clarity and maintainability. The integration of modern web technologies (Streamlit, Plotly) provides an accessible user interface that makes complex regulatory data understandable and actionable for business users.

---

## Technical Stack Summary

- **Web Scraping**: BeautifulSoup4, Requests, Regular Expressions
- **Data Processing**: Pandas, NumPy
- **Configuration**: PyYAML
- **Scheduling**: APScheduler, Schedule
- **Visualization**: Plotly, Plotly Express
- **Machine Learning**: Scikit-learn (optional)
- **Web Framework**: Streamlit
- **Data Formats**: JSON, CSV, Excel (via openpyxl/pandas)
- **Logging**: Python Logging Module
- **Type Safety**: Python Typing Module
- **File Operations**: Pathlib, OS, Shutil

---

*This system was designed and developed to address the complex and evolving landscape of state-level prescription drug pricing transparency regulations, providing pharmaceutical companies with the tools needed to maintain compliance and make informed strategic decisions.*

