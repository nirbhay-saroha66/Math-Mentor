flowchart TD

A[User Input] --> B{Input Type}

B --> C[Text]
B --> D[Image]
B --> E[Audio]

D --> F[OCR]
E --> G[Speech To Text]

C --> H[Parser Agent]
F --> H
G --> H

H --> I[Intent Router Agent]

I --> J[Solver Agent]

J --> K[RAG Knowledge Base]
J --> L[Math Solver]

K --> M[Verifier Agent]

M --> N[Explainer Agent]

N --> O[Final Answer]

O --> P[Memory Storage]

P --> Q[Reuse for Similar Question]