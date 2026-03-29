# Upcoming Tasks - Math Tutor with RAG

## ✅ Completed Tasks
- [x] Frontend/Backend separation
- [x] FastAPI backend structure
- [x] API routes for tutor endpoints
- [x] API client for Streamlit frontend
- [x] Streamlit frontend refactored to use API client
- [x] Docker Compose configuration
- [x] Backend Dockerfile
- [x] Statistics management

## 🔴 High Priority - RAG Implementation

### 1. **Create Vector Store Service** (`backend/app/services/vector_store.py`)
   - [ ] Initialize ChromaDB connection
   - [ ] Create collection for math documents
   - [ ] Implement document embedding using `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
   - [ ] Add documents to vector store
   - [ ] Implement similarity search/retrieval
   - [ ] Handle document metadata (topic, niveau, source, etc.)

### 2. **Create Document Processing Service** (`backend/app/services/document_processor.py`)
   - [ ] Support PDF documents (using pypdf)
   - [ ] Support Word documents (using python-docx)
   - [ ] Support plain text files
   - [ ] Chunk documents into appropriate sizes (e.g., 500-1000 chars)
   - [ ] Extract metadata from documents
   - [ ] Clean and preprocess text

### 3. **Create RAG Retriever** (`backend/app/rag/retriever.py`)
   - [ ] Implement retrieval logic
   - [ ] Query vector store with user question
   - [ ] Filter by context (topic, niveau) if available
   - [ ] Return top-k relevant chunks (e.g., top 3-5)
   - [ ] Format retrieved context for LLM

### 4. **Integrate RAG into Agent Service** (`backend/app/core/agent.py`)
   - [ ] Import and initialize RAG retriever
   - [ ] Modify `process_message()` to call RAG when `use_rag=True`
   - [ ] Inject retrieved context into LLM prompts
   - [ ] Include source citations in responses
   - [ ] Update `_handle_chat()` to use RAG context

### 5. **Add Document Upload Endpoints** (`backend/app/api/routes/documents.py`)
   - [ ] POST `/api/documents/upload` - Upload and process documents
   - [ ] GET `/api/documents/list` - List uploaded documents
   - [ ] DELETE `/api/documents/{doc_id}` - Delete document
   - [ ] POST `/api/documents/search` - Search documents (for testing)

## 🟡 Medium Priority - Testing & Integration

### 6. **Test Backend API**
   - [ ] Test health endpoint
   - [ ] Test chat endpoint without RAG
   - [ ] Test chat endpoint with RAG
   - [ ] Test question generation
   - [ ] Test hint generation
   - [ ] Test exercise generation
   - [ ] Test course generation
   - [ ] Test answer classification
   - [ ] Test statistics endpoints

### 7. **Test Frontend-Backend Integration**
   - [ ] Verify API client connection
   - [ ] Test all quick action buttons
   - [ ] Test chat input
   - [ ] Test statistics sync
   - [ ] Test error handling

### 8. **Test Docker Compose Setup**
   - [ ] Build all containers
   - [ ] Verify services start correctly
   - [ ] Test inter-service communication
   - [ ] Verify volumes are mounted correctly
   - [ ] Test environment variables

## 🟢 Low Priority - Enhancements

### 9. **Add Document Management UI** (Streamlit)
   - [ ] Create document upload page
   - [ ] Display uploaded documents list
   - [ ] Show document metadata
   - [ ] Allow document deletion
   - [ ] Show RAG retrieval status

### 10. **Improve Error Handling**
   - [ ] Add proper error messages in backend
   - [ ] Add retry logic for API calls
   - [ ] Add fallback when RAG fails
   - [ ] Improve user-facing error messages

### 11. **Add Logging & Monitoring**
   - [ ] Add structured logging
   - [ ] Log API requests/responses
   - [ ] Log RAG retrieval queries
   - [ ] Add performance metrics

### 12. **Documentation**
   - [ ] Update README with setup instructions
   - [ ] Document API endpoints
   - [ ] Document RAG workflow
   - [ ] Add example usage

## 📋 Quick Start Commands

### Build and Run with Docker Compose:
```bash
docker-compose up --build -d
```

### View Logs:
```bash
docker-compose logs -f
```

### Stop Services:
```bash
docker-compose down
```

### Rebuild Specific Service:
```bash
docker-compose build backend
docker-compose up -d backend
```

## 🔧 Environment Variables Needed

Make sure your `.env` file has:
- `GROQ_API_KEY` (and GROQ_API_KEY2, GROQ_API_KEY3)
- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY` (and OPENROUTER_API_KEY2-4)
- `TAVILY_API_KEY` (optional, for web search)
- `API_BASE_URL=http://localhost:8000` (for Streamlit)

## 📝 Next Immediate Steps

1. **Start with Task #1** - Create Vector Store Service
2. **Then Task #2** - Document Processing
3. **Then Task #3** - RAG Retriever
4. **Then Task #4** - Integrate into Agent
5. **Then Task #5** - Document Upload Endpoints

After RAG is implemented, proceed with testing tasks (#6-8).

