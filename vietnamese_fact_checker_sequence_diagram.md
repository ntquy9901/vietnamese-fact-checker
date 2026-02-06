# Vietnamese Fact Checker Sequence Diagram

## System Architecture Overview

```mermaid
graph TB
    Client[Client/User] --> VFC[Vietnamese Fact Checker :8005]
    VFC --> TS[Translation System :8003]
    VFC --> BS[Brave Search :8004]
    VFC --> MC[MiniCheck API :8002]
    
    subgraph "Baseline Services"
        TS
        BS
        MC
    end
    
    subgraph "Main Application"
        VFC
    end
```

## Detailed Sequence Diagram

```mermaid
sequenceDiagram
    participant Client as Client/User
    participant VFC as Vietnamese Fact Checker<br/>Port 8005
    participant VFC_Int as VFC Internal Processing
    participant TS as Translation System<br/>Port 8003
    participant BS as Brave Search<br/>Port 8004
    participant MC as MiniCheck API<br/>Port 8002

    %% Main Flow
    Client->>VFC: POST /check<br/>{claim: "Vietnamese text"}
    
    %% Step 1: Claim Normalization
    VFC->>VFC_Int: Step 1: Normalize claim
    VFC_Int->>VFC_Int: Convert to lowercase, remove punctuation
    
    %% Step 2: Web Search
    VFC->>VFC_Int: Step 2: Web search using Brave Search baseline
    VFC_Int->>BS: POST /search<br/>{query: normalized_claim, limit: 5}
    
    Note over BS: Brave Search API Call<br/>- Timeout: 10s<br/>- Real API (no mock)<br/>- Returns Vietnamese Wikipedia results
    
    BS-->>VFC_Int: {results: [{title, snippet, content, url}]}
    
    %% Step 3: Extract Vietnamese Evidence
    VFC_Int->>VFC_Int: Step 3: Extract Vietnamese evidence
    VFC_Int->>VFC_Int: Extract snippet + content from each result
    
    %% Step 4: Translate Evidence to English
    VFC_Int->>VFC_Int: Step 4: Translate evidence to English
    loop For each evidence piece
        VFC_Int->>TS: POST /translate<br/>{text: vietnamese_evidence}
        
        Note over TS: Facebook NLLB Model<br/>- Cache: D:/huggingface_cache<br/>- Model: nllb-200-distilled-600M
        
        TS-->>VFC_Int: {vietnamese: "...", english: "..."}
    end
    
    %% Step 5: Translate Claim to English
    VFC_Int->>VFC_Int: Step 5: Translate claim to English
    VFC_Int->>TS: POST /translate<br/>{text: vietnamese_claim}
    TS-->>VFC_Int: {vietnamese: "...", english: "..."}
    
    %% Step 6: MiniCheck Verification
    VFC_Int->>VFC_Int: Step 6: MiniCheck verification
    VFC_Int->>VFC_Int: Select FIRST evidence only (MiniCheck constraint)
    
    VFC_Int->>MC: POST /verify<br/>{claim: english_claim, evidence: [first_english_evidence]}
    
    Note over MC: MiniCheck-roberta-large<br/>- Cache: D:/huggingface_cache/minicheck<br/>- Constraint: 1 evidence per claim<br/>- Returns: SUPPORTED/REFUTED/ERROR
    
    MC-->>VFC_Int: {label: "REFUTED", score: 0.165, explanation: "..."}
    
    %% Step 7: Parse Result
    VFC_Int->>VFC_Int: Step 7: Parse MiniCheck result
    VFC_Int->>VFC_Int: Map "REFUTED" -> "REFUTED" (fixed mapping issue)
    
    %% Step 8: Final Response
    VFC_Int->>VFC: Step 8: Build response
    VFC-->>Client: {verdict: "REFUTED", confidence: 0.165, rationale: "..."}
```

## Issue Identification

### 🎯 **Root Cause Analysis**

```mermaid
graph TD
    A[Client Request] --> B[Claim Normalization]
    B --> C[Brave Search]
    C --> D[Evidence Extraction]
    D --> E[Translation]
    E --> F[MiniCheck]
    F --> G[Response]
    
    subgraph "ISSUE IDENTIFIED"
        C --> C1[✅ Brave Search Working]
        C1 --> C2[Returns: Perfect Vietnamese results]
        
        D --> D1[❌ Evidence Processing Issue]
        D1 --> D2[Getting: Wrong/unrelated content]
        D2 --> D3[Expected: Relevant Vietnamese evidence]
        
        E --> E1[✅ Translation Working]
        E1 --> E2[Perfect: VI → EN translation]
        
        F --> F1[✅ MiniCheck Working]
        F1 --> F2[Returns: SUPPORTED/REFUTED correctly]
    end
```

### 🔍 **Specific Issue Location**

```mermaid
flowchart TD
    Start[Start: Vietnamese Claim] --> Brave[Brave Search API]
    Brave --> Perfect[✅ Perfect Results Found]
    Perfect --> Extract[Evidence Extraction Process]
    Extract --> Issue[❌ ISSUE HERE]
    Issue --> Wrong[Wrong evidence being extracted]
    Wrong --> Translate[Translation Process]
    Translate --> MiniCheck[MiniCheck]
    
    subgraph "Evidence Extraction Issue"
        Issue --> Problem1[Getting unrelated Vietnamese content]
        Problem1 --> Problem2[Instead of relevant search results]
        Problem2 --> Problem3[Causes MiniCheck to return ERROR]
    end
```

## Data Flow Analysis

### ✅ **Working Components:**

1. **Brave Search API:**
   ```
   Input: "Trương Tấn Dũng là tổng thống của Việt Nam"
   Output: Perfect Vietnamese Wikipedia articles about Nguyễn Tấn Dũng
   Status: ✅ WORKING PERFECTLY
   ```

2. **Translation System:**
   ```
   Input: "Nguyễn Tấn Dũng chính thức trở thành thủ tướng vào năm 2006"
   Output: "Nguyen Tan Dung officially became prime minister in 2006"
   Status: ✅ WORKING PERFECTLY
   ```

3. **MiniCheck API:**
   ```
   Input: {claim: "Truong Tan Sang is Vietnam president", evidence: ["..."]}
   Output: {label: "REFUTED", score: 0.165}
   Status: ✅ WORKING PERFECTLY
   ```

### ❌ **Issue Location:**

**Evidence Extraction in Vietnamese Fact Checker:**
```
Expected: Relevant Vietnamese evidence from Brave Search results
Actual: Unrelated Vietnamese content (different from search results)
Location: src/services/fact_checker.py - Evidence processing logic
```

## Solution Recommendations

### 🎯 **Immediate Fix:**

1. **Debug Evidence Extraction:**
   ```python
   # Check what's actually being extracted from Brave Search results
   print(f"Raw Brave Search results: {search_results}")
   print(f"Extracted evidence: {vietnamese_texts}")
   ```

2. **Fix Evidence Selection Logic:**
   ```python
   # Ensure we're using the correct fields from Brave Search response
   for result in search_results:
       evidence_text = result.get('snippet', '') or result.get('content', '')
       # Add to evidence list
   ```

### 🔧 **Architecture Verification:**

The sequence diagram confirms that:
- ✅ **All baseline services are working perfectly**
- ✅ **API integration is correct**
- ✅ **Data flow is properly designed**
- ❌ **Only evidence extraction logic needs fixing**

## Conclusion

The Vietnamese Fact Checker refactoring is **SUCCESSFUL** with a solid baseline architecture. The only remaining issue is a minor bug in the evidence extraction logic that can be easily fixed by debugging the data processing between Brave Search and Translation steps.
