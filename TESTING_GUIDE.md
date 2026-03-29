# Testing Guide - Document Management & RAG

## 🎯 Recommended Testing Order

Test in this order to catch issues early:

1. ✅ **Backend Health Check** (30 seconds)
2. ✅ **Document Upload** (2-3 minutes)
3. ✅ **Document Listing & Selection** (1 minute)
4. ✅ **RAG in Chat** (3-5 minutes)

---

## Test 1: Backend Health Check ✅

**Goal**: Verify backend API is accessible

### Steps:
1. Open browser and go to: http://localhost:8000/docs
2. You should see FastAPI automatic documentation (Swagger UI)
3. Look for these endpoints:
   - `/api/tutor/chat`
   - `/api/documents/upload`
   - `/api/documents/list`
   - `/api/documents/{document_id}`

### ✅ Success Criteria:
- Swagger UI loads
- You can see all API endpoints
- No errors in the interface

### ❌ If Failed:
```bash
# Check backend logs
docker-compose logs backend

# Check if backend is running
docker-compose ps
```

---

## Test 2: Document Upload 📤

**Goal**: Test document upload and processing

### Steps:
1. Open Streamlit app: http://localhost:8502
2. Navigate to **"📚 Gestion Documents"** page (in sidebar)
3. **Upload a test document:**
   - Click "Choose File"
   - Select a PDF, Word (.docx), or TXT file
   - **Tip**: Use a small math document (2-3 pages) for testing
4. **Fill metadata** (optional but recommended):
   - **Nom**: Test Document
   - **Sujet**: Algèbre
   - **Niveau**: 10ème année
   - **Source**: Test
   - **Description**: Document de test
5. Click **"🚀 Uploader et Traiter le Document"**
6. Wait for processing (10-30 seconds)

### ✅ Success Criteria:
- Success message appears: "Document '...' uploadé et traité avec succès !"
- Document ID is shown
- Document appears in the list below
- Number of chunks is displayed

### ❌ If Failed:
```bash
# Check backend logs for errors
docker-compose logs -f backend

# Check if ChromaDB is running
docker-compose ps chromadb
```

### 🔍 Verify in Backend:
```bash
# Test API directly (optional)
curl http://localhost:8000/api/documents/list
```

---

## Test 3: Document Listing & Selection 📋

**Goal**: Verify documents are stored and can be selected

### Steps:
1. On the **"📚 Gestion Documents"** page
2. Scroll to **"📄 Documents Disponibles"** section
3. **Check the document list:**
   - Your uploaded document should appear
   - Metadata should be visible
   - Number of chunks should be shown
4. **Select document for chat:**
   - Find the multiselect dropdown: "Sélectionnez les documents à utiliser comme contexte RAG"
   - Select your uploaded document
   - You should see: "Documents sélectionnés pour le chat: 1 document(s)"
5. **Expand document details:**
   - Click on the expander to see full metadata
   - Verify all fields are correct

### ✅ Success Criteria:
- Document appears in the list
- You can select/deselect documents
- Selection count updates
- Document metadata is correct

### ❌ If Failed:
- Check browser console (F12) for JavaScript errors
- Verify session state is working (try refreshing)

---

## Test 4: RAG in Chat 💬

**Goal**: Test full RAG workflow - chat using document context

### Prerequisites:
- ✅ Document uploaded (Test 2)
- ✅ Document selected (Test 3)

### Steps:
1. Navigate to **"💬 Tuteur Interactif"** page
2. **Verify selected documents:**
   - Look for expander: "📚 Documents utilisés comme contexte RAG"
   - Your selected document should be listed
3. **Test chat with RAG:**
   - Type a question related to your uploaded document
   - Example: "Explique-moi [topic from your document]"
   - Click Send or press Enter
   - Wait for response (may take 10-30 seconds first time)
4. **Check RAG sources:**
   - Look for expander: "📚 Sources RAG" in the assistant's response
   - Click to expand
   - You should see:
     - Document name(s) used
     - Relevance score(s)

### ✅ Success Criteria:
- Response is generated
- RAG sources expander appears
- Your document is listed as a source
- Response is relevant to your document content

### ❌ If Failed:
```bash
# Check backend logs for RAG errors
docker-compose logs -f backend | grep -i "rag\|vector\|chroma"

# Check if document IDs are being passed
docker-compose logs backend | grep -i "document_id"
```

### 🔍 Additional Tests:

**Test without RAG:**
- Deselect all documents
- Ask the same question
- Response should still work (without RAG sources)

**Test with multiple documents:**
- Upload a second document
- Select both documents
- Ask a question
- Multiple sources should appear

---

## Test 5: Document Deletion 🗑️

**Goal**: Test document removal

### Steps:
1. Go to **"📚 Gestion Documents"** page
2. Find your test document in the list
3. Expand document details
4. Click **"Supprimer [document name]"** button
5. Confirm deletion

### ✅ Success Criteria:
- Success message appears
- Document disappears from list
- Document is removed from ChromaDB
- Cannot use deleted document in chat

---

## 🐛 Common Issues & Solutions

### Issue: "Backend connection failed"
**Solution:**
- Check `API_BASE_URL` in `.env` file
- Verify backend is running: `docker-compose ps`
- Check backend logs: `docker-compose logs backend`

### Issue: "Document upload fails"
**Solution:**
- Check file size (should be < 10MB for testing)
- Verify file type (PDF, DOCX, TXT only)
- Check backend logs for specific error
- Ensure ChromaDB is running

### Issue: "RAG sources not appearing"
**Solution:**
- Verify document is selected in document management page
- Check backend logs for RAG retrieval errors
- Try with a different question
- Verify document was actually processed (check chunk count)

### Issue: "ChromaDB connection error"
**Solution:**
- Check ChromaDB is running: `docker-compose ps chromadb`
- Verify `CHROMA_HOST=chromadb` in backend environment
- Check ChromaDB logs: `docker-compose logs chromadb`

---

## 📊 Quick Test Checklist

Use this checklist to track your testing:

```
[ ] Test 1: Backend Health Check
    [ ] Swagger UI loads
    [ ] All endpoints visible
    
[ ] Test 2: Document Upload
    [ ] Upload succeeds
    [ ] Document appears in list
    [ ] Chunks are created
    
[ ] Test 3: Document Selection
    [ ] Documents listed correctly
    [ ] Selection works
    [ ] Metadata displayed
    
[ ] Test 4: RAG in Chat
    [ ] Documents shown in chat page
    [ ] Response generated
    [ ] RAG sources appear
    [ ] Sources are correct
    
[ ] Test 5: Document Deletion
    [ ] Deletion succeeds
    [ ] Document removed from list
    [ ] Cannot use in chat
```

---

## 🚀 Quick Test Commands

```bash
# View all logs
docker-compose logs -f

# View backend logs only
docker-compose logs -f backend

# View ChromaDB logs only
docker-compose logs -f chromadb

# Check service status
docker-compose ps

# Restart backend (if needed)
docker-compose restart backend

# Rebuild and restart (if code changed)
docker-compose up --build -d backend
```

---

## ✅ Next Steps After Testing

If all tests pass:
1. Upload real math documents
2. Test with multiple documents
3. Test different question types
4. Test edge cases (empty documents, very long documents, etc.)

If tests fail:
1. Note which test failed
2. Check logs for error messages
3. Review the error handling section above
4. Fix issues and re-test

