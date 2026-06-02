# ARC AI — Maryland Housing & Rental Law Assistant

## Domain
AI Engineering | NLP | Retrieval-Augmented Generation | Legal AI Systems

## Technologies
Python, FastAPI, Ollama, ChromaDB, spaCy, KeyBERT, BART, RoBERTa, BeautifulSoup, TensorFlow, scikit-learn

## Concepts
RAG Pipelines, Vector Databases, Semantic Search, LLM Applications, NLP Workflows, Legal AI, Streaming APIs, Information Retrieval

## Detailed Work

- Built a fully local Retrieval-Augmented Generation (RAG) legal assistant for Maryland housing and rental law
- Developed end-to-end legal document ingestion pipeline using web scraping, chunking, embedding, and vector retrieval
- Integrated ChromaDB vector database with semantic similarity search for grounded legal responses
- Implemented FastAPI backend with streaming NDJSON response architecture
- Built multi-model LLM switching system using Ollama with Llama 3.1, Mistral, and Qwen models
- Designed semantic chunking workflows using token-aware chunking strategies
- Engineered local-first AI architecture with zero cloud dependency and offline inference support
- Implemented 9 NLP analysis techniques including NER, summarization, sentiment analysis, extractive QA, keyword extraction, and topic modeling
- Developed extractive QA verification pipeline using RoBERTa-SQuAD2
- Built custom frontend UI with live streaming responses and citation-aware interactions
- Created multi-source Maryland legal web scraper with browser User-Agent rotation and multi-hop crawling
- Implemented persistent vector storage and retrieval workflows using MiniLM embeddings
- Designed configurable session memory and conversation management system
- Engineered citation-grounded answer generation to reduce hallucinations
- Built modular NLP processing architecture with lazy-loaded transformer pipelines
- Developed REST API endpoints for chat inference and NLP analysis workflows

## NLP Techniques Implemented

- Intent Classification
- Named Entity Recognition (NER)
- Topic Modeling
- Extractive Question Answering (RoBERTa-SQuAD2)
- Sentiment Analysis
- Text Summarization
- Keyword Extraction
- Readability Scoring
- Emotion Detection

## Data Sources

- Maryland Attorney General
- Maryland DHCD
- Montgomery County DHCA
- Baltimore County Housing Resources
- Baltimore City DHCD
- Prince George's County DHCD
- People's Law Library

## Architecture Highlights

- Multi-source web scraping pipeline with User-Agent rotation and multi-hop crawling
- Token-aware chunking engine
- MiniLM embedding workflows → ChromaDB vector retrieval
- Streaming FastAPI inference APIs (NDJSON)
- Multi-model inference orchestration via Ollama
- Modular lazy-loaded NLP analysis engine
- Citation-aware response system for hallucination reduction

## Performance & Optimization

- Persistent ChromaDB vector indexing (100+ Maryland legal documents)
- Lazy-loaded NLP transformer pipelines
- Token streaming response architecture
- Configurable Top-K semantic retrieval
- Local inference optimization via Ollama
