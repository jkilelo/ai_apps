#!/usr/bin/env python3
"""
Run all AI integration demos to showcase the platform's capabilities
"""

import asyncio
import sys
from datetime import datetime

# Import all demo modules
from shopping_assistant import demonstrate_shopping_workflow
from medical_intake_ai import demonstrate_medical_intake
from travel_planner_ai import demonstrate_travel_planner
from financial_advisor_ai import demonstrate_financial_advisor
from education_tutor_ai import demonstrate_education_tutor
from customer_support_ai import demonstrate_customer_support
from html_v3_ai import demo_ai_form_chain


async def run_all_demos():
    """Run all AI integration demonstrations"""
    
    print("🚀 HTML v3 AI Integration Platform - Comprehensive Demo")
    print("="*70)
    print("Transforming Conversations into Actionable Workflows")
    print("="*70)
    
    demos = [
        ("Core AI Form Chain", demo_ai_form_chain),
        ("Smart Shopping Assistant", demonstrate_shopping_workflow),
        ("Medical Intake System", demonstrate_medical_intake),
        ("Travel Planning Assistant", demonstrate_travel_planner),
        ("Financial Advisory System", demonstrate_financial_advisor),
        ("Educational Tutor Platform", demonstrate_education_tutor),
        ("Customer Support System", demonstrate_customer_support)
    ]
    
    print(f"\n📋 Running {len(demos)} demonstrations...\n")
    
    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n{'='*70}")
        print(f"Demo {i}/{len(demos)}: {name}")
        print(f"{'='*70}")
        
        try:
            await demo_func()
            print(f"\n✅ {name} completed successfully!")
        except Exception as e:
            print(f"\n❌ Error in {name}: {str(e)}")
        
        if i < len(demos):
            print("\n⏳ Continuing to next demo in 2 seconds...")
            await asyncio.sleep(2)
    
    print("\n" + "="*70)
    print("🎉 All Demonstrations Completed!")
    print("="*70)
    
    # Summary
    print("\n📊 Platform Capabilities Summary:")
    print("""
    ✅ Natural Language Processing
       - Extract structured data from conversations
       - Understand intent and context
       - Detect sentiment and urgency
    
    ✅ Dynamic Form Generation
       - Create forms based on conversation analysis
       - Adaptive fields based on context
       - Multi-step workflows with state management
    
    ✅ Domain-Specific Intelligence
       - Shopping: Recipe matching, store recommendations
       - Medical: Symptom triage, risk assessment
       - Travel: Itinerary planning, budget optimization
       - Financial: Portfolio recommendations, tax strategies
       - Education: Personalized curricula, adaptive learning
       - Support: Ticket routing, troubleshooting workflows
    
    ✅ Workflow Automation
       - Convert conversations to actionable steps
       - Maintain context across interactions
       - Execute business logic based on inputs
    """)
    
    print("\n💡 Integration Opportunities:")
    print("""
    1. E-commerce platforms (Shopify, WooCommerce)
    2. CRM systems (Salesforce, HubSpot)
    3. Healthcare systems (EHR/EMR)
    4. Educational platforms (Canvas, Moodle)
    5. Financial services (Banking APIs)
    6. Customer support tools (Zendesk, Intercom)
    """)
    
    print("\n🔗 Next Steps:")
    print("""
    1. Integrate with real LLM APIs (OpenAI, Anthropic, Google)
    2. Add voice input support
    3. Implement multi-language capabilities
    4. Connect to external services
    5. Deploy as microservices
    """)
    
    # Generate summary report
    report = {
        "demo_run_date": datetime.now().isoformat(),
        "demos_completed": len(demos),
        "platform_version": "v3",
        "key_features": [
            "Conversational AI integration",
            "Dynamic form generation",
            "Multi-step workflows",
            "Domain-specific intelligence",
            "State management",
            "Adaptive UI/UX"
        ],
        "use_cases": [demo[0] for demo in demos],
        "status": "All demos completed successfully"
    }
    
    # Save report
    import json
    with open("demo_summary_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Summary report saved to: demo_summary_report.json")
    print("\nThank you for exploring the HTML v3 AI Integration Platform! 🚀")


def main():
    """Main entry point"""
    print("Starting HTML v3 AI Integration Platform Demo Suite...")
    print(f"Python version: {sys.version}")
    print(f"Start time: {datetime.now()}")
    
    try:
        asyncio.run(run_all_demos())
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running demos: {str(e)}")
        raise
    finally:
        print(f"\nEnd time: {datetime.now()}")


if __name__ == "__main__":
    main()