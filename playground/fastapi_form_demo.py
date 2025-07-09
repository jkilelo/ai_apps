#!/usr/bin/env python3
"""
FastAPI Demo: Dynamic Form Generation from Pydantic Models

This demonstrates how to use html.py to automatically generate forms
from your FastAPI request/response models.
"""

from fastapi import FastAPI, APIRouter, Response
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from enum import Enum
from datetime import date

# Import our form generator
from html import PydanticFormConverter, generate_form_endpoint

app = FastAPI(title="Dynamic Form Generator Demo")
router = APIRouter()


# Example 1: Simple Account Model
class AccountType(str, Enum):
    PERSONAL = "personal"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class AccountRequest(BaseModel):
    """Account registration request"""
    username: str = Field(..., min_length=3, max_length=20, description="Choose a unique username")
    email: EmailStr = Field(..., description="Your email address")
    password: str = Field(..., min_length=8, description="Must be at least 8 characters")
    account_type: AccountType = Field(..., description="Select your account type")
    company_name: Optional[str] = Field(None, description="Required for business accounts")
    newsletter: bool = Field(True, description="Receive updates and news")


# Automatically generate form endpoints
generate_form_endpoint(router, AccountRequest, "/account")


# Example 2: Multi-step Registration
class PersonalInfo(BaseModel):
    first_name: str = Field(..., min_length=2, description="Your first name")
    last_name: str = Field(..., min_length=2, description="Your last name")
    date_of_birth: date = Field(..., description="Must be 18 or older")
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$', description="Optional phone number")


class AddressInfo(BaseModel):
    street: str = Field(..., description="Street address")
    city: str = Field(...)
    state: str = Field(..., max_length=2, description="2-letter state code")
    zip_code: str = Field(..., pattern=r'^\d{5}(-\d{4})?$')
    country: str = Field(default="USA")


class Preferences(BaseModel):
    interests: List[str] = Field(default_factory=list, description="Select your interests")
    communication_preference: str = Field("email", description="How should we contact you?")
    language: str = Field("en", description="Preferred language")


@router.get("/register", response_class=Response)
async def get_registration_form():
    """Multi-step registration form"""
    wizard = PydanticFormConverter.create_wizard_from_models(
        [PersonalInfo, AddressInfo, Preferences],
        title="Complete Registration",
        submit_url="/api/register",
        step_titles=["Personal Information", "Address", "Preferences"],
        step_descriptions=[
            "Tell us about yourself",
            "Where are you located?",
            "Customize your experience"
        ]
    )
    return Response(content=wizard.generate_html(), media_type="text/html")


@router.post("/api/register")
async def submit_registration(
    personal: PersonalInfo,
    address: AddressInfo,
    preferences: Preferences
):
    """Handle multi-step form submission"""
    return {
        "status": "success",
        "message": "Registration complete!",
        "data": {
            "personal": personal.model_dump(),
            "address": address.model_dump(),
            "preferences": preferences.model_dump()
        }
    }


# Example 3: Dynamic Product Configuration
class ProductCategory(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    BOOKS = "books"


class ProductBase(BaseModel):
    category: ProductCategory = Field(..., description="Product category")
    name: str = Field(..., description="Product name")
    quantity: int = Field(1, ge=1, le=100)


@router.get("/product-config", response_class=Response)
async def get_product_form():
    """Single model form with custom styling"""
    fields = PydanticFormConverter.model_to_form_fields(
        ProductBase,
        custom_labels={
            "category": "Product Category",
            "name": "Product Name",
            "quantity": "How many?"
        }
    )
    
    # Create a single-step wizard
    from html import FormStep, FormWizard
    wizard = FormWizard(
        title="Configure Your Product",
        steps=[
            FormStep(
                title="Product Details",
                description="Select and configure your product",
                fields=fields
            )
        ],
        submit_url="/api/product-config"
    )
    
    return Response(content=wizard.generate_html(), media_type="text/html")


@router.post("/api/product-config")
async def submit_product(product: ProductBase):
    """Handle product configuration"""
    # Calculate price based on category
    prices = {
        "electronics": 99.99,
        "clothing": 49.99,
        "books": 19.99
    }
    
    total = prices.get(product.category, 0) * product.quantity
    
    return {
        "status": "success",
        "product": product.model_dump(),
        "total_price": total
    }


# Include router in app
app.include_router(router)


# Homepage with links to all forms
@app.get("/", response_class=Response)
async def homepage():
    """Homepage with links to all available forms"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI Form Generator Demo</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }
            h1 { color: #333; }
            .form-links {
                list-style: none;
                padding: 0;
            }
            .form-links li {
                margin: 20px 0;
                padding: 20px;
                background: #f5f5f5;
                border-radius: 8px;
            }
            .form-links a {
                font-size: 18px;
                color: #007bff;
                text-decoration: none;
            }
            .form-links a:hover {
                text-decoration: underline;
            }
            .description {
                color: #666;
                margin-top: 5px;
            }
            code {
                background: #eee;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <h1>🚀 FastAPI Dynamic Form Generator</h1>
        <p>This demo shows how to automatically generate HTML forms from Pydantic models!</p>
        
        <h2>Available Forms:</h2>
        <ul class="form-links">
            <li>
                <a href="/account">Account Registration Form</a>
                <div class="description">
                    Single-step form generated from <code>AccountRequest</code> model
                </div>
            </li>
            <li>
                <a href="/register">Multi-Step Registration</a>
                <div class="description">
                    3-step wizard from multiple models: <code>PersonalInfo</code>, <code>AddressInfo</code>, <code>Preferences</code>
                </div>
            </li>
            <li>
                <a href="/product-config">Product Configuration</a>
                <div class="description">
                    Dynamic product form with calculated pricing
                </div>
            </li>
        </ul>
        
        <h2>How it works:</h2>
        <ol>
            <li>Define your Pydantic models with validation rules</li>
            <li>Use <code>PydanticFormConverter</code> to generate form fields</li>
            <li>Forms automatically include:
                <ul>
                    <li>✅ HTML5 validation from Pydantic constraints</li>
                    <li>✅ Proper field types (email, number, date, etc.)</li>
                    <li>✅ Help text from field descriptions</li>
                    <li>✅ Enum fields become select dropdowns</li>
                    <li>✅ Progress tracking for multi-step forms</li>
                    <li>✅ Local storage for saving progress</li>
                </ul>
            </li>
        </ol>
        
        <p><strong>Try the forms above to see it in action!</strong></p>
    </body>
    </html>
    """
    return Response(content=html, media_type="text/html")


if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI Form Generator Demo...")
    print("Visit http://localhost:8035 to see the forms")
    uvicorn.run(app, host="0.0.0.0", port=8035)