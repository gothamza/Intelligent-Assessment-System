# Setup Guide - Document Management & RAG

## 🚀 Quick Start

### 1. Build and Run with Docker Compose

```bash
docker-compose up --build -d
```

This will start:
- **ChromaDB** on port `8001`
- **FastAPI Backend** on port `8000`
- **Streamlit Frontend** on port `8502`

### 2. Access the Application

- **Streamlit App**: http://localhost:8502
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ChromaDB**: http://localhost:8001

## 📚 Using Document Management

### Step 1: Upload Documents

1. Navigate to **"📚 Gestion Documents"** page in Streamlit
2. Click "Choose File" and select a PDF, Word, or TXT file
3. Fill in metadata (optional but recommended):
   - **Sujet**: Topic (Algèbre, Géométrie, etc.)
   - **Niveau**: Grade level (7ème année, etc.)
   - **Source**: Where the document came from
   - **Description**: Brief description
4. Click **"🚀 Télécharger et Indexer"**
5. Wait for processing (document is chunked and embedded)

### Step 2: Select Documents for Chat

1. In the **sidebar** of the document management page:
   - Check the documents you want to use as context
   - Or click **"✅ Sélectionner tous les documents"**
2. Selected documents are stored in session state
3. These will be used as RAG context in the chat

### Step 3: Use RAG in Chat

1. Navigate to **"💬 Tuteur Interactif"** page
2. You'll see which documents are selected (if any)
3. Ask questions related to your uploaded documents
4. The AI will use document context to answer
5. Check **"📚 Sources RAG"** expander to see which documents were used

## 🔧 Configuration

### Environment Variables (.env)

```env
# API Keys
GROQ_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here

# Backend URL (for Streamlit)
API_BASE_URL=http://localhost:8000

# ChromaDB (for Docker)
CHROMA_HOST=chromadb
CHROMA_PORT=8000
```

### Directory Structure

The following directories will be created automatically:
```
data/
  ├── uploads/          # Uploaded document files
  └── chroma_db/        # ChromaDB persistent storage
```

## 📝 Example Workflow

1. **Upload a math textbook chapter** (PDF)
   - Topic: "Algèbre"
   - Niveau: "10ème année"
   - Description: "Chapitre sur les équations"

2. **Select the document** in the sidebar

3. **Go to chat** and ask:
   - "Explique-moi comment résoudre une équation du second degré"
   - The AI will use content from your uploaded document!

4. **Check sources** to see which parts of the document were used

## 🐛 Troubleshooting

### Backend not connecting
- Check if backend is running: `docker-compose ps`
- Check logs: `docker-compose logs backend`
- Verify API_BASE_URL in .env

### Documents not appearing
- Check if backend is running
- Check browser console for errors
- Verify document upload succeeded (check backend logs)

### RAG not working
- Ensure documents are selected in document management page
- Check if ChromaDB is running: `docker-compose ps chromadb`
- Verify document_ids are being passed in chat context
- Check backend logs for RAG retrieval errors

### ChromaDB connection issues
- In Docker: Use `chromadb` as host
- Locally: Use `localhost` as host
- Check port mapping (8001:8000)

## 📊 Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f streamlit-app
docker-compose logs -f chromadb
```

### Check Service Status
```bash
docker-compose ps
```

### Restart Services
```bash
docker-compose restart backend
docker-compose restart streamlit-app
```

## 🎯 Next Steps

1. Test document upload with a real math document
2. Test RAG retrieval in chat
3. Fine-tune chunk size if needed
4. Add more document types if needed
5. Consider adding document database for persistence

