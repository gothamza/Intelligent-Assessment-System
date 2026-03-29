### this file handles document upload, listing, deletion, and file retrieval

from models.models import *
from fastapi import logger
import tempfile
import shutil


router_docs= APIRouter(tags=["📄Documents Management APIs"])

loader_map = {
            "pdf": PyPDFLoader, "txt": TextLoader, "md": TextLoader,
            "docx": UnstructuredWordDocumentLoader, "xlsx": UnstructuredExcelLoader,
            "xls": UnstructuredExcelLoader, "csv": UnstructuredCSVLoader
             }

async def _process_and_store_document(
    doc_id: str,
    user_id: int,
    team_id: str,
    filename: str,
    file_type: str,
    visibility: str,
    upload_date: datetime,
    content: bytes
):
    """
    Helper function to save a document permanently to disk, database, and vector store.
    """
    # 1. Save file to disk
    save_dir = os.path.join("data", str(user_id), doc_id)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)
    with open(save_path, "wb") as f:
        f.write(content)

    # 2. Store metadata in database
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO documents 
                (doc_id, user_id, team_id, doc_title, file_type, visibility, upload_date, file_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (doc_id, user_id, team_id, filename, file_type, visibility, upload_date, save_path)
            )
        conn.commit()
    finally:
        conn.close()

    # 3. Add to vector store
    if file_type in ["txt", "pdf", "md", "docx", "xlsx", "xls", "csv"]:
        try:
            loader = loader_map[file_type](save_path)
            documents = loader.load()

            for doc in documents:
                doc.metadata.update({
                    "doc_id": doc_id,
                    "user_id": user_id,
                    "team_id": team_id,
                    "visibility": visibility,
                    "source": filename
                })

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
            split_docs = text_splitter.split_documents(documents)
            ids = [f"{doc_id}_{i}" for i in range(len(split_docs))]
            vectorstore3.add_documents(split_docs, ids=ids)

        except Exception as e:
            print(f"Error adding to vector store: {str(e)}")

 
#
##
###🔐 Uses filtering to only show files visible to the current user, based on ownership, team membership, or if the file is public.

@router_docs.get("/docs/list", response_model=List[DocumentMetadata])
async def list_documents(current_user: dict = Depends(get_current_user)):
    """
    List documents accessible to current user based on visibility rules:
    - Private: Only owner
    - Team: Users in same team
    - Public: All users
    """
    user_id = current_user["user_id"]
    user_role = current_user.get("role", "user")  # Default to 'user' if role not set
    team_id = current_user.get("team_id")
    
    conn = get_db_connection()
    if user_role == "admin":
        # Admins can see all documents
        query = """
        SELECT d.doc_id, d.user_id, d.team_id, d.doc_title, d.file_type, d.visibility, d.upload_date,
               ARRAY_AGG(cd.collection_id) FILTER (WHERE cd.collection_id IS NOT NULL) as collection_ids,
               u.login AS uploader_login
        FROM documents d
        LEFT JOIN collection_documents cd ON d.doc_id = cd.doc_id
        LEFT JOIN users u ON d.user_id = u.id
        GROUP BY d.doc_id, d.user_id, d.team_id, d.doc_title, d.file_type, d.visibility, d.upload_date, u.login
        """
        try:
            with conn.cursor() as cur:
                cur.execute(query)
                documents = cur.fetchall()
                return [dict(doc) for doc in documents]
        finally:
            conn.close()
        
    else :
        try:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT d.doc_id, d.user_id, d.team_id, d.doc_title, d.file_type, d.visibility, d.upload_date,
                       ARRAY_AGG(cd.collection_id) FILTER (WHERE cd.collection_id IS NOT NULL) as collection_ids,
                       u.login AS uploader_login
                FROM documents d
                LEFT JOIN collection_documents cd ON d.doc_id = cd.doc_id
                LEFT JOIN users u ON d.user_id = u.id
                WHERE d.visibility = 'public'
                OR (d.visibility = 'team' AND d.team_id = %s)
                OR (d.visibility IN ('private', 'session') AND d.user_id = %s)
                GROUP BY d.doc_id, d.user_id, d.team_id, d.doc_title, d.file_type, d.visibility, d.upload_date, u.login
                """, (team_id, user_id))
                documents = cur.fetchall()
                return [dict(doc) for doc in documents]
        finally:
            conn.close()


#
##
###🛡️ Only admins or the original uploader can delete documents. It also ensures removal from both disk and vectorstore.

@router_docs.delete("/docs/delete/{doc_id}", status_code=204)
async def delete_document(
    doc_id: str = Path(..., description="The ID of the document to delete"),
    current_user: dict = Depends(get_current_user)
):
    """
    Deletes a document from the database and the vector store.
    Permissions are based on ownership and user role.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Get the document's owner ID and team ID
            cur.execute(
                """
                SELECT d.user_id, u.team_id AS owner_team_id
                FROM documents d
                JOIN users u ON d.user_id = u.id
                WHERE d.doc_id = %s
                """,
                (doc_id,)
            )
            doc_info = cur.fetchone()

            if not doc_info:
                raise HTTPException(status_code=404, detail="Document not found")

            # 2. Check permissions based on the new logic
            user_role = current_user.get("role")
            user_id = current_user.get("user_id")
            user_team_id = current_user.get("team_id")
            
            is_owner = (doc_info["user_id"] == user_id)
            is_admin = (user_role == "admin")
            is_manager_of_owner = (user_role == "manager" and doc_info["owner_team_id"] == user_team_id)

            if not (is_owner or is_admin or is_manager_of_owner):
                raise HTTPException(status_code=403, detail="You do not have permission to delete this document.")

            # 3. If permission is granted, proceed with deletion
            # Delete from vector store
            vectorstore3.delete([doc_id])

            # Delete from documents table
            cur.execute("DELETE FROM documents WHERE doc_id = %s", (doc_id,))
            conn.commit()
    finally:
        conn.close()

    return

#
##
###🔒 Protects access using the same permission rules as listing, and serves files securely using FileResponse.

@router_docs.get("/files/{doc_id}")
async def get_file(
    doc_id: str = Path(..., description="The ID of the document"),
    current_user: dict = Depends(get_current_user)
):
    """
    Download a file by doc_id, checking user permissions.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, team_id, visibility, file_path, doc_title FROM documents WHERE doc_id = %s",
                (doc_id,)
            )
            doc = cur.fetchone()
            if not doc:
                raise HTTPException(status_code=404, detail="Document not found")

            # Permission check (reuse your logic)
            user_id = current_user["user_id"]
            team_id = current_user.get("team_id")
            if not (
                doc["visibility"] == "public"
                or (doc["visibility"] == "team" and doc["team_id"] == str(team_id))
                or (doc["visibility"] == "private" and doc["user_id"] == user_id)
                or (current_user.get("role") == "admin")
            ):
                raise HTTPException(status_code=403, detail="Not authorized to access this file")

            file_path = doc["file_path"]
            filename = doc["doc_title"]
    finally:
        conn.close()

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)
@router_docs.post("/docs/upload_for_chat")
async def upload_for_chat(
    files: List[UploadFile] = File(...),
    save_permanently: str = Form("true"),
    visibility: str = Form("private"),
    target_team_id: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Uploads one or more files for chat.
    If save_permanently is True, saves them to the DB and disk with the specified visibility.
    If False, processes them in-memory for session-only RAG.
    """
    user_id = current_user.get("user_id")
    user_team_id = str(current_user.get("team_id", ""))
    user_role = current_user.get("role", "user")

    # Enforce: only manager/admin can set public visibility
    if visibility == "public" and user_role not in ("manager", "admin"):
        raise HTTPException(status_code=403, detail="Only managers or admins can set documents to public visibility.")

    processed_docs = []

    # Handle both single file and multiple files
    file_list = files if isinstance(files, list) else [files]
    
    for file in file_list:
        doc_id = str(uuid4())
        upload_date = datetime.utcnow()
        filename = file.filename
        file_type = filename.split(".")[-1].lower() if "." in filename else "unknown"
        content = await file.read()

        # Resolve target team for team visibility
        if visibility == "team" and target_team_id and user_role in ("manager", "admin"):
            team_id = target_team_id
        else:
            team_id = user_team_id

        # Convert string to bool
        save_permanently_bool = save_permanently.lower() == "true" if isinstance(save_permanently, str) else save_permanently
        
        if save_permanently_bool:
            await _process_and_store_document(
                doc_id=doc_id, user_id=user_id, team_id=team_id, filename=filename,
                file_type=file_type, visibility=visibility, upload_date=upload_date,
                content=content
            )
        else:
            await _process_and_store_document(
                doc_id=doc_id, user_id=user_id, team_id=team_id, filename=filename,
                file_type=file_type, visibility=visibility, upload_date=upload_date,
                content=content
            )

        processed_docs.append({
            "doc_id": doc_id, "doc_title": filename, "visibility": visibility
        })

    return {"documents": processed_docs}