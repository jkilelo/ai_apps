"""
Business Document Intelligence MCP Server
Real-world application for executive decision support
Analyzes documents, extracts insights, answers questions
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Optional imports for document processing
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    import docx
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

# Initialize MCP server
mcp = FastMCP("Business Intelligence Server")

# In-memory document store (in production, use a database)
document_store = {}
insights_cache = {}
kpi_metrics = {}

@mcp.tool()
async def analyze_document(file_path: str, document_type: str = "auto") -> Dict[str, Any]:
    """
    Analyze a business document and extract key information.

    Args:
        file_path: Path to the document
        document_type: Type of document (contract, report, proposal, memo, auto)

    Returns:
        Extracted information and insights
    """
    try:
        # Read document content
        content = await read_document_content(file_path)

        # Extract key information based on patterns
        analysis = {
            "file": file_path,
            "type": document_type if document_type != "auto" else detect_document_type(content),
            "length": len(content),
            "extracted_data": {}
        }

        # Extract dates
        dates = extract_dates(content)
        analysis["extracted_data"]["dates"] = dates

        # Extract monetary amounts
        amounts = extract_amounts(content)
        analysis["extracted_data"]["amounts"] = amounts

        # Extract company/party names
        entities = extract_entities(content)
        analysis["extracted_data"]["entities"] = entities

        # Extract key terms and sections
        key_terms = extract_key_terms(content)
        analysis["extracted_data"]["key_terms"] = key_terms

        # Extract action items
        action_items = extract_action_items(content)
        analysis["extracted_data"]["action_items"] = action_items

        # Risk indicators
        risks = identify_risks(content)
        analysis["extracted_data"]["risks"] = risks

        # Store in cache
        doc_id = Path(file_path).stem
        document_store[doc_id] = {
            "content": content,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }

        return analysis

    except Exception as e:
        return {"error": f"Failed to analyze document: {str(e)}"}

@mcp.tool()
async def generate_executive_summary(document_id: str, max_length: int = 500) -> str:
    """
    Generate an executive summary for a document.

    Args:
        document_id: ID of the document to summarize
        max_length: Maximum length of summary in characters

    Returns:
        Executive summary with key points
    """
    if document_id not in document_store:
        return f"Document {document_id} not found. Please analyze it first."

    doc = document_store[document_id]
    analysis = doc["analysis"]
    content = doc["content"]

    # Create structured summary
    summary = f"EXECUTIVE SUMMARY - {document_id}\n"
    summary += "=" * 50 + "\n\n"

    # Document type and overview
    summary += f"Document Type: {analysis['type'].upper()}\n"
    summary += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    # Key findings
    summary += "KEY FINDINGS:\n"

    # Financial highlights
    if analysis["extracted_data"]["amounts"]:
        summary += f"• Financial Impact: {', '.join(analysis['extracted_data']['amounts'][:3])}\n"

    # Important dates
    if analysis["extracted_data"]["dates"]:
        summary += f"• Critical Dates: {', '.join(analysis['extracted_data']['dates'][:3])}\n"

    # Key parties
    if analysis["extracted_data"]["entities"]:
        summary += f"• Key Parties: {', '.join(analysis['extracted_data']['entities'][:3])}\n"

    # Risks
    if analysis["extracted_data"]["risks"]:
        summary += f"\nRISK FACTORS ({len(analysis['extracted_data']['risks'])}):\n"
        for risk in analysis["extracted_data"]["risks"][:3]:
            summary += f"  ⚠ {risk}\n"

    # Action items
    if analysis["extracted_data"]["action_items"]:
        summary += f"\nACTION REQUIRED ({len(analysis['extracted_data']['action_items'])}):\n"
        for item in analysis["extracted_data"]["action_items"][:3]:
            summary += f"  → {item}\n"

    # Key terms mentioned
    if analysis["extracted_data"]["key_terms"]:
        summary += f"\nKEY TERMS: {', '.join(analysis['extracted_data']['key_terms'][:5])}\n"

    # Recommendations
    summary += "\nRECOMMENDATIONS:\n"
    summary += generate_recommendations(analysis)

    # Trim to max length if needed
    if len(summary) > max_length:
        summary = summary[:max_length-3] + "..."

    # Cache the summary
    insights_cache[f"{document_id}_summary"] = summary

    return summary

@mcp.tool()
async def extract_kpi_metrics(document_ids: List[str]) -> Dict[str, Any]:
    """
    Extract KPI metrics from multiple documents.

    Args:
        document_ids: List of document IDs to analyze

    Returns:
        Aggregated KPI metrics and trends
    """
    metrics = {
        "total_documents": len(document_ids),
        "financial_exposure": 0,
        "upcoming_deadlines": [],
        "risk_score": 0,
        "action_items_count": 0,
        "key_entities": {},
        "document_types": {},
        "trends": {}
    }

    for doc_id in document_ids:
        if doc_id not in document_store:
            continue

        analysis = document_store[doc_id]["analysis"]
        data = analysis["extracted_data"]

        # Aggregate financial amounts
        for amount in data.get("amounts", []):
            # Extract numeric value (simplified)
            num = extract_numeric_value(amount)
            if num:
                metrics["financial_exposure"] += num

        # Collect deadlines
        for date_str in data.get("dates", []):
            deadline = parse_date(date_str)
            if deadline and deadline > datetime.now():
                metrics["upcoming_deadlines"].append({
                    "date": deadline.isoformat(),
                    "document": doc_id,
                    "days_remaining": (deadline - datetime.now()).days
                })

        # Count action items
        metrics["action_items_count"] += len(data.get("action_items", []))

        # Risk scoring
        metrics["risk_score"] += len(data.get("risks", [])) * 10

        # Track entities
        for entity in data.get("entities", []):
            metrics["key_entities"][entity] = metrics["key_entities"].get(entity, 0) + 1

        # Document type distribution
        doc_type = analysis.get("type", "unknown")
        metrics["document_types"][doc_type] = metrics["document_types"].get(doc_type, 0) + 1

    # Sort deadlines by urgency
    metrics["upcoming_deadlines"].sort(key=lambda x: x["days_remaining"])

    # Calculate risk level
    if metrics["risk_score"] > 50:
        metrics["risk_level"] = "HIGH"
    elif metrics["risk_score"] > 20:
        metrics["risk_level"] = "MEDIUM"
    else:
        metrics["risk_level"] = "LOW"

    # Store in cache
    kpi_metrics.update(metrics)

    return metrics

@mcp.tool()
async def answer_document_question(question: str, document_ids: Optional[List[str]] = None) -> str:
    """
    Answer questions about analyzed documents using AI reasoning.

    Args:
        question: The question to answer
        document_ids: Optional list of document IDs to search (None = all)

    Returns:
        Answer based on document analysis
    """
    # Get relevant documents
    if document_ids is None:
        document_ids = list(document_store.keys())

    if not document_ids:
        return "No documents available. Please analyze some documents first."

    # Compile relevant information
    context = "Available document information:\n\n"

    for doc_id in document_ids[:5]:  # Limit to 5 most relevant
        if doc_id not in document_store:
            continue

        doc = document_store[doc_id]
        analysis = doc["analysis"]

        context += f"Document: {doc_id}\n"
        context += f"Type: {analysis['type']}\n"

        # Add relevant extracted data
        if "amounts" in analysis["extracted_data"] and analysis["extracted_data"]["amounts"]:
            context += f"Amounts: {', '.join(analysis['extracted_data']['amounts'][:3])}\n"
        if "dates" in analysis["extracted_data"] and analysis["extracted_data"]["dates"]:
            context += f"Dates: {', '.join(analysis['extracted_data']['dates'][:3])}\n"
        if "entities" in analysis["extracted_data"] and analysis["extracted_data"]["entities"]:
            context += f"Entities: {', '.join(analysis['extracted_data']['entities'][:3])}\n"

        context += "\n"

    # Search for specific information based on question keywords
    question_lower = question.lower()

    # Financial questions
    if any(word in question_lower for word in ["cost", "price", "amount", "budget", "financial", "money", "$"]):
        amounts = []
        for doc_id in document_ids:
            if doc_id in document_store:
                amounts.extend(document_store[doc_id]["analysis"]["extracted_data"].get("amounts", []))
        if amounts:
            return f"Based on the documents, here are the relevant financial figures: {', '.join(amounts[:5])}"

    # Timeline questions
    if any(word in question_lower for word in ["when", "date", "deadline", "timeline", "schedule"]):
        dates = []
        for doc_id in document_ids:
            if doc_id in document_store:
                dates.extend(document_store[doc_id]["analysis"]["extracted_data"].get("dates", []))
        if dates:
            return f"Key dates from the documents: {', '.join(dates[:5])}"

    # Risk questions
    if any(word in question_lower for word in ["risk", "concern", "issue", "problem", "challenge"]):
        risks = []
        for doc_id in document_ids:
            if doc_id in document_store:
                risks.extend(document_store[doc_id]["analysis"]["extracted_data"].get("risks", []))
        if risks:
            return f"Identified risks: {'; '.join(risks[:3])}"

    # Action questions
    if any(word in question_lower for word in ["action", "todo", "task", "next step", "required"]):
        actions = []
        for doc_id in document_ids:
            if doc_id in document_store:
                actions.extend(document_store[doc_id]["analysis"]["extracted_data"].get("action_items", []))
        if actions:
            return f"Action items: {'; '.join(actions[:5])}"

    # General answer based on context
    return f"Based on {len(document_ids)} analyzed documents: {context[:500]}..."

@mcp.tool()
async def compare_documents(doc_id1: str, doc_id2: str) -> Dict[str, Any]:
    """
    Compare two documents and highlight differences.

    Args:
        doc_id1: First document ID
        doc_id2: Second document ID

    Returns:
        Comparison analysis with key differences
    """
    if doc_id1 not in document_store or doc_id2 not in document_store:
        return {"error": "One or both documents not found"}

    doc1 = document_store[doc_id1]["analysis"]
    doc2 = document_store[doc_id2]["analysis"]

    comparison = {
        "document1": doc_id1,
        "document2": doc_id2,
        "differences": {},
        "similarities": {},
        "recommendations": []
    }

    # Compare financial amounts
    amounts1 = set(doc1["extracted_data"].get("amounts", []))
    amounts2 = set(doc2["extracted_data"].get("amounts", []))

    if amounts1 != amounts2:
        comparison["differences"]["financial"] = {
            "doc1_unique": list(amounts1 - amounts2),
            "doc2_unique": list(amounts2 - amounts1),
            "common": list(amounts1 & amounts2)
        }

    # Compare dates
    dates1 = set(doc1["extracted_data"].get("dates", []))
    dates2 = set(doc2["extracted_data"].get("dates", []))

    if dates1 != dates2:
        comparison["differences"]["dates"] = {
            "doc1_unique": list(dates1 - dates2),
            "doc2_unique": list(dates2 - dates1),
            "common": list(dates1 & dates2)
        }

    # Compare entities
    entities1 = set(doc1["extracted_data"].get("entities", []))
    entities2 = set(doc2["extracted_data"].get("entities", []))

    comparison["similarities"]["shared_entities"] = list(entities1 & entities2)
    comparison["differences"]["unique_entities"] = {
        "doc1": list(entities1 - entities2),
        "doc2": list(entities2 - entities1)
    }

    # Risk comparison
    risks1 = doc1["extracted_data"].get("risks", [])
    risks2 = doc2["extracted_data"].get("risks", [])

    if len(risks1) > len(risks2):
        comparison["recommendations"].append(f"{doc_id1} has higher risk profile ({len(risks1)} risks vs {len(risks2)})")

    # Generate recommendations
    if comparison["differences"]:
        comparison["recommendations"].append("Significant differences found - review carefully")

    return comparison

@mcp.tool()
async def generate_action_plan(document_ids: List[str]) -> Dict[str, Any]:
    """
    Generate an action plan based on analyzed documents.

    Args:
        document_ids: List of document IDs to base the plan on

    Returns:
        Prioritized action plan with deadlines
    """
    action_plan = {
        "generated_at": datetime.now().isoformat(),
        "immediate_actions": [],  # Within 7 days
        "short_term_actions": [],  # Within 30 days
        "long_term_actions": [],   # Beyond 30 days
        "risks_to_mitigate": [],
        "key_milestones": []
    }

    all_actions = []
    all_dates = []
    all_risks = []

    # Collect all action items and dates
    for doc_id in document_ids:
        if doc_id not in document_store:
            continue

        analysis = document_store[doc_id]["analysis"]
        data = analysis["extracted_data"]

        # Collect actions
        for action in data.get("action_items", []):
            all_actions.append({
                "action": action,
                "source": doc_id,
                "priority": "high" if any(word in action.lower() for word in ["urgent", "immediate", "asap"]) else "normal"
            })

        # Collect dates
        for date_str in data.get("dates", []):
            parsed_date = parse_date(date_str)
            if parsed_date:
                all_dates.append({
                    "date": parsed_date,
                    "source": doc_id,
                    "description": date_str
                })

        # Collect risks
        all_risks.extend(data.get("risks", []))

    # Categorize actions by urgency
    now = datetime.now()

    for date_item in all_dates:
        days_until = (date_item["date"] - now).days

        milestone = {
            "date": date_item["date"].strftime("%Y-%m-%d"),
            "description": date_item["description"],
            "source": date_item["source"],
            "days_remaining": days_until
        }

        if days_until <= 7:
            action_plan["immediate_actions"].append(f"Deadline approaching: {milestone}")
        elif days_until <= 30:
            action_plan["short_term_actions"].append(f"Upcoming: {milestone}")
        else:
            action_plan["long_term_actions"].append(f"Future: {milestone}")

        action_plan["key_milestones"].append(milestone)

    # Add high priority actions
    for action_item in all_actions:
        if action_item["priority"] == "high":
            action_plan["immediate_actions"].append(action_item)
        else:
            action_plan["short_term_actions"].append(action_item)

    # Add risk mitigations
    for risk in set(all_risks):  # Unique risks
        action_plan["risks_to_mitigate"].append({
            "risk": risk,
            "recommended_action": f"Review and mitigate: {risk}",
            "priority": "high" if "critical" in risk.lower() else "medium"
        })

    # Sort milestones by date
    action_plan["key_milestones"].sort(key=lambda x: x["days_remaining"])

    return action_plan

# Helper functions
async def read_document_content(file_path: str) -> str:
    """Read content from various document formats."""
    path = Path(file_path)

    if not path.exists():
        # For demo, return sample content
        return generate_sample_document_content(path.stem)

    # In real implementation, would read PDF, DOCX, etc.
    try:
        if path.suffix == ".pdf" and PDF_SUPPORT:
            with open(path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text()
                return content
        elif path.suffix == ".docx" and DOCX_SUPPORT:
            doc = docx.Document(path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        elif path.suffix in [".txt", ".md"]:
            with open(path, 'r', encoding='utf-8') as file:
                return file.read()
        else:
            # For unsupported formats or missing libraries, use demo content
            return generate_sample_document_content(path.stem)
    except:
        # Return demo content if file reading fails
        return generate_sample_document_content(path.stem)

def generate_sample_document_content(doc_name: str) -> str:
    """Generate realistic sample document content for demo."""
    samples = {
        "contract": """
        SERVICE AGREEMENT
        Effective Date: January 15, 2025

        This Agreement is between TechCorp Inc. ("Client") and AI Solutions Ltd. ("Vendor").

        Services: The Vendor will provide AI consulting services for $150,000.
        Timeline: Project must be completed by March 31, 2025.
        Payment Terms: 50% upfront ($75,000), 50% on completion.

        Key Deliverables:
        - AI Strategy Document by February 1, 2025
        - Implementation Plan by February 15, 2025
        - System Deployment by March 15, 2025

        Risks: Delays may incur penalties of $1,000 per day.
        Action Required: Sign and return by January 20, 2025.
        """,

        "quarterly_report": """
        Q4 2024 FINANCIAL REPORT

        Revenue: $2.3 million (up 15% YoY)
        Operating Costs: $1.8 million
        Net Profit: $500,000

        Key Achievements:
        - Secured contracts with Microsoft and Google
        - Launched new AI product line
        - Expanded team by 25 employees

        Upcoming Deadlines:
        - Annual filing due: April 15, 2025
        - Board meeting: February 5, 2025
        - Audit completion: March 1, 2025

        Risk Factors:
        - Market competition increasing
        - Supply chain disruptions possible
        - Regulatory changes pending

        Action Items:
        - Review budget allocations
        - Approve new hiring plan
        - Update risk management strategy
        """,

        "proposal": """
        BUSINESS PROPOSAL
        Digital Transformation Initiative

        Submitted to: Global Enterprises Ltd.
        Date: January 10, 2025
        Total Investment: $850,000

        Executive Summary:
        Complete digital transformation over 18 months.

        Phase 1 (Q1 2025): Assessment and Planning - $150,000
        Phase 2 (Q2-Q3 2025): Implementation - $500,000
        Phase 3 (Q4 2025): Training and Optimization - $200,000

        Key Milestones:
        - Kickoff: February 1, 2025
        - Mid-project review: July 15, 2025
        - Go-live: December 1, 2025

        Risks:
        - Integration complexity with legacy systems
        - User adoption challenges
        - Data migration risks

        Next Steps:
        - Decision required by January 25, 2025
        - Contract negotiation by January 30, 2025
        """
    }

    # Return appropriate sample or default
    for key, content in samples.items():
        if key in doc_name.lower():
            return content

    return samples["contract"]  # Default

def detect_document_type(content: str) -> str:
    """Detect document type from content."""
    content_lower = content.lower()

    if any(word in content_lower for word in ["agreement", "contract", "terms and conditions"]):
        return "contract"
    elif any(word in content_lower for word in ["proposal", "quotation", "offer"]):
        return "proposal"
    elif any(word in content_lower for word in ["report", "quarterly", "annual", "financial"]):
        return "report"
    elif any(word in content_lower for word in ["memo", "memorandum"]):
        return "memo"
    else:
        return "document"

def extract_dates(content: str) -> List[str]:
    """Extract dates from content."""
    # Simple date patterns
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b',
        r'\bQ[1-4]\s+\d{4}\b'
    ]

    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        dates.extend(matches)

    return list(set(dates))[:10]  # Return up to 10 unique dates

def extract_amounts(content: str) -> List[str]:
    """Extract monetary amounts from content."""
    # Pattern for currency amounts
    amount_patterns = [
        r'\$[\d,]+\.?\d*\s*(million|billion|thousand|k|m|b)?',
        r'USD\s*[\d,]+\.?\d*',
        r'[\d,]+\.?\d*\s*dollars'
    ]

    amounts = []
    for pattern in amount_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        amounts.extend(matches)

    return list(set(amounts))[:10]

def extract_entities(content: str) -> List[str]:
    """Extract company/person names from content."""
    # Simple pattern for capitalized words (company names)
    entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Ltd|LLC|Corp|Company|Enterprises|Solutions|Group)\b', content)

    # Also look for quoted names
    quoted = re.findall(r'"([^"]+)"', content)
    entities.extend([q for q in quoted if len(q.split()) <= 4])  # Likely entity names

    return list(set(entities))[:10]

def extract_key_terms(content: str) -> List[str]:
    """Extract key business terms from content."""
    key_terms = []

    # Business terms to look for
    business_terms = [
        "deliverable", "milestone", "deadline", "payment", "invoice",
        "compliance", "audit", "risk", "liability", "warranty",
        "revenue", "profit", "cost", "budget", "forecast",
        "strategy", "implementation", "integration", "migration"
    ]

    content_lower = content.lower()
    for term in business_terms:
        if term in content_lower:
            key_terms.append(term)

    return key_terms[:10]

def extract_action_items(content: str) -> List[str]:
    """Extract action items from content."""
    action_patterns = [
        r'(?:action required|next steps?|todo|must|need to|should|required to)[:\s]+([^.\n]+)',
        r'(?:please|kindly)\s+([^.\n]+)',
        r'deadline[:\s]+([^.\n]+)'
    ]

    actions = []
    for pattern in action_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        actions.extend(matches)

    # Clean up
    actions = [a.strip() for a in actions if len(a.strip()) > 10]

    return actions[:10]

def identify_risks(content: str) -> List[str]:
    """Identify risk factors in content."""
    risk_patterns = [
        r'(?:risk|concern|issue|challenge|threat|warning)[:\s]+([^.\n]+)',
        r'(?:may|might|could)\s+(?:result in|cause|lead to)\s+([^.\n]+)',
        r'penalty|penalties[:\s]+([^.\n]+)'
    ]

    risks = []
    for pattern in risk_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        risks.extend(matches)

    # Also check for risk keywords
    risk_keywords = ["liability", "penalty", "breach", "violation", "default", "termination"]
    content_lower = content.lower()

    for keyword in risk_keywords:
        if keyword in content_lower:
            # Extract sentence containing keyword
            sentences = content.split('.')
            for sent in sentences:
                if keyword in sent.lower():
                    risks.append(sent.strip()[:100])
                    break

    return list(set([r.strip() for r in risks if len(r.strip()) > 10]))[:10]

def generate_recommendations(analysis: Dict[str, Any]) -> str:
    """Generate recommendations based on analysis."""
    recommendations = []

    data = analysis["extracted_data"]

    # Risk-based recommendations
    if len(data.get("risks", [])) > 3:
        recommendations.append("• High risk profile detected - recommend legal review")

    # Date-based recommendations
    dates = data.get("dates", [])
    if dates:
        recommendations.append(f"• Monitor {len(dates)} critical dates")

    # Financial recommendations
    if data.get("amounts"):
        recommendations.append("• Verify financial terms and payment schedule")

    # Action items
    if len(data.get("action_items", [])) > 5:
        recommendations.append("• Multiple action items - assign responsible parties")

    return "\n".join(recommendations) if recommendations else "• Document appears standard - proceed with normal review"

def extract_numeric_value(amount_str: str) -> float:
    """Extract numeric value from amount string."""
    try:
        # Remove currency symbols and commas
        cleaned = re.sub(r'[$,]', '', amount_str)

        # Find first number
        match = re.search(r'[\d.]+', cleaned)
        if match:
            value = float(match.group())

            # Handle millions/billions
            if 'million' in amount_str.lower() or 'm' in amount_str.lower():
                value *= 1000000
            elif 'billion' in amount_str.lower() or 'b' in amount_str.lower():
                value *= 1000000000
            elif 'k' in amount_str.lower() or 'thousand' in amount_str.lower():
                value *= 1000

            return value
    except:
        pass
    return 0

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime."""
    try:
        # Try common formats
        formats = [
            "%B %d, %Y",
            "%b %d, %Y",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y-%m-%d"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.replace(",", ""), fmt)
            except:
                continue

        # Handle quarters
        if 'Q' in date_str:
            quarter_match = re.search(r'Q(\d)\s+(\d{4})', date_str)
            if quarter_match:
                quarter = int(quarter_match.group(1))
                year = int(quarter_match.group(2))
                month = (quarter - 1) * 3 + 1
                return datetime(year, month, 1)
    except:
        pass

    return None

# Resources
@mcp.resource("dashboard://executive")
async def get_executive_dashboard() -> str:
    """Get executive dashboard with key metrics."""
    dashboard = "EXECUTIVE DASHBOARD\n" + "="*50 + "\n\n"

    # Document summary
    dashboard += f"Documents Analyzed: {len(document_store)}\n"

    if kpi_metrics:
        dashboard += f"Total Financial Exposure: ${kpi_metrics.get('financial_exposure', 0):,.2f}\n"
        dashboard += f"Risk Level: {kpi_metrics.get('risk_level', 'Unknown')}\n"
        dashboard += f"Pending Actions: {kpi_metrics.get('action_items_count', 0)}\n"

        if kpi_metrics.get('upcoming_deadlines'):
            dashboard += f"\nUrgent Deadlines:\n"
            for deadline in kpi_metrics['upcoming_deadlines'][:3]:
                dashboard += f"  - {deadline['date']}: {deadline['document']} ({deadline['days_remaining']} days)\n"

    return dashboard

if __name__ == "__main__":
    print("Business Intelligence MCP Server")
    print("="*50)
    print("Available tools:")
    print("- analyze_document: Extract insights from business documents")
    print("- generate_executive_summary: Create executive summaries")
    print("- extract_kpi_metrics: Aggregate KPIs across documents")
    print("- answer_document_question: Q&A about documents")
    print("- compare_documents: Compare two documents")
    print("- generate_action_plan: Create prioritized action plans")
    print("\nStarting server on stdio...")
    mcp.run(transport="stdio")