# Tutor Page Refactoring Guide

## Current Status
The file `pages/7_💬_Tuteur_Interactif.py` has become corrupted during refactoring. It contains duplicate functions and broken code.

## Required Changes

### 1. Remove Old Functions (Lines 45-679)
- Remove all `create_math_tools()` code
- Remove `create_agent()` function  
- Remove `run_agent()` function
- Keep only the correct helper functions starting at line 681

### 2. Replace Imports
```python
# OLD:
from src.enhanced_chains import create_enhanced_llm_manager

# NEW:
from services.api_client import APIClient
```

### 3. Initialize API Client Instead of Agent
```python
# OLD:
if 'agent' not in st.session_state:
    st.session_state.agent = None

# NEW:
if 'api_client' not in st.session_state:
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    st.session_state.api_client = APIClient(base_url=api_base_url)
```

### 4. Replace Agent Initialization in Sidebar
```python
# OLD:
if st.session_state.agent is None:
    with st.spinner("Initialisation de l'agent..."):
        agent, error = create_agent()
        if error:
            st.error(f"❌ {error}")
        else:
            st.session_state.agent = agent
            st.success("✅ Agent prêt")
else:
    st.success("✅ Agent actif")

# NEW:
try:
    health = st.session_state.api_client.health_check()
    st.success("✅ Backend connecté")
except Exception as e:
    st.error(f"❌ Erreur de connexion: {str(e)}")
```

### 5. Replace run_agent() Calls with API Client Calls

#### For Chat Input:
```python
# OLD:
response, reasoning = run_agent(
    st.session_state.agent,
    prompt,
    {"topic": topic, "niveau": niveau, "difficulty": difficulty, "custom_instructions": custom_instructions}
)

# NEW:
result = st.session_state.api_client.chat(
    message=prompt,
    context={"topic": topic, "niveau": niveau, "difficulty": difficulty, "custom_instructions": custom_instructions},
    chat_history=st.session_state.chat_history[-5:],  # Last 5 messages
    use_rag=True
)
response = result["response"]
reasoning = result.get("reasoning")
```

#### For Generate Question Button:
```python
# OLD:
response, reasoning = run_agent(
    st.session_state.agent,
    prompt,
    {"topic": topic, "niveau": niveau, "difficulty": difficulty, "custom_instructions": custom_instructions}
)

# NEW:
question = st.session_state.api_client.generate_question(
    context={"topic": topic, "niveau": niveau, "difficulty": difficulty, "custom_instructions": custom_instructions}
)
response = f"📝 **Question ({topic} - {niveau}):**\n\n{question}"
reasoning = None
```

#### For Generate Hint Button:
```python
# OLD:
response, reasoning = run_agent(
    st.session_state.agent,
    prompt,
    {"topic": topic, "niveau": niveau, "custom_instructions": custom_instructions}
)

# NEW:
hint = st.session_state.api_client.generate_hint(
    question=last_question,
    context={"topic": topic, "niveau": niveau, "custom_instructions": custom_instructions}
)
response = f"💡 **Indice:**\n\n{hint}"
reasoning = None
```

#### For Generate Exercise Button:
```python
# OLD:
response, reasoning = run_agent(
    st.session_state.agent,
    prompt,
    {"topic": topic, "niveau": niveau}
)

# NEW:
exercise = st.session_state.api_client.generate_exercise(
    context={"topic": topic, "niveau": niveau}
)
response = f"📚 **Exercice:**\n\n{exercise}"
reasoning = None
```

#### For Generate Course Button:
```python
# OLD:
response, reasoning = run_agent(
    st.session_state.agent,
    prompt,
    {"topic": topic, "niveau": niveau}
)

# NEW:
course = st.session_state.api_client.generate_course(
    context={"topic": topic, "niveau": niveau}
)
response = f"📖 **Cours Complet:**\n\n{course}"
reasoning = None
```

### 6. Update Statistics
```python
# OLD:
if "correcte" in response.lower():
    st.session_state.stats["correct"] += 1
    st.session_state.stats["total_questions"] += 1
elif "partielle" in response.lower():
    st.session_state.stats["partial"] += 1
    st.session_state.stats["total_questions"] += 1
elif "incorrecte" in response.lower():
    st.session_state.stats["incorrect"] += 1
    st.session_state.stats["total_questions"] += 1

# NEW:
# Statistics are now managed by the backend
# Optionally sync with backend:
try:
    stats = st.session_state.api_client.get_stats()
    st.session_state.stats = stats
except:
    pass
```

## Next Steps
1. Restore the file from version control OR
2. Manually fix the corrupted sections using this guide OR  
3. Create a new clean version of the file

