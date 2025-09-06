
# AI Auditor - Client Package for RTX 4090

## 🎯 What You Get

### Core System
- **Invoice Audit Engine**: Complete index → match → export pipeline
- **Tie-breaker Logic**: Filename vs. customer matching with configurable weights
- **Number Format Compatibility**: Handles 1,000.00, 1 000,00, and other formats
- **Professional Reports**: Excel, JSON, CSV outputs with executive summaries

### Web Interface
- **Upload Panel**: Drag-and-drop PDF/ZIP files
- **Audit Configuration**: Adjust tie-breaker weights and processing options
- **Results Dashboard**: View top non-conformities and download packages
- **Real-time Processing**: Live progress updates

### Local AI Assistant
- **RAG-based Q&A**: Ask questions about your audit data
- **Offline Operation**: Works without internet after model download
- **Multilingual Support**: Polish and English
- **Accounting Expertise**: Trained on audit and accounting knowledge

### Integrations (Ready for Configuration)
- **KRS Integration**: Company data enrichment pipeline
- **VAT Whitelist**: Tax validation pipeline
- **OCR Processing**: GPU-accelerated text extraction

## 🖥️ System Requirements

### Hardware
- **GPU**: NVIDIA RTX 4090 (24 GB VRAM)
- **CPU**: 8+ cores
- **RAM**: 32 GB+
- **Storage**: 10+ GB free space

### Software
- **OS**: Linux x86_64 (Ubuntu 22.04 LTS recommended)
- **NVIDIA Drivers**: Latest version
- **CUDA**: 12.x
- **Python**: 3.10-3.12

## 🚀 Quick Start

### 1. Setup
```bash
# Run setup script
./scripts/setup_4090.sh
```

### 2. Start System
```bash
# Start all services
./scripts/start_4090.sh
```

### 3. Access Interface
- **Web Panel**: http://localhost:8501
- **API Server**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs

## 📊 Usage Examples

### Web Interface
1. Open http://localhost:8501
2. Upload PDF files (or ZIP archive)
3. Upload POP data file
4. Configure tie-breaker settings
5. Click "Run Audit"
6. Download results package

### CLI Usage
```bash
# Demo validation
ai-auditor validate --demo --file invoice.pdf --pop-file pop.xlsx

# Bulk validation
ai-auditor validate --bulk --input-dir ./pdfs --pop-file pop.xlsx --output-dir ./results

# With custom tie-breaker settings
ai-auditor validate --bulk --input-dir ./pdfs --pop-file pop.xlsx \
  --tiebreak-weight-fname 0.7 --tiebreak-min-seller 0.4 --amount-tol 0.01
```

### AI Assistant
1. Open web interface
2. Go to "AI Assistant" tab
3. Ask questions like:
   - "What are the top mismatches in my audit?"
   - "Explain the tie-breaker logic"
   - "How do I interpret the confidence scores?"

## 📁 Output Files

### Audit Results
- `Audyt_koncowy.xlsx` - Complete Excel report
- `verdicts.jsonl` - Detailed matching results
- `verdicts_summary.json` - Executive summary
- `verdicts_top50_mismatches.csv` - Top mismatches
- `All_invoices.csv` - All processed invoices
- `ExecutiveSummary.pdf` - Executive summary (optional)

### System Files
- `logs/` - System logs
- `data/` - Processed data
- `models/` - AI models
- `outputs/` - Audit results

## 🔧 Configuration

### AI Models
Edit `config/ai_config.json` to adjust:
- LLM model settings
- Embedding model configuration
- OCR options
- RAG parameters

### Processing Options
- File size limits
- Memory usage
- Processing threads
- Output formats

## 🧪 Testing

### Run Tests
```bash
# Complete test suite
python3 scripts/smoke_all.py

# Performance test
python3 scripts/smoke_perf_200.py

# Tie-breaker A/B test
python3 scripts/smoke_tiebreak_ab.py
```

### Verify Installation
```bash
# Check GPU
nvidia-smi

# Check models
python3 -c "from core.ai_assistant import create_ai_assistant; print('AI ready')"

# Check web interface
curl http://localhost:8501
```

## 🛡️ Security

### Data Protection
- All processing is local (no cloud)
- No data leaves your system
- Encrypted storage options
- Audit trails for all operations

### Access Control
- Local network access only
- Configurable authentication
- Role-based permissions
- Session management

## 📞 Support

### Documentation
- `docs/` - Complete documentation
- `PRODUCTION_CHECKLIST.md` - Feature status
- `docs/CONTEXT_FOR_CURSOR.md` - Development context

### Troubleshooting
- Check logs in `logs/` directory
- Run diagnostic scripts
- Verify system requirements
- Check model downloads

## 🎯 Performance

### Benchmarks
- **PDF Processing**: >20 files/second
- **Matching**: >100 matches/second
- **Memory Usage**: <100MB per 1000 records
- **AI Response**: <2 seconds per question

### Optimization
- GPU acceleration enabled
- 4-bit model quantization
- Batch processing
- Memory-efficient streaming

---

**Your AI Auditor system is ready for production use!** 🚀
