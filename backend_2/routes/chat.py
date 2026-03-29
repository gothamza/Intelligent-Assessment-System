### this file handles chat-related endpoints, including creating chats, listing chats, adding messages, and deleting chats.

from models.models import *
import shutil
router_chat= APIRouter(tags=["💬Chat Management APIs"])
# ======== Data Models ========
# Request model for creating a new chat
class ChatCreateRequest(BaseModel):
    chat_title: str
    chat_type: str = "llm"  # or "rag"

# Request model for updating chat title
class ChatUpdateRequest(BaseModel):
    chat_title: str

# ========= Endpoints =========

# ----------- Create Chat -----------
@router_chat.post("/chats/create")
async def create_chat(request: ChatCreateRequest, current_user: dict = Depends(get_current_user)):
    chat_id = str(uuid4())
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO chats (chat_id, user_id, chat_title, chat_type) VALUES (%s, %s, %s, %s)",
                (chat_id, str(current_user["user_id"]), request.chat_title, request.chat_type)
            )
        conn.commit()
    finally:
        conn.close()
    return {"chat_id": chat_id}


# ----------- List Chats -----------
@router_chat.get("/chats/list")
async def list_chats(
    chat_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if chat_type:
                cur.execute(
                    "SELECT chat_id, chat_title, created_at FROM chats WHERE user_id = %s AND chat_type = %s ORDER BY created_at DESC",
                    (str(current_user["user_id"]), chat_type)
                )
            else:
                cur.execute(
                    "SELECT chat_id, chat_title, created_at FROM chats WHERE user_id = %s ORDER BY created_at DESC",
                    (str(current_user["user_id"]),)
                )
            chats = cur.fetchall()
    finally:
        conn.close()
    return [{"chat_id": c["chat_id"], "chat_title": c["chat_title"], "created_at": c["created_at"]} for c in chats]


# ----------- Get Messages for a Chat -----------
@router_chat.get("/chats/{chat_id}/messages")
async def get_chat_messages(
    chat_id: str,
    limit: int = Query(40, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS count FROM chat_messages WHERE chat_id = %s",
                (chat_id,)
            )
            count_row = cur.fetchone()
            total = count_row["count"] if count_row and count_row["count"] is not None else 0
            cur.execute(
                "SELECT role, content, timestamp FROM chat_messages WHERE chat_id = %s ORDER BY timestamp DESC LIMIT %s OFFSET %s",
                (chat_id, limit, offset)
            )
            messages = cur.fetchall()
    finally:
        conn.close()
    messages = list(reversed(messages))
    return {
        "messages": [
            {"role": m["role"], "content": m["content"], "timestamp": m["timestamp"]}
            for m in messages
        ],
        "total": total
    }


# ----------- Add Message to Chat -----------
@router_chat.post("/chats/{chat_id}/add_message")
async def add_chat_message(request: ChatMessageRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO chat_messages (chat_id, role, content) VALUES (%s, %s, %s)",
                (request.chat_id, request.role, request.content)
            )
        conn.commit()
    finally:
        conn.close()
    return {"status": "ok"}


# ----------- Update Chat Title -----------
@router_chat.put("/chats/{chat_id}")
async def update_chat_title(
    chat_id: str,
    request: ChatUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update the title of a chat if the user is the owner.
    """
    user_id = str(current_user["user_id"])  # Convert to string to match database type
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check if the chat belongs to the user
            cur.execute(
                "SELECT user_id FROM chats WHERE chat_id = %s",
                (chat_id,)
            )
            chat_owner = cur.fetchone()
            
            if not chat_owner:
                raise HTTPException(status_code=404, detail="Chat not found")
            
            if chat_owner["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to edit this chat")
            
            # Update the chat title
            cur.execute(
                "UPDATE chats SET chat_title = %s WHERE chat_id = %s",
                (request.chat_title, chat_id)
            )
        conn.commit()
    finally:
        conn.close()
    
    return {"status": "ok", "chat_title": request.chat_title}


# ----------- Delete Chat -----------
@router_chat.delete("/chats/{chat_id}", status_code=204)
async def delete_chat(
    chat_id: str,
    current_user: dict = Depends(get_current_user),
    request: Request = None
):
    """
    Delete a chat and all its messages if the user is the owner or admin.
    """
    user_id = current_user["user_id"]
    user_role = current_user.get("role")

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check chat ownership
            cur.execute("SELECT user_id FROM chats WHERE chat_id = %s", (chat_id,))
            chat = cur.fetchone()
            if not chat:
                raise HTTPException(status_code=404, detail="Chat not found")
            # print("chat user_id:", chat["user_id"])
            # print("-------------------------------")
            # print("current user_id:", user_id)
            if chat["user_id"] == str(user_id):
                # Delete all messages for this chat

                cur.execute("DELETE FROM chat_messages WHERE chat_id = %s", (chat_id,))
                # Delete the chat itself
                cur.execute("DELETE FROM chats WHERE chat_id = %s", (chat_id,))
            else:
                raise HTTPException(status_code=403, detail="Not authorized to delete this chat")

            
        conn.commit()
    finally:
        conn.close()
    # --- Delete associated image folder ---
    image_dir = os.path.join("data/generated_images", chat_id)
    if os.path.isdir(image_dir):
        try:
            shutil.rmtree(image_dir)
        except Exception as e:
            print(f"Warning: Failed to delete image directory {image_dir}: {e}")
    
    # --- Clear LangGraph memory for this chat ---
    try:
        postgres_url = os.getenv("DATABASE_URL")
        with PostgresSaver.from_conn_string(postgres_url) as memory:
            cur = memory.conn.cursor()
            for table in ("checkpoints", "checkpoint_writes", "checkpoint_blobs"):
                cur.execute(f"DELETE FROM {table} WHERE thread_id = %s", (chat_id,))
            memory.conn.commit()

    except Exception as e:
        print(f"Warning: failed to clear LLM memory for chat {chat_id}: {e}")
    
    # try:
    #     # Clear vector store memory
    #     vectorstore3.delete(where={"chat_id": chat_id})
        
    #     # Clear Postgres checkpoints
    #     checkpointer.clear(thread_id=chat_id)
        
    #     return {"status": "Memory cleared"}
    # except Exception as e:
    #     raise HTTPException(500, f"Memory clearance failed: {str(e)}")

    return