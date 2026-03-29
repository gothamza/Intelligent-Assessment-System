from fastapi import APIRouter, Depends, HTTPException, status
from models.models import PromptTemplate , get_db_connection
from auth.oauth2 import get_current_user

router_prompts = APIRouter(prefix="/prompts",tags=["Prompts Management APIs"])

@router_prompts.get("/")
def list_prompts(current_user: dict = Depends(get_current_user), conn = Depends(get_db_connection)):
    """
    List prompts based on visibility and user permissions.
    """
    user_id = current_user["user_id"]
    team_id = current_user.get("team_id")
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM prompt_templates
                WHERE visibility = 'public'
                OR (visibility = 'private' AND created_by = %s)
                OR (visibility = 'team' AND team_id = %s)
            """, (user_id, team_id))
            prompts = cur.fetchall()
    finally:
        conn.close()
    return prompts

@router_prompts.post("/")
def create_prompt(prompt: PromptTemplate, current_user: dict = Depends(get_current_user), conn = Depends(get_db_connection)):
    """
    Create a new prompt.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO prompt_templates (title, content, type, tags, visibility, team_id, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                prompt.title,
                prompt.content,
                prompt.type,
                prompt.tags,
        
                prompt.visibility,
                current_user.get("team_id") if prompt.visibility == "team" else None,
                current_user["user_id"]
            ))
        conn.commit()
    finally:
        conn.close()
    return {"message": "Prompt created successfully"}

@router_prompts.get("/{id}")
def get_prompt(id: int, current_user: dict = Depends(get_current_user), conn = Depends(get_db_connection)):
    """
    Retrieve a specific prompt by ID.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM prompt_templates
                WHERE id = %s
                AND (visibility = 'public'
                     OR (visibility = 'private' AND created_by = %s)
                     OR (visibility = 'team' AND team_id = %s))
            """, (id, current_user["user_id"], current_user.get("team_id")))
            prompt = cur.fetchone()
    finally:
        conn.close()

    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found or you don't have access")
    return prompt

@router_prompts.put("/{id}")
def update_prompt(id: int, prompt: PromptTemplate, current_user: dict = Depends(get_current_user), conn = Depends(get_db_connection)):
    """
    Update a prompt if the current user is the creator.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE prompt_templates
                SET title = %s, content = %s, type = %s, tags = %s, visibility = %s
                WHERE id = %s AND created_by = %s
            """, (
                prompt.title,
                prompt.content,
                prompt.type,
                prompt.tags,

                prompt.visibility,
                id,
                current_user["user_id"]
            ))
            if cur.rowcount == 0:
                 raise HTTPException(status_code=404, detail="Prompt not found or you are not the owner")
        conn.commit()
    finally:
        conn.close()
    return {"message": "Prompt updated successfully"}

@router_prompts.delete("/{id}")
def delete_prompt(id: int, current_user: dict = Depends(get_current_user), conn = Depends(get_db_connection)):
    """
    Delete a prompt if the current user is the creator.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM prompt_templates
                WHERE id = %s AND created_by = %s
            """, (id, current_user["user_id"]))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Prompt not found or you are not the owner")
        conn.commit()
    finally:
        conn.close()
    return {"message": "Prompt deleted successfully"}