# **Citrature:** **Core Logic Implementation Blueprint**

This document provides a definitive, expert-level implementation blueprint to construct the core application logic for the Citrature platform. The plan is structured as a sequence of 20 distinct engineering steps, designed for rapid, iterative development while ensuring architectural robustness and scalability. The focus is exclusively on the implementation of the core services and features, transitioning the concept into a functional product.

## **1\. Microservice and Environment Configuration**

This foundational step establishes the complete project structure, container orchestration, and a robust, centralized configuration management system. This ensures all services can communicate and access necessary credentials and parameters securely and consistently.

### **Implementation Details**

* **Project Structure:** Create the root project directory containing subdirectories for each microservice: frontend/, api/, worker/. The db/, rabbitmq/, redis/, and grobid/ services will be defined directly within the docker-compose.yml file.  
* **Service Initialization:** Initialize the api service as a FastAPI application, the worker service as a Celery application, and the frontend service as a standard React project.  
* **Centralized Configuration:** Implement a configuration module within the api and worker services. This module must load all environment variables at application startup, validate their presence, and store them as immutable settings objects. This approach establishes a definitive contract that governs the entire distributed system, preventing a wide class of runtime errors by ensuring environmental consistency from a single source of truth.  
* **Docker Compose Orchestration:** Define the docker-compose.yml file at the project root to orchestrate all seven services. This file must configure a primary shared Docker network for inter-service communication and define persistent volumes for PostgreSQL data (pgdata) and the BM25 index directory (bm25\_indices) to ensure data integrity across container restarts.  
* **Startup Ordering:** Utilize depends\_on within docker-compose.yml to enforce a strict startup order. Foundational services (db, rabbitmq, redis, grobid) must be healthy before the application services (api, worker) are started.

### **Centralized Environment Configuration**

| Variable Name | Description | Consumed By | Example Value (Non-Sensitive) |
| :---- | :---- | :---- | :---- |
| API\_ORIGIN | The public-facing URL of the API service. | api | http://localhost:8000 |
| WEB\_ORIGIN | The public-facing URL of the React frontend. | api | http://localhost:3000 |
| POSTGRES\_DSN | Database connection string for PostgreSQL. | api, worker | postgresql://user:pass@db:5432/citrature |
| PGVECTOR\_DIMENSION | The dimensionality of the vectors stored in pgvector. | api, worker | 768 |
| RABBITMQ\_URL | Connection URL for the RabbitMQ message broker. | api, worker | amqp://user:pass@rabbitmq:5672/ |
| REDIS\_URL | Connection URL for the Redis result backend. | worker | redis://redis:6379/0 |
| OPENROUTER\_BASE\_URL | Base URL for the OpenRouter API. | worker | https://openrouter.ai/api/v1 |
| OPENROUTER\_API\_KEY | API key for authenticating with OpenRouter. | worker | sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxx |
| CROSSREF\_BASE\_URL | Base URL for the Crossref API. | worker | https://api.crossref.org |
| CROSSREF\_MAILTO | Email address for the Crossref "polite" API pool. | worker | hello@citrature.com |
| GOOGLE\_CLIENT\_ID | Google OAuth 2.0 Client ID. | api | xxxxxxxx.apps.googleusercontent.com |
| GOOGLE\_CLIENT\_SECRET | Google OAuth 2.0 Client Secret. | api | GOCSPX-xxxxxxxxxxxxxxxx |
| GOOGLE\_REDIRECT\_URI | The callback URI registered with Google for OAuth. | api | http://localhost:8000/auth/google/callback |
| GROBID\_BASE\_URL | The URL for the self-hosted GROBID service. | worker | http://grobid:8070 |
| GCS\_BUCKET\_NAME | The name of the Google Cloud Storage bucket. | api, worker | citrature-uploads |
| GCS\_PROJECT\_ID | The Google Cloud project ID. | api, worker | citrature-prod |
| GCS\_CREDENTIALS\_JSON | The JSON content of the GCS service account key. | api, worker | {"type": "service\_account",...} |
| MAX\_TOPIC\_PAPERS | Cap on the number of papers to fetch for a topic ingestion. | api, worker | 30 |
| MAX\_GRAPH\_DEPTH | Cap on the traversal depth for citation graph building. | api, worker | 3 |
| MAX\_COLLECTIONS\_PER\_USER | Cap on the number of collections a free-tier user can create. | api | 1 |
| MONTHLY\_CHAT\_QUOTA | Cap on the number of chat messages per user per month. | api | 100 |

### **Testing Method**

Execute docker-compose up \--build. All seven services must start without crashing. Verify service-to-service connectivity by executing docker-compose exec api ping db and confirming a successful response; repeat for rabbitmq, redis, and grobid. The logs for the api and worker services must explicitly confirm that all required environment variables were loaded successfully at startup.

## **2\. Database Schema and Migration Foundation**

This step translates the application's data model into a concrete PostgreSQL schema using an ORM and establishes Alembic for migration management. This creates the persistent, integrity-enforced backbone for the entire application.

### **Implementation Details**

* **ORM and Migration Tooling:** Integrate SQLAlchemy as the ORM and Alembic for migration management within the api service codebase.  
* **Vector Extension:** Create an initial Alembic migration that executes the CREATE EXTENSION IF NOT EXISTS vector; SQL command to enable pgvector in the database.  
* **Model Definition:** Define the SQLAlchemy ORM models for all tables as specified in the schema overview below. All primary keys must be UUIDs, and all timestamp fields must be timezone-aware (UTC).  
* **Integrity Constraints:** Implement all specified relationships, indexes, and constraints. Critically, ON DELETE CASCADE must be enforced for all child entities of collections and papers. This offloads complex cleanup logic to the database, guaranteeing that the system cannot enter an inconsistent state with orphaned records following a deletion.  
* **Data Normalization:** Implement a normalization rule at the application level for all DOI values before persistence: convert to lowercase, strip https://doi.org/ prefixes, and trim whitespace.

### **Core Database Schema Overview**

| Table Name | Core Purpose | Primary Key(s) | Key Foreign Keys / Relationships |
| :---- | :---- | :---- | :---- |
| users | Stores authenticated user profiles. | id (UUID) | \- |
| collections | A user's workspace for a set of papers. | id (UUID) | user\_id \-\> users.id |
| papers | Core metadata for a single scholarly document. | id (UUID) | collection\_id \-\> collections.id |
| authors | Stores information about a single author. | id (UUID) | \- |
| paper\_authors | Many-to-many join table linking papers and authors. | paper\_id, author\_id | paper\_id \-\> papers.id, author\_id \-\> authors.id |
| citations | Represents a directed citation edge from one paper to another. | src\_paper\_id, dst\_doi | src\_paper\_id \-\> papers.id, resolved\_paper\_id \-\> papers.id (nullable) |
| chunks | A segment of text from a paper, used for retrieval. | id (UUID) | paper\_id \-\> papers.id |
| chunk\_embeddings | Stores the vector embedding for a text chunk. | chunk\_id | chunk\_id \-\> chunks.id |
| paper\_summaries | Stores AI-generated summaries for a paper's key sections. | paper\_id | paper\_id \-\> papers.id |
| gap\_insights | Stores AI-generated research gap insights for a collection. | id (UUID) | collection\_id \-\> collections.id |

### **Testing Method**

From within the api service container, run the alembic upgrade head command. The command must complete successfully. Connect to the db container using a psql client and use \\dt and \\d \<table\> commands to verify that all tables, columns, indexes, and foreign key constraints have been created as specified in the ORM models.

## **3\. Asynchronous Task Orchestration Setup**

This step configures the core components for background job processing: Celery, RabbitMQ, and Redis. This architecture is essential for handling long-running, resource-intensive operations like document ingestion and analysis without blocking the API, thereby ensuring a responsive user experience.

### **Implementation Details**

* **Celery Application:** Configure the Celery application instance in the worker service. It must be configured to use RabbitMQ as the message broker and Redis as the result backend.  
* **Serialization and Queues:** Define a single default queue for all tasks and enforce the use of the JSON serializer for task messages to ensure interoperability and debuggability.  
* **Task Definitions:** Create placeholder functions decorated with @celery.task for the primary jobs: ingest\_pdf\_task, ingest\_topic\_task, build\_graph\_task, and gap\_analysis\_task.  
* **API Client:** Implement a shared Celery client module accessible to the api service. This module will provide a simple interface for API endpoints to enqueue tasks to the RabbitMQ broker.  
* **Task Policies:** Establish default task policies to enhance robustness. This includes bounded retries with exponential backoff for tasks that interact with external networks (e.g., GROBID, Crossref, OpenRouter) to handle transient failures gracefully. Set soft time limits to prevent runaway processes: long for PDF ingestion and graph building, medium for topic ingestion and gap analysis.  
* **Result Persistence:** The system will treat Redis results as transient state for monitoring task completion. All durable outcomes (e.g., new papers, chunks, embeddings) must be persisted directly to the PostgreSQL database by the worker tasks themselves.

### **Testing Method**

Implement a simple add(x, y) test task in the worker service. Create a temporary test endpoint in the api service that enqueues this task with sample arguments. Call the endpoint and verify that a message appears in the RabbitMQ management UI (accessible via browser). The worker log must show that it received and executed the task. Finally, use the returned task ID to query the result from Redis, confirming that the result backend is correctly configured.

## **4\. Centralized Object Storage Integration (GCS)**

This step implements a dedicated service layer for interacting with Google Cloud Storage (GCS). This is critical for separating large, unstructured binary data (PDFs) from structured metadata (in Postgres), a pattern that enhances scalability and performance.

### **Implementation Details**

* **GCS Client Module:** Develop a GCS client module, configurable via the GCS\_CREDENTIALS\_JSON environment variable. This module should be shared or accessible by both the api and worker services.  
* **Server-Side Upload Logic:** Implement the file upload logic within an api service endpoint. This function will receive a multipart file, validate its size and MIME type against configured limits, and stream it directly to the configured GCS bucket. This avoids loading large files into memory on the API server.  
* **Object Key Schema:** All uploaded and derived objects must follow a strict naming convention to ensure organization and prevent collisions.  
  * Original uploads: collections/{collection\_id}/uploads/{uuid}.pdf  
  * Derived artifacts: collections/{collection\_id}/derived/{paper\_id}/tei.xml.  
* **Secure Download URLs:** Implement a function to generate short-lived (e.g., 5-minute expiry) V4 signed URLs. This provides a secure mechanism for an authenticated user to access a private GCS object directly from their browser without proxying the download through the API server.

### **Testing Method**

Create a test API endpoint that accepts a multipart/form-data file upload. Call this endpoint with a sample PDF file. Verify using the Google Cloud Console or gsutil that the file appears in the GCS bucket at the correct, structured path. Create a second test endpoint that takes an object key and returns a signed URL. Accessing this URL in a browser must successfully download or display the PDF file.

## **5\. User Authentication and Session Management**

This step implements the complete user authentication flow using Google SSO. By delegating identity verification, the application reduces its security surface area and provides a frictionless onboarding experience. The use of signed, stateless session cookies is crucial for horizontal scalability.

### **Implementation Details**

* **OAuth Configuration:** Configure the Google OAuth 2.0 credentials (GOOGLE\_CLIENT\_ID, GOOGLE\_CLIENT\_SECRET, GOOGLE\_REDIRECT\_URI) in the api service's environment settings.  
* **Login Endpoint:** Create an /auth/google/login endpoint that redirects the user to the Google consent screen, requesting the openid, email, and profile scopes.  
* **Callback Endpoint:** Implement the /auth/google/callback endpoint to handle the response from Google. This endpoint must:  
  1. Exchange the received authorization code for an ID token.  
  2. Validate the ID token's signature and claims.  
  3. Extract the user's profile information: email, name, and picture URL.  
* **User Persistence:** Implement "upsert" logic. Upon successful authentication, query the users table by email. If a user exists, update their name and picture URL. If not, create a new user record with the default plan set to free.  
* **Session Management:** After the user is identified or created, generate a signed, HttpOnly, Secure session cookie containing the user's unique ID. This stateless token allows the API to authenticate subsequent requests without a server-side session store.  
* **Route Protection:** Implement a FastAPI dependency (middleware) that inspects incoming requests for the session cookie, validates its signature, and attaches the authenticated user's ID to the request context. Apply this dependency to all non-public endpoints to enforce authentication.

### **Testing Method**

Manually navigate to the /auth/google/login endpoint in a browser. This must redirect to the Google login page. After authenticating with a valid Google account, it should redirect back to the /auth/google/callback endpoint. The callback must complete without error, and a session cookie should be present in the browser's developer tools. A subsequent request to a protected test endpoint (e.g., /api/v1/me) must succeed and return the correct user's information from the database.

## **6\. PDF Ingestion Pipeline**

This step implements the asynchronous pipeline that processes an uploaded PDF, extracting its structure, metadata, and references using the GROBID service.

### **Implementation Details**

* **Task Entry Point:** The ingest\_pdf\_task(collection\_id, object\_key) Celery task is the entry point. It will first fetch the specified PDF object from GCS using the GCS client module.  
* **GROBID Parsing:** The PDF bytes are submitted to the GROBID service's /api/processFulltextDocument endpoint. The task should request header and citation consolidation. On success, the resulting TEI XML is stored back to GCS under the derived artifacts path (collections/{collection\_id}/derived/{paper\_id}/tei.xml) for archival and debugging purposes.  
* **Parsing Fallback:** If the GROBID service fails (e.g., timeout, error response), the pipeline must implement a fallback mechanism using a library like PyMuPDF to perform basic text extraction. This fallback should apply heuristics to identify the abstract, introduction, and conclusion sections, ensuring the process does not fail completely.  
* **TEI XML Extraction:** A dedicated parser will process the in-memory TEI XML string to extract:  
  * Core metadata: title, DOI (if present), year, venue.  
  * Authors: name, affiliation, and email (where available).  
  * Sections: abstract and all body text sections, labeled with canonical names (e.g., 'introduction', 'conclusion').  
  * References: a structured list of cited works, each containing DOI, title, year, and authors if available.  
* **Database Persistence:** The extracted data is persisted to the database in a single transaction:  
  1. **Upsert Paper:** Create or update a papers record using the deduplication logic (Step 8). Set source='upload' and added\_via='upload'.  
  2. **Upsert Authors:** Create or update authors records and link them to the paper via the paper\_authors table, preserving author order.  
  3. **Insert Citations:** For each extracted reference, insert a row into the citations table with the src\_paper\_id and the destination DOI, title, and year.  
  4. **Create Chunks:** The extracted section texts are passed to the chunking logic (Step 9\) to be divided and stored.

### **Testing Method**

Upload a sample scientific PDF via the API endpoint developed for GCS integration, which should enqueue the ingest\_pdf\_task. Monitor the worker logs to confirm the task completes successfully. Inspect the database to verify that a papers record has been created with the correct metadata, along with associated authors, citations, and chunks records. Verify that the derived TEI XML file exists in the correct GCS path.

## **7\. Topic Ingestion Pipeline**

This pipeline enables users to build a collection by providing a topic query. It uses the Crossref API to find relevant papers, deduplicates them, and persists them to the database.

### **Implementation Details**

* **Task Entry Point:** The ingest\_topic\_task(collection\_id, query, limit) Celery task is triggered by an API endpoint. The limit will have already been capped at MAX\_TOPIC\_PAPERS by the API.  
* **Crossref Search:** The task will call the Crossref works API with the user's query. A mailto parameter must be included in the request to comply with Crossref's "polite" API usage policy.  
* **Data Mapping:** For each result returned by Crossref, extract the following fields: DOI, title, abstract, year, venue (e.g., container-title), URLs, and author information (names, affiliations).  
* **Deduplication and Persistence:** Iterate through the mapped results and persist them:  
  1. **Apply Deduplication Rules (Step 8):** For each paper, use the defined upsert logic to either create a new papers record or enrich an existing one. This is critical to avoid creating duplicate entries if a paper is added via both topic search and direct upload.  
  2. **Set Metadata:** For new papers, set source='crossref', added\_via='topic', and store the complete, raw JSON response from Crossref in the raw\_json field for future re-processing.  
  3. **Abstract Chunking and Embedding:** If a paper's abstract is present, immediately create a single corresponding record in the chunks table with section='abstract' and ord=0. This abstract chunk must then be sent immediately to the embedding pipeline (Step 9\) to generate and store its vector. This ensures that topic-ingested papers are immediately available for semantic search and analysis.

### **Testing Method**

Invoke the topic ingestion API endpoint with a common research query (e.g., "transformer models for protein folding"). Monitor the worker logs to confirm the ingest\_topic\_task runs and interacts with the Crossref API. After completion, query the database for papers in the specified collection. The count should be less than or equal to MAX\_TOPIC\_PAPERS. Verify that the new papers records have source='crossref' and that for each paper with an abstract, a corresponding chunks record and a chunk\_embeddings record exist.

## **8\. Paper and Author Deduplication Logic**

This step defines the precise business rules for upserting paper and author data. This is not a standalone service but a core set of rules to be implemented within the ingestion pipelines (Steps 6 and 7\) to maintain data integrity and prevent redundancy.

### **Implementation Details**

* **DOI Normalization:** Before any comparison or storage, all DOI strings must be normalized: convert to lowercase, strip any doi: or https://doi.org/ prefixes, and trim all leading/trailing whitespace.  
* **Paper Merge Strategy:** When adding a new paper, the following sequence must be executed to determine if it's a duplicate within the *same collection*:  
  1. **Match by DOI:** If the incoming paper has a normalized DOI, query for an existing paper in the collection with the same DOI.  
  2. **Match by Title/Year:** If no DOI is present or no match is found, query for an existing paper in the collection with a normalized matching title and the same publication year.  
  3. **Decision Logic:**  
     * If a match is found by either method, do not create a new papers record. Instead, enrich the existing record by filling in any missing fields (e.g., adding an abstract to a paper that was previously just a citation stub).  
     * If no match is found, create a new papers record.  
* **Author Merge Strategy:** A similar strategy applies to authors to avoid creating multiple records for the same person:  
  1. **Normalize Name:** Normalize author names (e.g., lowercase, remove punctuation) for comparison.  
  2. **Match by Name and Affiliation:** Attempt to find an existing authors record with an exact match on the normalized name and affiliation.  
  3. **Decision Logic:**  
     * If a match is found, use the existing author's ID.  
     * If no match is found, create a new authors record.  
  4. **Linkage:** In either case, create a new entry in the paper\_authors join table to link the paper to the correct author record.

### **Testing Method**

This logic is tested implicitly via the ingestion pipeline tests.

1. Run the topic ingestion task for "attention is all you need". Note the created paper ID.  
2. Manually create a citation record in the database pointing to the same paper's DOI but with a slightly different title.  
3. Run the PDF ingestion for the same paper. Verify that no new papers record is created. Instead, the existing record should be updated with the metadata from the PDF.  
4. Verify that the authors table contains only one entry for each unique author of the paper.

## **9\. Section-Aware Text Chunking and Embedding**

This composite pipeline is responsible for breaking down document text into manageable, semantically coherent chunks and then converting those chunks into numerical vectors (embeddings) for machine learning applications.

### **Implementation Details**

* **Chunking Strategy:**  
  * **Policy:** Implement a chunking function that operates on the text of each section of a paper (excluding the 'references' section). The function should aim for chunks of approximately 800-1200 tokens with a \~15% token overlap between consecutive chunks within the same section. This overlap helps preserve context at chunk boundaries.  
  * **Metadata:** When creating chunks records in the database, persist the source section label and the sequential ord (order) of the chunk within that section. This is crucial for reconstructing context and providing accurate citations.  
  * **Idempotency:** To prevent re-processing, compute and store a stable content hash (e.g., SHA256) of each section's text within the papers table or a related metadata table. The chunking process for a paper should only run if this hash changes.  
* **Embedding Pipeline:**  
  * **Batching:** The embedding logic, triggered after chunking, must batch the text from multiple chunks records into a single API call to the OpenRouter embedding endpoint. This is far more efficient than sending one request per chunk. The implementation must maintain a mapping between the input texts and their chunk\_ids.  
  * **API Call:** The request to OpenRouter must specify the embedding model configured in the environment variables. The dimensionality of this model must match the PGVECTOR\_DIMENSION setting.  
  * **Persistence:** Upon receiving the embedding vectors, upsert them into the chunk\_embeddings table, aligning each vector with its corresponding chunk\_id. The upsert should be idempotent, skipping chunks that already have an embedding and whose source text has not changed.  
  * **Error Handling:** Implement robust error handling for the API call. If the batch request partially fails, the logic should persist the successfully generated vectors and log the chunk\_ids of the failed ones for a potential retry mechanism.

### **Testing Method**

After a PDF has been successfully ingested (Step 6), query the chunks table for the corresponding paper\_id. Verify that multiple chunks exist, that they have correct section and ord values, and that the 'references' section was not chunked. Subsequently, query the chunk\_embeddings table. Verify that a vector exists for each created chunk and that its dimension matches PGVECTOR\_DIMENSION.

## **10\. Hybrid Search Foundation**

This step establishes the dual-retrieval system that powers the grounded Q\&A feature. It combines traditional keyword-based search (BM25) with modern semantic search (vectors) to achieve high recall and relevance.

### **Implementation Details**

* **BM25 Index (Lexical Search):**  
  * **Technology:** Use the Whoosh library to implement the BM25 index.  
  * **Layout:** Create one Whoosh index per collection, persisted in the shared volume mounted at /app/bm25\_indices. This volume must be accessible by both the api and worker services.  
  * **Schema:** The index schema for each document (a chunk) must contain the following fields: text (the main content, analyzed for search), chunk\_id (for linking back to the database), paper\_id, section, and ord.  
  * **Indexing Operation:** The logic to add/update documents in the BM25 index must be triggered whenever chunks are created or updated during the ingestion pipelines.  
* **Vector Search (Semantic Search):**  
  * Vector search capabilities are provided by the pgvector extension in PostgreSQL. The primary task is to write the SQL queries that perform Approximate Nearest Neighbor (ANN) search.  
  * The query will take a query vector as input and use the cosine distance operator (\<=\>) to find the chunk\_embeddings with the smallest distance to the query vector.  
* **Hybrid Retrieval Fusion:**  
  * This logic will reside in the api service.  
  * **Candidate Generation:** When a search query is received, the service will execute two parallel searches: one against the collection's BM25 index and one against the chunk\_embeddings table in Postgres.  
  * **Score Fusion:** The results from both searches (a list of chunk\_ids with scores) must be fused. Implement Reciprocal Rank Fusion (RRF) to combine the two ranked lists into a single, more robust ranking. Deduplicate the final list of chunk\_ids.

### **Testing Method**

1. Ingest several related papers into a collection. Verify that the corresponding BM25 index directory is created and populated.  
2. Create a search API endpoint that takes a text query.  
3. Execute a search with a specific keyword known to be in only one paper (e.g., an author's name from the middle of a paragraph). Verify that the BM25 component returns the correct chunk.  
4. Execute a search with a conceptual query that does not use exact keywords from the text (e.g., "methods for improving model attention" when the text uses "techniques for enhancing transformer focus"). Verify that the vector search component returns relevant chunks.  
5. The hybrid endpoint should return a fused and deduplicated list of chunk IDs from both queries.

## **11\. Citation Graph Construction Logic**

This step implements the core logic for building and expanding the citation graph. The process traverses references from a set of seed papers using either Breadth-First Search (BFS) or Depth-First Search (DFS), up to a configurable depth.

### **Implementation Details**

* **Task Entry Point:** The build\_graph\_task(collection\_id, mode, depth, seed\_paper\_ids) Celery task orchestrates the graph build process. The mode will be 'bfs' or 'dfs', and the depth will have been capped at MAX\_GRAPH\_DEPTH by the API.  
* **Frontier Management:** The traversal algorithm must maintain a visited set of normalized DOIs and resolved paper\_ids to avoid cycles and redundant processing. The traversal proceeds level by level (for BFS) or path by path (for DFS), decrementing the remaining depth at each step until it reaches zero.  
* **Reference Resolution:** For each unresolved citation encountered during traversal:  
  1. **Check by DOI:** If the citation has a normalized DOI, check if a paper with this DOI already exists in the database (across any collection). If not, call the Crossref API (works/{doi}) to fetch its metadata.  
  2. **Check by Title/Year:** If the citation has no DOI, attempt a Crossref search using its title and year. Use a confidence threshold to accept a match.  
  3. **Persistence:** If a match is found via Crossref, create a new minimal papers record in the current collection with source='crossref' and added\_via='graph'. This new paper becomes a node in the graph.  
  4. **Edge Creation:** Update the original citations record to link to the newly found or created paper by setting its resolved\_paper\_id.  
* **Post-Traversal Enrichment:** After the traversal completes, for any new papers that were added from Crossref and have an abstract, enqueue a follow-up task to chunk and embed their abstracts. This ensures new graph nodes are immediately searchable.  
* **Graph Export:** The API will provide an endpoint that queries the papers and citations tables for a given collection to generate a JSON representation of the graph (nodes and edges) for the frontend visualization.

### **Testing Method**

1. Ingest a single, highly-cited "seed" paper.  
2. Trigger the build\_graph\_task with mode='bfs' and depth=1.  
3. After the task completes, query the papers table. There should now be new papers corresponding to the references of the seed paper.  
4. Query the citations table. The resolved\_paper\_id column should be populated for the citations of the seed paper that were successfully found on Crossref.  
5. Call the graph export API endpoint and verify that it returns a correct list of nodes and edges representing the depth-1 graph.

## **12\. Structured Summarization Service**

This service uses a Large Language Model (LLM) to generate concise, section-aware summaries for each paper, accelerating user comprehension.

### **Implementation Details**

* **Task-Based Trigger:** Summarization will be an on-demand process, likely triggered by a Celery task summarize\_paper\_task(paper\_id).  
* **Input Aggregation:** The task will fetch the full text for a paper's abstract, introduction, and conclusion sections from the chunks table.  
* **Prompt Orchestration:**  
  * Construct a specific prompt for the LLM (via OpenRouter). The prompt must instruct the model to generate four distinct summaries in a single call:  
    1. abstract\_summary: A concise summary of the abstract.  
    2. intro\_summary: A summary of the introduction, focusing on the problem statement and context.  
    3. conclusion\_summary: A summary of the conclusion, focusing on findings and future work.  
    4. tldr: A one-sentence "Too Long; Didn't Read" summary of the entire paper.  
  * The prompt must enforce a scientific tone and explicitly request the output in a JSON format with keys matching the four field names above to simplify parsing.  
* **Persistence:** The parsed JSON response from the LLM is used to upsert a record into the paper\_summaries table, keyed by the paper\_id. The logic should only update missing or stale fields.  
* **API Exposure:** The generated summaries will be joined and exposed as part of the main paper data retrieval endpoints used by the frontend.

### **Testing Method**

1. Ingest a paper that has distinct abstract, introduction, and conclusion sections.  
2. Manually trigger the summarize\_paper\_task for this paper.  
3. Monitor the worker logs for the call to the OpenRouter API.  
4. After the task completes, query the paper\_summaries table for the paper\_id. Verify that a record exists and all four summary fields (abstract\_summary, intro\_summary, conclusion\_summary, tldr) are populated with non-empty, coherent text.

## **13\. Gap Analysis and Insight Generation Pipeline**

This pipeline analyzes the entire collection of papers to identify and rank potential research gaps, providing users with actionable strategic insights.

### **Implementation Details**

* **Task Entry Point:** The gap\_analysis\_task(collection\_id) Celery task will orchestrate this entire process.  
* **Corpus Assembly:** The task begins by fetching the embeddings for all papers in the collection. It should prioritize abstract embeddings; if an abstract is missing, it can fall back to using an embedding of the paper's title.  
* **Clustering:** Apply a deterministic clustering algorithm to the collected embeddings. K-Means with a heuristic for determining K (e.g., based on the number of papers) is a suitable starting point due to its stability and predictability.  
* **Metric Calculation:** For each identified cluster, calculate a set of metrics:  
  * **Coverage:** A measure of cluster size and diversity (e.g., number of papers, variety of publication venues).  
  * **Novelty:** The inverse local density of the cluster, indicating how distinct it is from other thematic groups.  
  * **Trajectory:** The proportion of recent papers (e.g., last 2 years) in the cluster, indicating growing research interest.  
* **Scoring and Insight Generation:**  
  * Combine the metrics into a final score for each potential gap using a weighted formula, for example: $Score \= w\_{1} \\cdot novelty \+ w\_{2} \\cdot trajectory \+ \\dots$.  
  * For the top-ranked gaps (e.g., top 5), use an LLM with a carefully crafted prompt to generate a concise, human-readable statement describing the research gap (e.g., "There is limited research on applying reinforcement learning to combinatorial optimization in logistics, despite recent advances in graph neural networks.").  
  * The prompt should also request representative keywords for the gap.  
* **Persistence:** Store the top-ranked insights in the gap\_insights table. Each record will include the generated text, the score, and an evidence JSONB field containing the cluster ID, representative paper IDs, and the raw metric values.

### **Testing Method**

1. Create a collection with at least 20-30 papers covering a few distinct but related sub-topics.  
2. Trigger the gap\_analysis\_task.  
3. Monitor the worker logs for the clustering and scoring steps.  
4. After completion, query the gap\_insights table for the collection. Verify that at least 5 insights have been generated.  
5. Inspect the evidence JSON of one of the insights to confirm it contains plausible paper IDs and metric scores. The generated insight text should be relevant to the collection's content.

## **14\. RAG-based Chat Service Implementation**

This step implements the core Retrieval-Augmented Generation (RAG) service, which combines the hybrid search foundation with an LLM to provide citation-backed answers to user questions.

### **Implementation Details**

* **Orchestration Logic:** This logic will reside in the api service, exposed via a dedicated chat endpoint.  
* **Intake and Validation:** The endpoint will accept a user's message and the collection\_id. It must first validate that the user owns the collection and that their monthly chat quota has not been exhausted.  
* **Retrieval Step:** Invoke the hybrid retrieval logic (Step 10\) with the user's message as the query. This will produce a ranked list of the most relevant text chunks from the collection.  
* **Context Packing:**  
  * Select the top K chunks from the retrieval results.  
  * Assemble a context block to be injected into the LLM prompt. This block will contain the text of the selected chunks, each clearly demarcated and prefixed with a citation marker (e.g., \`\`).  
  * Enforce a strict token budget for the context block to avoid exceeding the LLM's context window.  
* **LLM Call:**  
  * Compose the final prompt sent to the OpenRouter chat model. The prompt will include a system message instructing the model to answer the user's question *based only on the provided context* and to cite its sources using the provided markers.  
  * The user's message is then appended.  
* **Post-processing and Response:**  
  * Parse the LLM's response to extract the answer text and the citation markers it used.  
  * Construct a structured JSON response for the frontend containing the answer string and a list of citation objects. Each citation object must include the paper\_id, chunk\_id, and the source snippet text for UI display.  
  * On a successful response, decrement the user's remaining chat quota for the month.

### **Testing Method**

1. Ingest a collection of papers on a specific topic.  
2. Use the chat API endpoint to ask a question whose answer is explicitly contained within one of the ingested papers (e.g., "What was the key finding of the paper titled 'Attention Is All You Need'?").  
3. Verify that the API response contains a correct textual answer.  
4. Verify that the response also contains a citations array with at least one entry, and that this entry correctly points to the paper and chunk where the answer was found.  
5. Check the user's quota to ensure it has been decremented by one.

## **15\. Collections, Ingestion, & Graph Management**

This step defines and implements the public-facing API surface in the api service for managing core user resources and initiating data processing workflows.

### **Implementation Details**

* **Collections API:**  
  * POST /collections: Creates a new collection. Must enforce the MAX\_COLLECTIONS\_PER\_USER limit for the user's plan.  
  * GET /collections: Lists all collections for the authenticated user.  
  * GET /collections/{collection\_id}: Retrieves details for a single collection, including a list of its papers.  
  * DELETE /collections/{collection\_id}: Deletes a collection and all its associated data (cascades handled by the database).  
* **Ingestion API:**  
  * POST /collections/{collection\_id}/ingest/upload: Accepts a multipart/form-data PDF upload. Streams the file to GCS and enqueues the ingest\_pdf\_task. Returns the newly created (or matched) paper's ID.  
  * POST /collections/{collection\_id}/ingest/topic: Accepts a JSON body with query and limit. Caps the limit at MAX\_TOPIC\_PAPERS, enqueues the ingest\_topic\_task, and returns a task ID for polling.  
* **Graph API:**  
  * POST /collections/{collection\_id}/graph/build: Accepts a JSON body with mode ('bfs'/'dfs') and depth. Caps the depth at MAX\_GRAPH\_DEPTH, enqueues the build\_graph\_task, and returns a task ID.  
  * GET /collections/{collection\_id}/graph: Returns the current state of the citation graph as a JSON object with nodes and edges arrays, suitable for rendering by a visualization library.

### **Testing Method**

Use an API client like Postman or Insomnia to test each endpoint.

* **Collections:** Verify that a user can create, list, retrieve, and delete a collection. Confirm that creating a second collection for a free-tier user results in a 403 Forbidden error.  
* **Ingestion:** Successfully call the upload and topic ingestion endpoints. Verify that the correct Celery tasks are enqueued by checking the worker logs or RabbitMQ.  
* **Graph:** Call the build endpoint and verify task enqueueing. After the task completes, call the GET endpoint and confirm it returns a valid graph JSON structure.

## **16\. Summarization, Gap Analysis, and Chat**

This step implements the API endpoints that expose the application's core AI-driven features to the frontend.

### **Implementation Details**

* **Summaries API:**  
  * GET /papers/{paper\_id}/summaries: Retrieves the structured summaries for a given paper. If the summaries do not exist in the paper\_summaries table, this endpoint should enqueue the summarize\_paper\_task and return a 202 Accepted status, indicating the resource is being generated. Subsequent calls would return the completed summaries with a 200 OK.  
* **Gaps API:**  
  * POST /collections/{collection\_id}/gaps/generate: Enqueues the gap\_analysis\_task to compute insights for the collection. Returns a task ID.  
  * GET /collections/{collection\_id}/gaps: Retrieves the list of persisted gap\_insights for the collection, ordered by score.  
* **Chat API:**  
  * POST /collections/{collection\_id}/chat: The main RAG endpoint as detailed in Step 14\. Accepts a user message, performs retrieval-augmented generation, and returns a structured answer with citations. This endpoint contains the full orchestration logic, including quota checks.  
* **Diagnostic Search API:**  
  * GET /collections/{collection\_id}/search: A utility endpoint for debugging. Accepts a query and returns the raw, fused results from the hybrid search pipeline, including chunk IDs, snippets, and scores, before they are passed to the LLM.

### **Testing Method**

* **Summaries:** For a paper without summaries, the first GET request should return 202\. After the worker task completes, a second GET request must return 200 with the JSON object containing the four summary fields.  
* **Gaps:** Call the POST endpoint to trigger analysis. After the task completes, call the GET endpoint and verify it returns a ranked list of gap insight objects.  
* **Chat:** Test this endpoint thoroughly as described in Step 14\.  
* **Search:** Call the search endpoint with a query and verify it returns a structured list of ranked chunk results.

## **17\. Server-Side Usage Limit & Quota Enforcement**

This step implements the server-side guards that enforce all business rules and free-tier limitations. This logic must be robust and centralized to ensure consistency across the application.

### **Implementation Details**

* **Centralized Enforcement Logic:** Create a set of reusable dependencies or decorators in the FastAPI application to handle limit enforcement. This avoids scattering the logic across multiple endpoint handlers.  
* **Topic Paper Limit:** In the POST /.../ingest/topic endpoint, the requested limit must be replaced with min(requested\_limit, MAX\_TOPIC\_PAPERS) before being passed to the Celery task.  
* **Graph Depth Limit:** In the POST /.../graph/build endpoint, the requested depth must be replaced with min(requested\_depth, MAX\_GRAPH\_DEPTH).  
* **Collection Limit:** In the POST /collections endpoint, before creating the collection, perform a database query to check if the authenticated user already owns a collection. If so, return a 403 Forbidden error with an informative message.  
* **Chat Quota:** In the POST /.../chat endpoint, before any processing, check the user's monthly quota. If the quota is exhausted, return a 429 Too Many Requests error. The quota itself should be stored and managed in the users table or a related table.  
* **Informative Responses:** When a cap is applied or a limit is reached, the API response body must include a clear, human-readable message explaining what happened (e.g., "Graph depth capped at 3 for free plan."). For quota-limited features like chat, the response should also include the remaining quota count.

### **Testing Method**

* Attempt to create a second collection for a new user; it must fail with a 403\.  
* Call the topic ingestion endpoint with limit=50; verify the enqueued task receives limit=30 (or MAX\_TOPIC\_PAPERS).  
* Call the graph build endpoint with depth=5; verify the enqueued task receives depth=3 (or MAX\_GRAPH\_DEPTH).  
* Manually set a user's chat quota to 0 in the database. Attempting to use the chat API must fail with a 429\.

## **18\. Frontend Application Shell & Authentication**

This step establishes the main structure of the React application, including routing, authentication state management, and the primary UI layout that houses all other components.

### **Implementation Details**

* **Authentication Guard:** Implement a top-level component or routing guard that checks for the user's authentication status. It can do this by checking for the presence of a session cookie or by calling a /api/v1/me endpoint. Unauthenticated users must be redirected to a dedicated Login page.  
* **State Management:** Use a state management library (e.g., Zustand, Redux Toolkit) to store the global user state (profile information, authentication status) and the active usage caps fetched from the backend.  
* **Main Layout:** Create a main application layout component that includes a persistent header or sidebar. This layout will prominently display a "Free plan" badge and the user's active limits (e.g., "1/1 Collection", "78/100 Chat Messages Remaining") by reading them from the global state.  
* **Login Component:** Create a simple Login page with a single "Sign in with Google" button. Clicking this button should navigate the browser to the backend's /auth/google/login endpoint to initiate the SSO flow.

### **Testing Method**

1. Navigate to the application's root URL in a clean browser session. You must be redirected to the Login page.  
2. Click the "Sign in with Google" button. You should be taken through the Google SSO flow and redirected back to the application's main dashboard.  
3. The main layout should be visible, and the header should display the user's name/email and the "Free plan" badge with the correct usage caps.  
4. Manually deleting the session cookie and refreshing the page must redirect you back to the Login page.

## **19\. Core Data Views**

This step implements the primary user interface components for managing and exploring the core data entities: collections, papers, and the citation graph.

### **Implementation Details**

* **Dashboard View:**  
  * This view will be the default landing page for authenticated users.  
  * It will list the user's single collection, providing controls to delete it or create a new one (if the current one is deleted).  
  * It will display key statistics for the collection: paper count and graph node/edge counts.  
* **Collection View (Tabbed Interface):** Create a main view for a single collection, structured with tabs.  
  * **Ingest Panel:** A persistent panel within this view will contain:  
    * A PDF uploader with client-side size/MIME type validation and a progress bar.  
    * A topic search input field.  
    * Graph build controls with a mode selector (BFS/DFS) and a depth input, which displays a "capped to 3" message if the user enters a higher number.  
  * **Papers Tab:**  
    * A paginated table listing all papers in the collection with columns for title, year, venue, and status badges (e.g., "Embedded", "Summarized").  
    * Clicking a row opens a "Drawer" component. This drawer slides in to display rich details for the selected paper: authors, affiliations, the four generated summaries, and a link to view the PDF (which uses the signed GCS URL).  
  * **Graph Tab:**  
    * Implement a graph visualization using a library like react-force-graph.  
    * The component will fetch data from the /api/.../graph endpoint.  
    * It must support zoom/pan, show paper titles on node hover, and open the same Paper Drawer component when a node is clicked.  
    * Edges for unresolved citations should be styled differently (e.g., dashed line).

### **Testing Method**

1. Navigate through the entire data exploration flow. Start at the dashboard, click into the collection.  
2. Use the ingest panel to add a new paper via PDF upload and another set via topic search. The papers table must update correctly.  
3. Click on a paper in the table. The details drawer must open and display the correct summaries and metadata.  
4. Switch to the Graph tab. A force-directed graph must render. Hovering over and clicking nodes must function as expected.

## **20\. AI-Driven Interfaces**

This final implementation step builds the user-facing components for the application's primary AI-powered features: the grounded chat and the gap analysis viewer.

### **Implementation Details**

* **Chat Tab:**  
  * Implement a standard chat interface with a message history view and a text input box at the bottom.  
  * When a user submits a message, it should be sent to the /api/.../chat endpoint.  
  * The response from the API (answer and citations) must be rendered in the message history.  
  * The answer text must render clickable "citation chips" (e.g., , ).  
  * Hovering over a citation chip must display a tooltip/popover showing the source paper title, section, and the text snippet.  
  * Clicking a citation chip must open the Paper Drawer for the source paper and ideally scroll to highlight the specific chunk/passage.  
  * A quota indicator (77/100 remaining) must be clearly visible near the input box.  
* **Gaps Tab:**  
  * This tab will fetch data from the /api/.../gaps endpoint and display the insights as a ranked list of "Insight Cards".  
  * Each card will display the gap's title/statement, its score, and representative keywords/themes.  
  * Each card must have a "View Evidence" button. Clicking this opens a modal window that lists the representative papers that form the basis of the insight, allowing users to click through to view them in the Papers tab.  
  * Each card should also feature "quick action" buttons like "Ask chat about this gap", which pre-fills the chat input with a relevant question, and "Locate related nodes", which could highlight the evidence papers in the Graph tab.

### **Testing Method**

1. Go to the Chat tab and ask a question. The response must appear with clickable citation chips. Hovering and clicking the chips must trigger the correct popover and Drawer actions.  
2. Go to the Gaps tab. A list of ranked insight cards must be displayed.  
3. Click "View Evidence" on a card. A modal must appear showing the correct list of source papers.  
4. Click the "Ask chat about this gap" button. You should be switched to the Chat tab with a pre-filled, relevant question in the input box.