# HTML Form Chain Engine v3.0

## Revolutionary Form Processing Paradigm

Form Chain Engine v3 introduces a groundbreaking approach to web forms: **Forms as Input-Output Processors**. Unlike traditional form wizards that simply collect data step-by-step, v3 treats each form as a processor in a chain, where the output of one step becomes the input for the next.

## Key Innovation

Each step in a form chain consists of:
1. **Request Model** (Pydantic) - Defines the input schema
2. **Processing Logic** - Business logic that transforms input
3. **Response Model** (Pydantic) - Defines the output schema
4. **Next Step** - Uses the response to generate the next form

```
Form 1 → Process → Response → Form 2 (pre-filled) → Process → Response → Form 3
```

## Quick Start

```python
from html_v3 import FormChainEngine, FormStep, FormStepProcessor
from pydantic import BaseModel, Field

# Define your models
class Step1Request(BaseModel):
    database_name: str = Field(..., description="Database to analyze")
    table_name: str = Field(..., description="Table to check")

class Step1Response(BaseModel):
    columns: List[str]
    row_count: int
    
# Create processor
class DatabaseProcessor(FormStepProcessor):
    async def process(self, input_data: Step1Request, context: Dict) -> Step1Response:
        # Your business logic here
        return Step1Response(columns=["id", "name"], row_count=1000)

# Build the chain
chain = FormChainEngine(
    chain_id="data_quality",
    title="Data Quality Check",
    description="Analyze and improve your data",
    steps=[
        FormStep(
            id="step_1",
            title="Select Data Source",
            request_model=Step1Request,
            response_model=Step1Response,
            processor=DatabaseProcessor(),
            is_entry_point=True,
            next_step_id="step_2"
        ),
        # More steps...
    ]
)
```

## Core Features

### 1. Dynamic Field Injection
Response data from one step can dynamically add fields to the next form:

```python
def inject_column_fields(response: Step1Response) -> List[FormFieldSpec]:
    return [
        FormFieldSpec(
            name=f"check_{col}",
            field_type=FieldType.CHECKBOX,
            label=f"Check {col} column"
        )
        for col in response.columns
    ]
```

### 2. Conditional Routing
Route to different forms based on processing results:

```python
def route_by_score(response: QualityResponse) -> str:
    if response.quality_score > 90:
        return "success_step"
    elif response.quality_score > 50:
        return "improvement_step"
    else:
        return "critical_step"
```

### 3. State Persistence
The engine maintains state across the entire chain:
- Previous responses are available in context
- Forms can reference data from any previous step
- State can be persisted to storage

### 4. Type Safety
Full type safety with Pydantic models:
- Automatic validation
- Clear request/response contracts
- IDE autocomplete support

## Real-World Examples

### 1. Data Quality Check Process
```bash
# User selects database/table
→ System analyzes and returns metadata
→ Form shows columns as checkboxes
→ User selects checks to perform
→ System runs checks and returns issues
→ Form shows actions based on issues
```

### 2. Dynamic Job Application
```bash
# Basic info + department selection
→ System screens and routes by department
→ Engineering: Technical assessment
→ Sales: Sales methodology questions  
→ System evaluates and schedules interview
```

### 3. Insurance Claim with Documents
```bash
# Claim type selection
→ System determines required documents
→ Auto: Vehicle photos, police report
→ Home: Property photos, estimates
→ Dynamic document upload fields
```

### 4. AI-Powered Support
```bash
# Issue description
→ AI analyzes and suggests solutions
→ If not resolved: Technical diagnostics
→ System attempts automated fixes
→ Escalation if needed
```

## Running the Demo

1. Start the demo server:
```bash
python html_v3_demo_server.py
```

2. Visit http://localhost:8037

3. Try the live examples:
   - Data Quality Check
   - Job Application
   - Insurance Claim
   - Support Ticket

## API Pattern

Each form chain follows a consistent API:

```
GET  /chain/{chain_id}/start         # Get entry form
POST /api/chain/{id}/process/{step}  # Process step
GET  /api/chain/{id}/status          # Get status
```

Response format:
```json
{
  "next_form_html": "...",  // Next form HTML
  "completed": false,       // Chain complete?
  "chain_state": {...}      // Current state
}
```

## Advanced Usage

### Custom Processors
```python
class MLProcessor(FormStepProcessor):
    async def process(self, input_data, context):
        # Call ML model
        predictions = await self.ml_model.predict(input_data)
        
        # Return response with predictions
        return PredictionResponse(
            predictions=predictions,
            confidence=0.95
        )
```

### Complex Routing
```python
def multi_path_routing(response):
    if response.user_type == "enterprise":
        if response.budget > 100000:
            return "enterprise_premium"
        else:
            return "enterprise_standard"
    else:
        return "consumer_flow"
```

### Integration with Services
```python
class APIProcessor(FormStepProcessor):
    async def process(self, input_data, context):
        # Call external API
        async with httpx.AsyncClient() as client:
            result = await client.post(
                "https://api.service.com/analyze",
                json=input_data.dict()
            )
        
        return ServiceResponse(**result.json())
```

## Benefits

1. **Modularity**: Each step is independent and testable
2. **Reusability**: Steps can be shared across chains
3. **Type Safety**: Full type checking with Pydantic
4. **Flexibility**: Dynamic routing and field injection
5. **State Management**: Automatic state handling
6. **Business Logic**: Clear separation of concerns

## Migration from v2

v3 is a complete paradigm shift:
- v2: Static multi-step forms
- v3: Dynamic form chains with processing

To migrate:
1. Define Pydantic models for each step
2. Create processors for business logic
3. Build the chain with FormChainEngine
4. Update endpoints to handle processing

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Browser   │────▶│ Form Engine  │────▶│ Processors  │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │                     │
       │                    ▼                     ▼
       │            ┌──────────────┐     ┌─────────────┐
       └───────────▶│    State     │     │   Services  │
                    └──────────────┘     └─────────────┘
```

## Best Practices

1. **Keep processors focused**: One responsibility per processor
2. **Use type hints**: Leverage Pydantic for validation
3. **Handle errors gracefully**: Return user-friendly messages
4. **Test processors independently**: Unit test business logic
5. **Document models**: Use Field descriptions

## Conclusion

Form Chain Engine v3 transforms forms from simple data collectors into powerful processing pipelines. By treating forms as input-output processors, you can build sophisticated workflows that adapt dynamically to user input and processing results.

Visit the demo at http://localhost:8037 to see it in action!