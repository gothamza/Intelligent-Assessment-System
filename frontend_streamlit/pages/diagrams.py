import streamlit as st


def diagrams_page():
    st.title("📊 Architecture & Flux - Diagrammes")
    st.caption("Visualisation du schéma de données et du workflow pour réaliser des captures ou exports.")

    # --------------------------------------
    # Schéma BD conceptuel (Graphviz)
    # --------------------------------------
    st.subheader("Schéma BD (conceptuel)")
    db_graph = r"""
    digraph {
        rankdir=TB;
        bgcolor="white";
        node [shape=plain, fontname="Inter", fontsize=10, fontcolor="black"];
        edge [color="#2563eb", penwidth=1.5, fontname="Inter", fontsize=10, fontcolor="#1e40af"];

        users [label=<
            <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6" BGCOLOR="#dbeafe" BORDERCOLOR="#1e40af">
                <TR><TD COLSPAN="1" BGCOLOR="#3b82f6"><B><FONT COLOR="white">users</FONT></B></TD></TR>
                <TR><TD><FONT COLOR="black">id</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">login</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">password</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">team_id</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">role</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">is_active</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">created_at</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">updated_at</FONT></TD></TR>
            </TABLE>
        >];

        chats [label=<
            <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6" BGCOLOR="#d1fae5" BORDERCOLOR="#059669">
                <TR><TD BGCOLOR="#10b981"><B><FONT COLOR="white">chats</FONT></B></TD></TR>
                <TR><TD><FONT COLOR="black">chat_id</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">user_id</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">chat_title</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">chat_type</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">created_at</FONT></TD></TR>
            </TABLE>
        >];

        chat_messages [label=<
            <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6" BGCOLOR="#fef3c7" BORDERCOLOR="#d97706">
                <TR><TD BGCOLOR="#f59e0b"><B><FONT COLOR="white">chat_messages</FONT></B></TD></TR>
                <TR><TD><FONT COLOR="black">message_id</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">chat_id</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">role</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">content</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">timestamp</FONT></TD></TR>
            </TABLE>
        >];

        documents [label=<
            <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6" BGCOLOR="#fce7f3" BORDERCOLOR="#be185d">
                <TR><TD BGCOLOR="#ec4899"><B><FONT COLOR="white">documents</FONT></B></TD></TR>
                <TR><TD><FONT COLOR="black">doc_id</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">user_id</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">team_id</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">doc_title</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">file_type</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">visibility</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">upload_date</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">file_path</FONT></TD></TR>
            </TABLE>
        >];

        prompt_templates [label=<
            <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6" BGCOLOR="#fef3c7" BORDERCOLOR="#d97706">
                <TR><TD BGCOLOR="#f59e0b"><B><FONT COLOR="white">prompt_templates</FONT></B></TD></TR>
                <TR><TD><FONT COLOR="black">id</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">title</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">content</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">type</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">tags[]</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">visibility</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">team_id</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">created_by</FONT></TD></TR>
                <TR><TD><FONT COLOR="black">created_at</FONT></TD></TR>
            </TABLE>
        >];

        {rank=same; users; documents; prompt_templates}
        {rank=same; chats; chat_messages}

        users -> chats [label="1..n", color="#2563eb"];
        users -> documents [label="1..n", color="#2563eb"];
        users -> prompt_templates [label="1..n", color="#2563eb"];
        chats -> chat_messages [label="1..n", color="#2563eb"];
    }
    """
    st.graphviz_chart(db_graph)

    # --------------------------------------
    # Workflow global
    # --------------------------------------
    st.subheader("Workflow global (simplifié)")
    flow_graph = r"""
    digraph {
        rankdir=LR;
        bgcolor="white";
        node [shape=box, style="rounded,filled", fontname="Inter", fontsize=11, color="black", fontcolor="white"];
        edge [color="#2563eb", penwidth=2, fontname="Inter", fontsize=10, fontcolor="#1e40af"];

        user     [label="Utilisateur Streamlit", fillcolor="#3b82f6"];
        auth     [label="/auth/*", fillcolor="#10b981"];
        upload   [label="/docs/upload_for_chat", fillcolor="#f59e0b"];
        status   [label="/docs/status/{id}", fillcolor="#f59e0b"];
        list     [label="/docs/list", fillcolor="#10b981"];
        rag      [label="/rag_langgraph2", fillcolor="#3b82f6"];
        chroma   [label="ChromaDB", fillcolor="#6366f1"];
        groq     [label="Groq API (llama/qwen/gpt-oss)", fillcolor="#ec4899"];
        gen_exam [label="Generate Exam (frontend)", fillcolor="#8b5cf6"];
        take_exam[label="Take Exam (frontend)", fillcolor="#ef4444"];

        user -> auth;
        user -> upload -> status;
        upload -> chroma;
        user -> list;
        user -> rag -> chroma;
        rag -> groq;
        user -> gen_exam;
        user -> take_exam -> groq;
    }
    """
    st.graphviz_chart(flow_graph)

    st.info("Pour les rapports Overleaf : faites une capture d’écran de ces vues, ou exportez-les en SVG/PNG si Graphviz est disponible localement.")

