content = """
# F1 Race Strategy System - Architecture Documentation

## System Overview
This system is a professional motorsport strategy simulation platform
that provides real-time telemetry analysis and race strategy recommendations.

## Module Descriptions

### 1. TelemetryDataGenerator (Backend )
- Generates realistic race telemetry data
- Provides: lap timing, tyre wear, fuel level, ERS data
- Connects to: StrategyEngine, WebSocketServer

### 2. StrategyEngine (Backend)
- Core strategy calculation module
- Analyzes: tyre wear, fuel, ERS, traffic
- Output: strategy recommendations

### 3. AIIntegrationLayer (Backend)
- Interprets telemetry data
- Generates intelligent recommendations
- Provides race insights

### 4. WebSocketServer (Backend)
- Real-time data broadcasting
- Connects backend to frontend
- Handles live updates

### 5. WhatIfSimulator (Backend)
- Simulates different race scenarios
- Compares: Safety Car, tyre strategies, fuel modes
- Output: race outcome predictions

### 6. ReportingModule (Documentation)
- Generates strategy reports using IBM Docling
- Exports race summaries
- Creates telemetry summaries
- Produces visualization charts
- Documents simulation reports

### 7. DocumentationSystem (Documentation)
- Creates PDF reports
- Maintains race summaries
- Archives strategy data
- Exports telemetry logs

### 8. FrontendDashboard
- Displays live telemetry charts
- Shows strategy recommendations
- Real-time metrics display

## Data Flow
TelemetryDataGenerator
        ↓
   WebSocketServer
        ↓
   StrategyEngine
     ↓         ↓
AILayer    WhatIfSimulator
     ↓         ↓
  ReportingModule (Ifrah)
        ↓
 DocumentationSystem
        ↓
  FrontendDashboard

## Technologies
- Python, FastAPI, WebSockets (Backend)
- IBM Docling, Matplotlib, Pandas (Documentation)
- Draw.io, GitHub, VS Code (Tools)
"""

import os
os.makedirs("documentation/architecture_docs", exist_ok=True)

with open("documentation/architecture_docs/architecture_explanation.md", "w", encoding="utf-8") as f:
    f.write(content)

print(content)
print("✅ Saved: documentation/architecture_docs/architecture_explanation.md")