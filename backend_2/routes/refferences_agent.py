
@app.post("/Ragwiki/")
async def process_text(request: PromptRequest , db: Session = Depends(get_db)):
    try:
        

        # Initialize the LLM
        current_user = await get_current_user(token=request.Token, db=db)
        await get_current_active_user(current_user=current_user)

        if request.lang == "fr":
            page =  wiki_fr.run(request.prompt)

            # Create prompt template
            prompt = ChatPromptTemplate.from_template(
                """
                Génère un bloc de texte pour une diapositive basé sur le texte fourni.
                Assure-toi que le texte ne soit pas trop long. Ne fournir que le texte sans titres ni détails supplémentaires :
                <texte>
                {context}
                </texte>
                """
            )
        else:
            page =  wiki.run(request.prompt)

            # Create prompt template
            prompt = ChatPromptTemplate.from_template(
                """
                Generate a block of text for a slide based on the provided content.
                Make sure the text is not too long,Only provide the block of text without titles or additional details.
                <text>
                {context}
                </text>
                """
            )
        # Fetch Wikipedia content

        # Load and split documents
        content = page
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        final_documents = text_splitter.split_text(content)
        vectors = FAISS.from_texts(final_documents, embeddings2)


        # Create document chain
        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = vectors.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        # Process the input prompt
        start = time.process_time()
        response = retrieval_chain.invoke({"input": request.prompt})
        response_time = time.process_time() - start

        # Clean up used data
        del content
        del text_splitter
        del final_documents
        del vectors

        # Return the response
        return {
            "response": response['answer'],
            "response_time": response_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/Rag-http/")
async def Rag_http(request: RequestDataHTTP ,db: Session = Depends(get_db)):
    try:
        # Validate the token
        current_user = await get_current_user(token=request.Token, db=db)
        await get_current_active_user(current_user=current_user)
        # Load and split documents
        loader = WebBaseLoader(request.link)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        final_documents = text_splitter.split_documents(docs[:50])
        vectors = FAISS.from_documents(final_documents, embeddings2)

        # Initialize the LLM

        # Create prompt template
        prompt = ChatPromptTemplate.from_template(
            """
            Answer the questions based on the provided context only.
            Please provide the most accurate response based on the question
            <context>
            {context}
            <context>
            Questions: {input}
            """
        )

        # Create document chain
        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = vectors.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        # Process the input prompt
        start = time.process_time()
        response = retrieval_chain.invoke({"input": request.text})
        response_time = time.process_time() - start

        # Clean up used data
        del loader
        del docs
        del text_splitter
        del final_documents
        del vectors

        # Return the response
        return {
            "response": response['answer'],
            "response_time": response_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    