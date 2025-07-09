Tech Stack:
- Python 3.12
- Node.js 22.16
- React 19.1
- Tailwind CSS 4.1

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

