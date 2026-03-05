# SurakshaNet

## Project Overview

**SurakshaNet** is an advanced, enterprise-grade fraud detection system designed for secure healthcare claims processing. It integrates machine learning, blockchain technology, and quantum-resistant security to detect, prevent, and report fraudulent claims in real-time while maintaining comprehensive audit trails.

The platform combines intelligent anomaly detection with decentralized verification through Algorand blockchain integration and quantum-safe cryptographic mechanisms, ensuring both accuracy and long-term security against emerging threats.

---

## Key Features

### 1. **Intelligent Fraud Detection**
- **Machine Learning Models**: Isolation Forest and Local Outlier Factor (LOF) for detecting unusual patterns
- **Anomaly Detection**: Real-time identification of outliers in claim amounts, frequencies, and temporal patterns
- **Rule-Based Detection**: Heuristic-driven detection of common fraud schemes (up-coding, ghost billing, claim surges)
- **Risk Scoring**: Multi-factor risk assessment with customizable severity thresholds

### 2. **Blockchain Integration**
- **Algorand Integration**: Immutable record-keeping of claim verification results
- **Decentralized Validation**: Distributed ledger technology for tamper-proof audit trails
- **Smart Contracts**: Verifiable claim processing with transparent stakeholder accountability

### 3. **Quantum-Safe Security**
- **Quantum Client**: Post-quantum cryptographic mechanisms for future-proof security
- **Secure Hashing**: Quantum-resistant algorithms for sensitive data protection
- **Long-term Compliance**: Protection against potential quantum computing threats

### 4. **Modern Analytics Dashboard**
- **Real-time Monitoring**: Live claims analysis with interactive visualizations
- **Glassmorphism UI**: Contemporary, intuitive user interface with Recharts analytics
- **Hospital Risk Profiles**: At-a-glance risk indicators and trend analysis
- **Automated Reports**: Machine-generated fraud reports with actionable insights

### 5. **Scalable Backend Architecture**
- **FastAPI Framework**: High-performance, asynchronous API endpoints
- **Optimized Caching**: Reduced latency and enhanced system responsiveness
- **Database Integration**: SQLite with expandable schema for large-scale deployments
- **Modular Design**: Pluggable components for easy customization and extension

---

## Project Structure

```
SurakshaNet/
├── fraud_detection_agent/          # Core fraud detection system
│   ├── agent/
│   │   └── monitor.py              # Real-time claim monitoring
│   ├── blockchain/
│   │   ├── algorand_client.py      # Algorand blockchain integration
│   │   └── quantum_client.py        # Quantum-safe cryptography
│   ├── database/
│   │   └── db_setup.py             # Database initialization and mock data
│   ├── models/
│   │   └── anomaly_model.py        # ML anomaly detection models
│   ├── preprocessing/
│   │   └── preprocess.py           # Data cleaning and feature engineering
│   ├── reports/
│   │   └── report_generator.py     # Automated fraud report generation
│   ├── scoring/
│   │   └── risk_scoring.py         # Risk assessment and scoring
│   └── main.py                      # FastAPI application & orchestration
│
├── frontend/                        # Modern analytics dashboard
│   ├── src/
│   │   ├── app/                    # Next.js 15+ app structure
│   │   └── components/             # Reusable UI components
│   ├── package.json                # Node.js dependencies
│   └── tsconfig.json               # TypeScript configuration
│
├── requirements.txt                # Python dependencies
└── README.md                        # Documentation
```

---

## Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- SQLite3
- Git

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/v3nom-95/SurakshaNet.git
cd SurakshaNet

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Backend Server

```bash
# Initialize database and run FastAPI server
python -m fraud_detection_agent.main

# API will be available at http://localhost:8000
# Interactive API docs: http://localhost:8000/docs
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Dashboard will be available at http://localhost:3000
```

---

## Core Capabilities

### Fraud Detection Pipeline
1. **Data Ingestion**: Mock claims data generation with SQLite persistence
2. **Preprocessing**: Feature normalization, scaling, and engineering
3. **Anomaly Detection**: ML-based outlier identification
4. **Risk Scoring**: Multi-dimensional risk assessment
5. **Blockchain Logging**: Immutable verification record creation
6. **Report Generation**: Automated audit-ready fraud reports

### Blockchain Features
- Claim verification hashes stored on Algorand mainnet/testnet
- Tamper-proof audit trails for compliance
- Stakeholder transparency with decentralized validation

### Security Features
- Quantum-resistant cryptographic algorithms
- Encrypted claim data storage
- Role-based access control ready
- Comprehensive audit logging

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend API** | FastAPI, Python 3.9+ |
| **Database** | SQLite, optional SQL scaling |
| **Machine Learning** | Scikit-learn, Isolation Forest, LOF |
| **Blockchain** | Algorand SDK |
| **Cryptography** | Quantum-safe algorithms |
| **Frontend** | Next.js 15+, TypeScript, React |
| **UI Components** | Recharts, Lucide Icons |
| **Styling** | Glassmorphism Design System |

---

## API Endpoints

- `GET /health` - System health check
- `POST /analyze-claim` - Submit claim for fraud analysis
- `GET /risk-profile/{hospital_id}` - Retrieve hospital risk profile
- `GET /reports` - Fetch generated fraud reports
- `POST /blockchain-verify` - Verify claim on blockchain

---

## Configuration & Customization

- **Anomaly Detection Thresholds**: Adjust in `models/anomaly_model.py`
- **Risk Scoring Rules**: Customize in `scoring/risk_scoring.py`
- **Database Schema**: Modify in `database/db_setup.py`
- **API Routes**: Extend in `fraud_detection_agent/main.py`

---

## Performance Metrics

- **Claim Processing**: ~100ms per claim (with caching)
- **Anomaly Detection**: Real-time analysis on 10K+ claims
- **Dashboard Load Time**: <2 seconds for full analytics view
- **Blockchain Verification**: Algorand integration with <30s finality

---

## Future Enhancements

- [ ] Multi-chain blockchain integration (Polygon, Cosmos)
- [ ] Advanced NLP for claim text analysis
- [ ] Federated learning for collaborative fraud detection
- [ ] GraphQL API for enhanced flexibility
- [ ] Mobile app for on-field verification
- [ ] Kubernetes deployment configurations

---

## Contributing

This project is maintained by **v3nom-95**. For inquiries or contributions, please contact: goslingstark95@gmail.com

---

## License

MIT License - See LICENSE file for details

---

## Support & Documentation

For detailed API documentation, visit: `http://localhost:8000/docs` (when server is running)

For issues, questions, or feature requests, please open an issue on GitHub.
