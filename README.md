# Agentic RFP Processing System

An intelligent system that automatically processes RFPs, selects the best product, and generates honest proposals using LangGraph and AI agents.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

## Features

- **Smart Product Selection**: Selects best-matching product with suitability evaluation (suitable/partial/not suitable)
- **Explainable Decisions**: Provides justification for selection and rejection reasons for other products
- **Zero Hallucination**: Strict prompts prevent AI from inventing requirements or features
- **Critical Requirements Detection**: Identifies missing security, compliance, and mandatory requirements
- **Multi-Agent System**: Technical, Pricing, and Sales agents working in parallel
- **Conditional Workflow**: Automatically skips agents when no suitable product is found

## Tech Stack

- **FastAPI** - REST API
- **LangGraph** - Workflow orchestration
- **LangChain + Claude Sonnet 4** - AI agents 
- **Pydantic** - Data validation

## How It Works

```
RFP → Match Products → Select Best → Evaluate Suitability → Calculate Pricing → Run Agents → Generate Proposal
```

**Decision Logic:**
- Score ≥ 0.8 + no critical gaps = Suitable (Strong)
- Score ≥ 0.6 + no critical gaps = Suitable (Moderate)
- Critical requirements missing = Not Suitable
- Score < 0.6 = Partial (Weak)

**Output includes:**
- Best product with match score and suitability
- Selection justification and rejection reasons
- Pricing breakdown (base + tests + markup)
- AI-generated technical analysis and proposal

## Quick Start

1. **Install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure API key:**
   Create `.env` file:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

3. **Run the server:**
   ```bash
   python main.py
   ```
   Server runs at `http://localhost:8000`

## Usage

**Process an RFP:**
```bash
curl -X POST http://localhost:8000/process-rfp \
  -H "Content-Type: application/json" \
  -d '{"rfp_id": "rfp1"}'
```

Note: RFP files must exist in `data/rfps/` directory (use filename without `.json`).

**API Endpoints:**
- `POST /process-rfp` - Process RFP and generate proposal
- `GET /health` - Health check

## Project Structure

```
agentic-rfp-system/
├── app/
│   ├── agents/          # Technical, Pricing, Sales agents
│   ├── api/             # FastAPI routes
│   ├── core/            # LangGraph workflow & config
│   ├── pipelines/       # RFP processing pipeline
│   ├── schemas/         # Pydantic models
│   ├── services/        # Matching & pricing logic
│   └── output/          # Proposal formatter
├── data/
│   ├── rfps/           # RFP JSON files
│   ├── products.json   # Product catalog
│   ├── pricing.json    # Test costs
│   └── config.json     # System config
└── logs/               # Application logs
```

## Configuration

Edit `data/config.json`:
- `matching_threshold`: Min score for matches (default: 0.3)
- `markup_percentage`: Profit margin (default: 25%)
- `default_tests`: Required testing costs


## Future Enhancements

- **Semantic Matching**: Replace keyword matching with vector embeddings for better accuracy
- **Multi-Product Proposals**: Support bundled solutions and product combinations
- **Database Integration**: Replace JSON files with PostgreSQL/MongoDB
- **Dynamic Pricing**: Add negotiation logic and volume discounts
- **Multi-Language Support**: Process RFPs in multiple languages
- **Advanced Analytics**: Track success rates, common gaps, and proposal patterns
- **Custom Workflows**: User-defined evaluation criteria and approval flows
- **Real-time Collaboration**: Multi-user editing and commenting
- **Integration APIs**: Connect with CRM, ERP, and procurement systems

## Current Limitations

- Keyword-based matching (not semantic)
- Single product selection only
- File-based storage (JSON)
- Basic pricing model

## License

MIT
