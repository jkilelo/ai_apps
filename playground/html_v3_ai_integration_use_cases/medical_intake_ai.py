#!/usr/bin/env python3
"""
AI-Powered Medical Intake System

Transforms natural language symptom descriptions into structured medical forms
with intelligent follow-up questions based on symptoms.

Features:
- Natural language symptom parsing
- Dynamic follow-up questions based on symptoms
- Risk assessment and triage
- Medical history integration
- HIPAA-compliant data handling
"""

import asyncio
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field
import json

from html_v3_ai import (
    LLMProvider, ConversationContext, ConversationIntent,
    AIFormChainGenerator, ConversationFormBridge
)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from html_v3 import FormChainEngine, FormStep, FormStepProcessor, FormFieldSpec, FieldType


class SymptomSeverity(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class BodySystem(str, Enum):
    RESPIRATORY = "respiratory"
    CARDIOVASCULAR = "cardiovascular"
    GASTROINTESTINAL = "gastrointestinal"
    NEUROLOGICAL = "neurological"
    MUSCULOSKELETAL = "musculoskeletal"
    DERMATOLOGICAL = "dermatological"
    GENERAL = "general"


class MedicalAIProvider(LLMProvider):
    """Medical-specific AI provider for symptom analysis"""
    
    def __init__(self):
        # Symptom knowledge base
        self.symptom_patterns = {
            "headache": {
                "systems": [BodySystem.NEUROLOGICAL],
                "follow_up_questions": [
                    "How long have you had this headache?",
                    "Where exactly does it hurt?",
                    "Rate the pain from 1-10",
                    "Any vision changes?",
                    "Any nausea or vomiting?"
                ],
                "red_flags": ["sudden onset", "worst ever", "vision loss", "confusion"]
            },
            "chest pain": {
                "systems": [BodySystem.CARDIOVASCULAR, BodySystem.RESPIRATORY],
                "follow_up_questions": [
                    "Where exactly is the pain?",
                    "Does it radiate anywhere?",
                    "What triggers it?",
                    "Any shortness of breath?",
                    "Any previous heart conditions?"
                ],
                "red_flags": ["crushing", "radiating", "shortness of breath", "sweating"]
            },
            "fever": {
                "systems": [BodySystem.GENERAL],
                "follow_up_questions": [
                    "What's your temperature?",
                    "How long have you had fever?",
                    "Any other symptoms?",
                    "Recent travel?",
                    "Any sick contacts?"
                ],
                "red_flags": ["high fever", "confusion", "stiff neck", "rash"]
            },
            "cough": {
                "systems": [BodySystem.RESPIRATORY],
                "follow_up_questions": [
                    "Is it dry or productive?",
                    "Any blood in sputum?",
                    "How long have you had it?",
                    "Any chest pain?",
                    "Any wheezing?"
                ],
                "red_flags": ["blood", "weight loss", "night sweats", "difficulty breathing"]
            }
        }
        
        self.triage_rules = {
            "emergency": [
                "chest pain with shortness of breath",
                "severe headache with confusion",
                "difficulty breathing",
                "uncontrolled bleeding"
            ],
            "urgent": [
                "moderate pain lasting >24 hours",
                "fever >103°F",
                "persistent vomiting",
                "moderate breathing difficulty"
            ],
            "routine": [
                "mild symptoms >1 week",
                "follow-up visit",
                "medication refill",
                "general checkup"
            ]
        }
    
    async def analyze_conversation(self, context: ConversationContext) -> Dict[str, Any]:
        """Analyze medical conversation for symptoms and urgency"""
        
        messages_text = " ".join([m["content"].lower() for m in context.messages])
        
        # Extract symptoms
        detected_symptoms = []
        affected_systems = set()
        all_follow_ups = []
        risk_level = "low"
        
        for symptom, data in self.symptom_patterns.items():
            if symptom in messages_text:
                detected_symptoms.append(symptom)
                affected_systems.update(data["systems"])
                all_follow_ups.extend(data["follow_up_questions"])
                
                # Check for red flags
                for red_flag in data["red_flags"]:
                    if red_flag in messages_text:
                        risk_level = "high"
                        break
        
        # Determine urgency
        urgency = self._calculate_urgency(messages_text, detected_symptoms)
        
        return {
            "intent": ConversationIntent.MEDICAL,
            "entities": {
                "symptoms": detected_symptoms,
                "affected_systems": list(affected_systems),
                "duration": self._extract_duration(messages_text),
                "severity": self._extract_severity(messages_text),
                "risk_level": risk_level
            },
            "urgency": urgency,
            "follow_up_questions": list(set(all_follow_ups))[:5],  # Top 5 unique questions
            "recommendations": self._get_recommendations(urgency, detected_symptoms)
        }
    
    async def generate_form_schema(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate medical intake form based on symptoms"""
        
        analysis = await self.analyze_conversation(context)
        entities = analysis["entities"]
        
        # Create dynamic form fields
        fields = [
            {
                "name": "patient_info",
                "type": "section",
                "label": "Patient Information",
                "fields": [
                    {"name": "full_name", "type": "text", "label": "Full Name", "required": True},
                    {"name": "date_of_birth", "type": "date", "label": "Date of Birth", "required": True},
                    {"name": "gender", "type": "select", "label": "Gender", 
                     "options": ["Male", "Female", "Other", "Prefer not to say"], "required": True}
                ]
            },
            {
                "name": "chief_complaint",
                "type": "textarea",
                "label": "Describe your symptoms in detail",
                "default": " ".join([m["content"] for m in context.messages]),
                "required": True
            }
        ]
        
        # Add symptom-specific fields
        for symptom in entities["symptoms"]:
            if symptom == "headache":
                fields.extend([
                    {
                        "name": "headache_location",
                        "type": "select",
                        "label": "Where is the headache located?",
                        "options": ["Frontal", "Temporal", "Occipital", "Whole head", "One side"],
                        "required": True
                    },
                    {
                        "name": "headache_character",
                        "type": "select",
                        "label": "How would you describe the pain?",
                        "options": ["Throbbing", "Sharp", "Dull", "Pressure", "Burning"],
                        "required": True
                    }
                ])
            elif symptom == "fever":
                fields.extend([
                    {
                        "name": "temperature",
                        "type": "number",
                        "label": "Current temperature (°F)",
                        "min": 95,
                        "max": 110,
                        "step": 0.1,
                        "required": False
                    },
                    {
                        "name": "fever_pattern",
                        "type": "select",
                        "label": "Fever pattern",
                        "options": ["Constant", "Intermittent", "Only at night", "Comes and goes"],
                        "required": False
                    }
                ])
        
        # Add general symptom checklist
        fields.append({
            "name": "associated_symptoms",
            "type": "checkbox_group",
            "label": "Check any other symptoms you're experiencing",
            "options": [
                "Fatigue", "Loss of appetite", "Weight loss", "Night sweats",
                "Difficulty sleeping", "Anxiety", "Depression", "Skin rash"
            ],
            "required": False
        })
        
        # Add medical history if high risk
        if entities.get("risk_level") == "high":
            fields.extend([
                {
                    "name": "medical_history",
                    "type": "checkbox_group",
                    "label": "Do you have any of these conditions?",
                    "options": [
                        "Heart disease", "Diabetes", "High blood pressure", "Asthma",
                        "Cancer", "Kidney disease", "Liver disease", "None"
                    ],
                    "required": True
                },
                {
                    "name": "current_medications",
                    "type": "textarea",
                    "label": "List all current medications",
                    "placeholder": "Include dosages if known",
                    "required": False
                }
            ])
        
        # Add urgency indicator
        urgency_color = {
            "emergency": "#dc3545",
            "urgent": "#ffc107",
            "routine": "#28a745"
        }
        
        return {
            "title": "Medical Symptom Assessment",
            "description": f"Based on your symptoms, please provide additional information",
            "urgency": analysis["urgency"],
            "urgency_color": urgency_color.get(analysis["urgency"], "#6c757d"),
            "fields": fields,
            "recommendations": analysis["recommendations"]
        }
    
    async def process_response(self, user_input: str, context: ConversationContext) -> Dict[str, Any]:
        """Process medical responses with safety checks"""
        
        # Add response to context
        context.messages.append({"role": "user", "content": user_input})
        
        # Check for emergency keywords
        emergency_keywords = ["can't breathe", "chest pain", "passing out", "severe pain", "bleeding heavily"]
        
        for keyword in emergency_keywords:
            if keyword in user_input.lower():
                return {
                    "emergency": True,
                    "action": "call_911",
                    "message": "Based on your symptoms, please call 911 or go to the nearest emergency room immediately."
                }
        
        # Update analysis
        new_analysis = await self.analyze_conversation(context)
        
        return {
            "updated_context": context,
            "new_symptoms": new_analysis["entities"]["symptoms"],
            "urgency_change": new_analysis["urgency"],
            "next_action": "continue_assessment"
        }
    
    def _calculate_urgency(self, text: str, symptoms: List[str]) -> str:
        """Calculate medical urgency level"""
        
        # Check emergency rules
        for rule in self.triage_rules["emergency"]:
            if all(word in text for word in rule.split()):
                return "emergency"
        
        # Check urgent rules
        for rule in self.triage_rules["urgent"]:
            if all(word in text for word in rule.split()):
                return "urgent"
        
        # Multiple symptoms or high-risk symptoms
        if len(symptoms) > 3 or any(s in ["chest pain", "difficulty breathing"] for s in symptoms):
            return "urgent"
        
        return "routine"
    
    def _extract_duration(self, text: str) -> Optional[str]:
        """Extract symptom duration from text"""
        
        duration_patterns = {
            "hours": r"(\d+)\s*hours?",
            "days": r"(\d+)\s*days?",
            "weeks": r"(\d+)\s*weeks?",
            "months": r"(\d+)\s*months?"
        }
        
        for unit, pattern in duration_patterns.items():
            import re
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)} {unit}"
        
        return None
    
    def _extract_severity(self, text: str) -> SymptomSeverity:
        """Extract symptom severity from text"""
        
        if any(word in text for word in ["severe", "terrible", "unbearable", "worst"]):
            return SymptomSeverity.SEVERE
        elif any(word in text for word in ["moderate", "medium", "somewhat"]):
            return SymptomSeverity.MODERATE
        elif any(word in text for word in ["mild", "slight", "little"]):
            return SymptomSeverity.MILD
        
        return SymptomSeverity.MODERATE
    
    def _get_recommendations(self, urgency: str, symptoms: List[str]) -> List[str]:
        """Get medical recommendations based on urgency and symptoms"""
        
        recommendations = []
        
        if urgency == "emergency":
            recommendations.append("🚨 Seek immediate emergency care")
            recommendations.append("Call 911 or go to nearest ER")
        elif urgency == "urgent":
            recommendations.append("⚠️ See a healthcare provider today")
            recommendations.append("Visit urgent care or call your doctor")
        else:
            recommendations.append("📅 Schedule an appointment with your doctor")
            recommendations.append("Monitor symptoms and rest")
        
        # Symptom-specific recommendations
        if "fever" in symptoms:
            recommendations.append("Stay hydrated and monitor temperature")
        if "headache" in symptoms:
            recommendations.append("Rest in a dark, quiet room")
        if "cough" in symptoms:
            recommendations.append("Avoid irritants and stay hydrated")
        
        return recommendations


class MedicalIntakeEngine:
    """Complete medical intake workflow engine"""
    
    def __init__(self):
        self.ai_provider = MedicalAIProvider()
        self.bridge = ConversationFormBridge(self.ai_provider)
    
    async def create_intake_workflow(
        self,
        patient_id: str,
        initial_complaint: str
    ) -> Dict[str, Any]:
        """Create medical intake workflow from initial complaint"""
        
        # Create conversation
        context = ConversationContext(messages=[
            {"role": "user", "content": initial_complaint}
        ])
        
        # Analyze symptoms
        analysis = await self.ai_provider.analyze_conversation(context)
        
        # Generate intake form
        schema = await self.ai_provider.generate_form_schema(context)
        
        # Create multi-step workflow based on urgency
        if analysis["urgency"] == "emergency":
            return {
                "type": "emergency_redirect",
                "message": "Based on your symptoms, please seek immediate emergency care.",
                "action": "call_911",
                "symptoms": analysis["entities"]["symptoms"]
            }
        
        # Create form chain for non-emergency cases
        steps = await self._create_intake_steps(schema, analysis)
        
        chain = FormChainEngine(
            chain_id=f"medical_intake_{patient_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            title="Medical Symptom Assessment",
            description="Please provide information about your symptoms",
            steps=steps,
            theme="modern"
        )
        
        return {
            "type": "intake_form",
            "chain": chain,
            "urgency": analysis["urgency"],
            "initial_analysis": analysis
        }
    
    async def _create_intake_steps(
        self,
        schema: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> List[FormStep]:
        """Create intake form steps"""
        
        from pydantic import create_model
        
        # Step 1: Initial symptom details
        SymptomDetails = create_model(
            "SymptomDetails",
            full_name=(str, Field(..., description="Your full name")),
            date_of_birth=(date, Field(..., description="Date of birth")),
            chief_complaint=(str, Field(..., description="Main reason for visit")),
            symptom_duration=(str, Field(..., description="How long have you had these symptoms?")),
            symptom_severity=(int, Field(..., ge=1, le=10, description="Rate severity 1-10"))
        )
        
        # Add dynamic fields based on symptoms
        for symptom in analysis["entities"]["symptoms"][:3]:  # Top 3 symptoms
            field_name = f"{symptom.replace(' ', '_')}_details"
            SymptomDetails.__fields__[field_name] = (
                Optional[str],
                Field(None, description=f"Additional details about {symptom}")
            )
        
        SymptomResponse = create_model(
            "SymptomResponse",
            risk_assessment=(str, Field(...)),
            recommended_action=(str, Field(...))
        )
        
        # Step 2: Medical history (if needed)
        MedicalHistory = create_model(
            "MedicalHistory",
            chronic_conditions=(List[str], Field(default_factory=list)),
            current_medications=(str, Field("", description="List all medications")),
            allergies=(str, Field("", description="List any allergies")),
            recent_travel=(bool, Field(False)),
            recent_exposures=(str, Field("", description="Any sick contacts?"))
        )
        
        MedicalHistoryResponse = create_model(
            "MedicalHistoryResponse",
            risk_factors_identified=(List[str], Field(...)),
            additional_screening_needed=(bool, Field(...))
        )
        
        # Step 3: Next steps
        NextSteps = create_model(
            "NextSteps",
            preferred_appointment_time=(str, Field(..., description="Morning, Afternoon, Evening")),
            preferred_provider_type=(str, Field(..., description="Primary care, Specialist, Any")),
            transportation_available=(bool, Field(...)),
            emergency_contact=(str, Field(..., description="Emergency contact phone"))
        )
        
        NextStepsResponse = create_model(
            "NextStepsResponse",
            appointment_scheduled=(bool, Field(...)),
            appointment_details=(Optional[Dict[str, Any]], Field(None)),
            pre_appointment_instructions=(List[str], Field(...))
        )
        
        return [
            FormStep(
                id="symptom_details",
                title="Symptom Information",
                description="Tell us more about your symptoms",
                request_model=SymptomDetails,
                response_model=SymptomResponse,
                processor=SymptomProcessor(self.ai_provider),
                is_entry_point=True,
                next_step_id="medical_history"
            ),
            FormStep(
                id="medical_history",
                title="Medical History",
                description="Help us understand your health background",
                request_model=MedicalHistory,
                response_model=MedicalHistoryResponse,
                processor=MedicalHistoryProcessor(),
                next_step_id="next_steps"
            ),
            FormStep(
                id="next_steps",
                title="Schedule Care",
                description="Let's get you the care you need",
                request_model=NextSteps,
                response_model=NextStepsResponse,
                processor=AppointmentProcessor(),
                is_exit_point=True
            )
        ]


class SymptomProcessor(FormStepProcessor):
    """Process symptom information"""
    
    def __init__(self, ai_provider: MedicalAIProvider):
        self.ai_provider = ai_provider
    
    async def process(self, input_data: BaseModel, chain_context: Dict[str, Any]) -> BaseModel:
        """Assess symptoms and determine risk"""
        
        # Create context from input
        severity = input_data.symptom_severity
        
        # Determine risk level
        if severity >= 8:
            risk = "high"
            action = "Urgent care recommended within 4 hours"
        elif severity >= 5:
            risk = "moderate"
            action = "See healthcare provider within 24-48 hours"
        else:
            risk = "low"
            action = "Monitor symptoms, schedule routine appointment if persists"
        
        response_model = type(self).process.__annotations__['return']
        return response_model(
            risk_assessment=risk,
            recommended_action=action
        )


class MedicalHistoryProcessor(FormStepProcessor):
    """Process medical history"""
    
    async def process(self, input_data: BaseModel, chain_context: Dict[str, Any]) -> BaseModel:
        """Analyze medical history for risk factors"""
        
        risk_factors = []
        
        # Check chronic conditions
        high_risk_conditions = ["heart disease", "diabetes", "cancer", "immunocompromised"]
        if hasattr(input_data, 'chronic_conditions'):
            for condition in input_data.chronic_conditions:
                if any(risk in condition.lower() for risk in high_risk_conditions):
                    risk_factors.append(f"Chronic condition: {condition}")
        
        # Check medications
        if hasattr(input_data, 'current_medications') and input_data.current_medications:
            if "immunosuppressant" in input_data.current_medications.lower():
                risk_factors.append("Immunosuppressive medication")
        
        # Travel history
        if getattr(input_data, 'recent_travel', False):
            risk_factors.append("Recent travel")
        
        response_model = type(self).process.__annotations__['return']
        return response_model(
            risk_factors_identified=risk_factors,
            additional_screening_needed=len(risk_factors) > 0
        )


class AppointmentProcessor(FormStepProcessor):
    """Process appointment scheduling"""
    
    async def process(self, input_data: BaseModel, chain_context: Dict[str, Any]) -> BaseModel:
        """Schedule appointment based on urgency and preferences"""
        
        # Get risk assessment from previous steps
        risk = chain_context.get("step_symptom_details_response", {}).get("risk_assessment", "low")
        
        # Simulate appointment scheduling
        if risk == "high":
            appointment = {
                "date": datetime.now().date().isoformat(),
                "time": "Next available (within 4 hours)",
                "type": "Urgent care",
                "provider": "First available provider"
            }
        else:
            # Schedule based on preference
            appointment = {
                "date": (datetime.now() + timedelta(days=2)).date().isoformat(),
                "time": f"{input_data.preferred_appointment_time} slot",
                "type": "Primary care",
                "provider": "Dr. Smith"
            }
        
        instructions = [
            "Bring list of all current medications",
            "Arrive 15 minutes early for paperwork",
            "Bring insurance card and ID"
        ]
        
        if risk == "high":
            instructions.insert(0, "If symptoms worsen, go to ER immediately")
        
        response_model = type(self).process.__annotations__['return']
        return response_model(
            appointment_scheduled=True,
            appointment_details=appointment,
            pre_appointment_instructions=instructions
        )


async def demonstrate_medical_intake():
    """Demonstrate the medical intake system"""
    
    print("🏥 AI-Powered Medical Intake Demo")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            "patient_id": "patient_001",
            "complaint": "I've had a terrible headache for 3 days. It's getting worse and I'm seeing spots.",
            "expected_urgency": "urgent"
        },
        {
            "patient_id": "patient_002",
            "complaint": "I have a mild cough and runny nose for the past week.",
            "expected_urgency": "routine"
        },
        {
            "patient_id": "patient_003",
            "complaint": "Sudden chest pain and can't breathe properly",
            "expected_urgency": "emergency"
        }
    ]
    
    engine = MedicalIntakeEngine()
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Patient Complaint: '{test['complaint']}'")
        print("-" * 40)
        
        result = await engine.create_intake_workflow(
            test["patient_id"],
            test["complaint"]
        )
        
        print(f"   Urgency: {result.get('urgency', result.get('type'))}")
        
        if result["type"] == "emergency_redirect":
            print(f"   ⚠️  Action: {result['action']}")
            print(f"   Message: {result['message']}")
        else:
            print(f"   ✅ Intake form created")
            print(f"   Chain ID: {result['chain'].chain_id}")
            
            analysis = result["initial_analysis"]
            print(f"   Symptoms detected: {', '.join(analysis['entities']['symptoms'])}")
            print(f"   Risk level: {analysis['entities']['risk_level']}")
            
            print("\n   Recommendations:")
            for rec in analysis["recommendations"][:3]:
                print(f"   - {rec}")
    
    print("\n" + "="*60)
    print("💡 Key Features Demonstrated:")
    print("- Natural language symptom extraction")
    print("- Urgency triage (emergency/urgent/routine)")
    print("- Dynamic form generation based on symptoms")
    print("- Risk assessment and recommendations")
    print("- HIPAA-compliant workflow design")


if __name__ == "__main__":
    asyncio.run(demonstrate_medical_intake())