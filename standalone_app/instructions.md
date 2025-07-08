# Version: 1.0.0
# Description: This document outlines the architecture and structure of the AI Apps platform, including the tech stack, app structure, and UI layout.

# instructions:
- create a standalone fullstack AI application that integrates web automation and data profiling capabilities.
- beauty is a key aspect of the application, with a focus on creating an interactive and visually appealing user interface. focus on creating beautiful, sleek, modern, fluid, responsive forms and layouts that enhance user experience.
- the application should have a backend API for LLM queries, web automation steps, and data profiling steps.
- the frontend should provide an interactive UI with beautiful forms for each step, allowing users to input data, view execution status, and see results.
- the application should be built using modern technologies and frameworks, ensuring a responsive and user-friendly experience.
- all code should be written in Python 3.12 for the backend and React 19.1 with Tailwind CSS 4.1 for the frontend, and should follow best practices for code organization and maintainability.
- use /var/www/ai_apps/standalone_app/v1 as the root directory for the application.
- the root should serve the react app on port 8004.
- entire app should be triggered by a script named `start_app.sh` that sets up the environment and starts the application.
- entire app should be teared down by a script named `stop_app.sh` that cleans up the environment, release the port and stops the application.
- app state should be stored in a MongoDB 6.0 database, allowing for persistent data storage and retrieval. Adapt /var/www/ai_apps/apps/common/database/mongodb_client.py to connect to the MongoDB instance and create v1 database.
- the application should be structured in a modular way, with separate directories for API endpoints, web automation steps, data profiling steps, and UI components.
- the application should include a left panel for app navigation (web automation and data profiling) and a right panel for app details, including interactive forms, input status, execution results, and more.
- ensure that the application is responsive and works well on both desktop and mobile devices, providing a seamless user experience across different screen sizes.
- the application should be designed to handle errors gracefully, providing clear feedback to users in case of issues during execution.
- the application should be well-documented, with clear instructions for setup, usage, and troubleshooting.
- the application should be tested thoroughly to ensure all features work as expected and provide a smooth user experience.
- the directory structure should be organized to facilitate easy navigation and maintenance, with clear naming conventions for files and directories. No unwanted files should be included in the final application. You need to constantly remove any working files that are not needed in the final application.
- each functionality should be build step by step, ensuring that each part is functional before moving on to the next. This will help in maintaining a clean and organized codebase.



# Tech Stack:
- Python 3.12
- Node.js 22.16
- React 19.1
- Tailwind CSS 4.1
- mongoDB 6.0


# brand colors
Hex code	#004685
Hex code	#EE1C25

# root directory
/var/www/ai_apps/standalone_app/v1

# default settings
- port: 8004

# app structure:
api/llm_query:
    input: str
    output: str

# web_automation:
step 1:
api/extract_elements:
    input: str
    output: list[object]

step 2:
api/generate_gherkin_tests:
    input: str
    output: list[object]

step 3:
api/generate_python_code:
    input: str
    output: str

step 4:
api/execute_python_code:
    input: str
    output: str

# data profiling:
step 1:
api/generate_profiling_suggestions:
    inputs: 1. database_name:str,
             2. table_name:str,
             3. columns:list[str]
    output: list[dict]

step 2:
api/generate_profiling_testcases:
    input: output from step 1
    output: list[dict]

step 3:
api/generate_pyspark_code:
    input: output from step 2
    output: str

step 4:
api/execute_pyspark_code:
    input: output from step 3
    output: 

step 5:
api/generate_dq_suggestions:
    input: output from step 4
    output: list[dict]

step 6:
api/generate_dq_tests:
    input: output from step 5
    output: list[dict]

step 7:
api/generate_pyspark_dq_code:
    input: output from step 6
    output: str

step 8:
api/execute_pyspark_dq_code:
    input: output from step 7
    output: str


# ui layout:
left panel:
    - apps
        - web_automation
        - data_profiling
right panel:
    - app details
        - interactive very beautiful forms for each step
        - inputs
            - status
            - not started
            - in progress
            - completed
            - error
        - view result of execution
        - etc.