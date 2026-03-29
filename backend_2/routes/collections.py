from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from models.models import get_db_connection
from auth.oauth2 import get_current_user

# --- Pydantic Models for API Data Validation ---

class CollectionCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    parent_id: Optional[int] = None
    visibility: str = "private" # 'private', 'team', or 'public'
    team_id: Optional[str] = None  # Allows admin/manager to target a specific team when visibility='team'

class CollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None

class DocumentsToModify(BaseModel):
    doc_ids: List[str]

# --- General Collections Router (for all authenticated users) ---

router_collections = APIRouter(
    prefix="/collections",
    tags=["📚 Collections"],
    dependencies=[Depends(get_current_user)]
)

# Ensure schema for collections table
def _ensure_collections_schema():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                ALTER TABLE collections
                ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
                """
            )
            conn.commit()
    finally:
        conn.close()

# Search across collections and documents
@router_collections.get("/search", summary="Search collections and documents by name/text")
def search_collections_and_documents(
    q: str,
    vis: Optional[str] = None,
    uploader: Optional[str] = None,  # comma-separated list of exact logins
    current_user: dict = Depends(get_current_user),
):
    term = f"%{q}%"
    conn = get_db_connection()
    try:
        _ensure_collections_schema()
        with conn.cursor() as cur:
            results = {"collections": [], "documents": []}

            # Collections visible to user
            collections_sql = [
                "SELECT c.id, c.name, c.description, c.parent_id, c.team_id, c.visibility,",
                "       c.created_at,",
                "       u.login AS creator_login",
                "FROM collections c",
                "LEFT JOIN users u ON c.created_by = u.id",
                "WHERE c.name ILIKE %s",
            ]
            collections_params = [term]
            # RBAC visibility
            if current_user['role'] != 'admin':
                collections_sql.append(
                    "AND (c.visibility = 'public' OR (c.visibility = 'team' AND c.team_id = %s) OR (c.visibility = 'private' AND c.created_by = %s))"
                )
                collections_params.extend([current_user['team_id'], current_user['user_id']])
            # Optional filters
            if vis and vis in ('session', 'private', 'team', 'public'):
                collections_sql.append("AND c.visibility = %s")
                collections_params.append(vis)
            if uploader:
                uploader_list = [u.strip() for u in uploader.split(',') if u.strip()]
                if uploader_list:
                    placeholders = ",".join(["%s"] * len(uploader_list))
                    collections_sql.append(f"AND u.login IN ({placeholders})")
                    collections_params.extend(uploader_list)
            collections_sql.append("ORDER BY c.name")
            cur.execute("\n".join(collections_sql), tuple(collections_params))
            results["collections"] = cur.fetchall()

            # Documents visible to user
            documents_sql = [
                "SELECT d.doc_id, d.doc_title, d.file_type, d.visibility, d.upload_date,",
                "       u.login AS uploader_login",
                "FROM documents d",
                "LEFT JOIN users u ON d.user_id = u.id",
                "WHERE d.doc_title ILIKE %s",
            ]
            documents_params = [term]
            if current_user['role'] != 'admin':
                documents_sql.append(
                    "AND (d.visibility = 'public' OR (d.visibility = 'team' AND d.team_id = %s) OR (d.visibility IN ('private','session') AND d.user_id = %s))"
                )
                documents_params.extend([current_user['team_id'], current_user['user_id']])
            if vis and vis in ('session', 'private', 'team', 'public'):
                documents_sql.append("AND d.visibility = %s")
                documents_params.append(vis)
            if uploader:
                uploader_list = [u.strip() for u in uploader.split(',') if u.strip()]
                if uploader_list:
                    placeholders = ",".join(["%s"] * len(uploader_list))
                    documents_sql.append(f"AND u.login IN ({placeholders})")
                    documents_params.extend(uploader_list)
            documents_sql.append("ORDER BY d.doc_title")
            cur.execute("\n".join(documents_sql), tuple(documents_params))
            results["documents"] = cur.fetchall()

            return {"q": q, **results}
    finally:
        conn.close()

# Ensure schema for document attribution (who added the doc into a collection)
def _ensure_collection_documents_schema():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                ALTER TABLE collection_documents
                ADD COLUMN IF NOT EXISTS added_by INTEGER,
                ADD COLUMN IF NOT EXISTS added_at TIMESTAMP DEFAULT NOW();
            """)
            conn.commit()
    finally:
        conn.close()

@router_collections.post("/", status_code=201, summary="Create a new collection")
def create_collection(collection: CollectionCreate, current_user: dict = Depends(get_current_user)):
    """
    Any user can create a collection and set its visibility.
    - 'private': Only the creator can see and manage.
    - 'team': Anyone in the creator's team can see and contribute.
    - 'public': Anyone in the organization can see and contribute.
    """
    user_id = current_user.get("user_id")
    user_team_id = current_user.get("team_id")
    user_role = current_user.get("role", "user")

    # Enforce: only manager/admin can create public collections
    if collection.visibility == "public" and user_role not in ("manager", "admin"):
        raise HTTPException(status_code=403, detail="Only managers or admins can create public collections.")

    conn = get_db_connection()

    # If visibility is 'team', determine which team to bind
    if collection.visibility == 'team':
        if collection.team_id and user_role in ("manager", "admin"):
            team_id = collection.team_id
        else:
            team_id = user_team_id
    else:
        team_id = None

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO collections (name, description, parent_id, created_by, visibility, team_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (collection.name, collection.description, collection.parent_id, user_id, collection.visibility, team_id)
        )
        new_id = cur.fetchone()["id"]
        conn.commit()
    conn.close()
    return {"id": new_id, "message": f"Collection '{collection.name}' created successfully."}

@router_collections.get("/", summary="List all visible collections")
def list_collections(current_user: dict = Depends(get_current_user)):
    """
    Lists collections visible to the user:
    - Admins see all.
    - Others see public collections, their team's collections, and their own private collections.
    """
    _ensure_collections_schema()
    conn = get_db_connection()
    with conn.cursor() as cur:
        if current_user['role'] == 'admin':
            cur.execute("""
                SELECT c.id, c.name, c.description, c.parent_id, c.team_id, c.visibility, c.created_by, c.created_at,
                       u.login AS creator_login
                FROM collections c
                LEFT JOIN users u ON c.created_by = u.id
                ORDER BY c.name
            """)
        else:
            cur.execute(
            """
                SELECT c.id, c.name, c.description, c.parent_id, c.team_id, c.visibility, c.created_by, c.created_at,
                       u.login AS creator_login
                FROM collections c 
                LEFT JOIN users u ON c.created_by = u.id
                WHERE 
                    c.visibility = 'public' OR 
                    (c.visibility = 'team' AND c.team_id = %s) OR
                    (c.visibility = 'private' AND c.created_by = %s)
                ORDER BY c.name
                """,
                (current_user['team_id'], current_user['user_id'])
            )
        collections = cur.fetchall()
    conn.close()
    return collections

@router_collections.delete("/{collection_id}", summary="Delete a collection")
def delete_collection(collection_id: int, current_user: dict = Depends(get_current_user)):
    """
    Deletes a collection.
    - Owners can delete their own collections.
    - Managers can delete collections created by their team members.
    - Admins can delete any collection.
    """
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.created_by, u.team_id AS owner_team_id
            FROM collections c
            JOIN users u ON c.created_by = u.id
            WHERE c.id = %s
            """,
            (collection_id,)
        )
        collection_info = cur.fetchone()

        if not collection_info:
            raise HTTPException(status_code=404, detail="Collection not found")

        is_owner = (collection_info["created_by"] == current_user["user_id"])
        is_admin = (current_user["role"] == "admin")
        is_manager_of_owner = (current_user["role"] == "manager" and collection_info["owner_team_id"] == current_user["team_id"])

        # Deletion policy:
        # - Admin can delete anything
        # - If creator is manager: same-team manager or admin can delete
        # - If creator is user: owner, same-team manager, or admin can delete
        # (If creator is admin: only admin can delete)
        if not (
            is_admin or
            (is_owner and current_user["role"] in ("user", "manager", "admin")) or
            (is_manager_of_owner and collection_info.get("created_by") is not None and current_user["role"] == "manager")
        ):
            raise HTTPException(status_code=403, detail="You do not have permission to delete this collection.")

        cur.execute("DELETE FROM collections WHERE id = %s", (collection_id,))
        conn.commit()
    conn.close()
    return {"message": "Collection and all its contents deleted successfully."}

@router_collections.post("/{collection_id}/documents", summary="Add documents to a collection")
def add_documents_to_collection(collection_id: int, request: DocumentsToModify, current_user: dict = Depends(get_current_user)):
    """
    Adds documents to any collection the user can see.
    """
    _ensure_collection_documents_schema()
    conn = get_db_connection()
    with conn.cursor() as cur:
        # Check if the user can view the collection. If so, they can add to it.
        cur.execute(
            """
            SELECT id FROM collections WHERE id = %s AND (
                visibility = 'public' OR
                (visibility = 'team' AND team_id = %s) OR
                (visibility = 'private' AND created_by = %s) OR
                %s = 'admin'
            )
            """,
            (collection_id, current_user['team_id'], current_user['user_id'], current_user['role'])
        )
        if not cur.fetchone():
            raise HTTPException(status_code=403, detail="You do not have permission to add documents to this collection.")

        # Add the documents with attribution
        values = [(collection_id, doc_id, current_user['user_id']) for doc_id in request.doc_ids]
        if values:
            args_str = ",".join(cur.mogrify("(%s,%s,%s)", v).decode('utf-8') for v in values)
            cur.execute(
                f"""
                INSERT INTO collection_documents (collection_id, doc_id, added_by)
                VALUES {args_str}
                ON CONFLICT (collection_id, doc_id) DO NOTHING
                """
            )
            conn.commit()
    conn.close()
    return {"message": "Documents added successfully."}

@router_collections.get("/{collection_id}/documents", summary="Get all document IDs in a collection (recursively)")
def get_collection_documents_recursively(collection_id: int):
    """
    Retrieves all document IDs within a specific collection and all its sub-collections.
    """
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            WITH RECURSIVE sub_collections AS (
                SELECT id FROM collections WHERE id = %s
                UNION
                SELECT c.id FROM collections c INNER JOIN sub_collections sc ON c.parent_id = sc.id
            )
            SELECT DISTINCT doc_id FROM collection_documents WHERE collection_id IN (SELECT id FROM sub_collections);
        """, (collection_id,))
        doc_ids = [row['doc_id'] for row in cur.fetchall()]
    conn.close()
    return {"doc_ids": doc_ids}


class CollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    visibility: Optional[str] = None  # enforce rules below


@router_collections.patch("/{collection_id}", summary="Update a collection")
def update_collection(collection_id: int, payload: CollectionUpdate, current_user: dict = Depends(get_current_user)):
    """
    Update name/description/parent/visibility.
    - Only manager/admin can set visibility to public.
    - Owner, same-team manager, or admin can update.
    """
    # Load collection owner and team
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.created_by, u.team_id AS owner_team_id, c.visibility
                FROM collections c
                JOIN users u ON c.created_by = u.id
                WHERE c.id = %s
                """,
                (collection_id,)
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Collection not found")

            is_owner = (row["created_by"] == current_user["user_id"])
            is_admin = (current_user["role"] == "admin")
            is_manager_same_team = (current_user["role"] == "manager" and row["owner_team_id"] == current_user["team_id"]) 

            if not (is_owner or is_manager_same_team or is_admin):
                raise HTTPException(status_code=403, detail="Not authorized to update this collection.")

            # Visibility guard
            if payload.visibility == "public" and current_user["role"] not in ("manager", "admin"):
                raise HTTPException(status_code=403, detail="Only managers or admins can set visibility to public.")

            fields = []
            values = []
            if payload.name is not None:
                fields.append("name = %s")
                values.append(payload.name)
            if payload.description is not None:
                fields.append("description = %s")
                values.append(payload.description)
            if payload.parent_id is not None:
                fields.append("parent_id = %s")
                values.append(payload.parent_id)
            if payload.visibility is not None:
                fields.append("visibility = %s")
                values.append(payload.visibility)

            if fields:
                values.append(collection_id)
                cur.execute(f"UPDATE collections SET {', '.join(fields)} WHERE id = %s", tuple(values))
                conn.commit()
    finally:
        conn.close()
    return {"message": "Collection updated."}


@router_collections.delete("/{collection_id}/documents", summary="Remove documents from a collection")
def remove_documents_from_collection(collection_id: int, request: DocumentsToModify, current_user: dict = Depends(get_current_user)):
    """
    Remove documents from a collection and delete them from database and vector store.
    - Allowed if current user added the doc, or is manager/admin.
    """
    _ensure_collection_documents_schema()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # First, get the documents that will be removed to check permissions
            if current_user["role"] in ("manager", "admin"):
                cur.execute(
                    "SELECT doc_id, added_by FROM collection_documents WHERE collection_id = %s AND doc_id = ANY(%s)",
                    (collection_id, request.doc_ids)
                )
            else:
                # Only get docs added by this user
                cur.execute(
                    "SELECT doc_id, added_by FROM collection_documents WHERE collection_id = %s AND doc_id = ANY(%s) AND added_by = %s",
                    (collection_id, request.doc_ids, current_user["user_id"])
                )
            
            documents_to_remove = cur.fetchall()
            
            if not documents_to_remove:
                raise HTTPException(status_code=404, detail="No documents found to remove")
            
            # Remove from collection_documents table
            if current_user["role"] in ("manager", "admin"):
                cur.execute(
                    "DELETE FROM collection_documents WHERE collection_id = %s AND doc_id = ANY(%s)",
                    (collection_id, request.doc_ids)
                )
            else:
                # Only remove docs added by this user
                cur.execute(
                    "DELETE FROM collection_documents WHERE collection_id = %s AND doc_id = ANY(%s) AND added_by = %s",
                    (collection_id, request.doc_ids, current_user["user_id"])
                )
            
            # Now delete the documents from database and vector store
            for doc in documents_to_remove:
                doc_id = doc["doc_id"]
                
                # Check if document exists in documents table
                cur.execute("SELECT user_id FROM documents WHERE doc_id = %s", (doc_id,))
                doc_info = cur.fetchone()
                
                if doc_info:
                    # Check permissions for deletion
                    user_role = current_user.get("role")
                    user_id = current_user.get("user_id")
                    user_team_id = current_user.get("team_id")
                    
                    is_owner = (doc_info["user_id"] == user_id)
                    is_admin = (user_role == "admin")
                    
                    # Get owner's team for manager check
                    cur.execute("SELECT team_id FROM users WHERE id = %s", (doc_info["user_id"],))
                    owner_team = cur.fetchone()
                    is_manager_of_owner = (user_role == "manager" and owner_team and owner_team["team_id"] == user_team_id)
                    
                    if is_owner or is_admin or is_manager_of_owner:
                        # Delete from vector store
                        try:
                            from models.models import vectorstore3
                            vectorstore3.delete([doc_id])
                        except Exception as e:
                            print(f"Warning: Failed to delete from vector store: {e}")
                        
                        # Delete from documents table
                        cur.execute("DELETE FROM documents WHERE doc_id = %s", (doc_id,))
                        
                        # Delete file from disk
                        try:
                            import os
                            import shutil
                            file_dir = os.path.join("data", str(doc_info["user_id"]), doc_id)
                            if os.path.exists(file_dir):
                                shutil.rmtree(file_dir)
                        except Exception as e:
                            print(f"Warning: Failed to delete file from disk: {e}")
            
            conn.commit()
    finally:
        conn.close()
    return {"message": "Documents removed from collection and deleted successfully."}