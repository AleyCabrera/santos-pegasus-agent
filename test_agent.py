#!/usr/bin/env python
"""
Script de prueba rápida para el agente
"""
import sys
import logging
from src.agent import create_rag_chain, ask_question
from src.vectorstore import load_vector_store

logging.basicConfig(level=logging.INFO)

def test_agent():
    """Prueba el agente con preguntas predefinidas"""
    print("🧪 Probando Agente RAG...\n")
    
    # Verificar vector store
    vector_store = load_vector_store()
    if vector_store is None:
        print("❌ No se encontró índice FAISS")
        print("👉 Ejecuta primero la ingesta con: python -c 'from src.ingest import process_documents; from src.vectorstore import create_vector_store; chunks = process_documents(); create_vector_store(chunks)'")
        return False
    
    # Crear agente
    chain = create_rag_chain()
    if chain is None:
        print("❌ No se pudo crear el agente")
        return False
    
    print("✅ Agente listo\n")
    
    # Preguntas de prueba
    test_questions = [
        "¿Cuál es la filosofía de Santos Pegasus Soluciones?",
        "¿Qué herramientas usamos para backend?",
        "¿Cómo manejamos los incidentes?",
        "¿Qué es la arquitectura de microservicios?",
        "¿Qué tecnologías usamos en frontend?"
    ]
    
    for question in test_questions:
        print(f"🔍 Pregunta: {question}")
        print("-" * 50)
        
        result = ask_question(chain, question)
        
        if result["success"]:
            print(f"✅ Respuesta:\n{result['answer']}")
        else:
            print(f"❌ Error: {result['answer']}")
        
        print("\n" + "="*50 + "\n")
    
    return True

if __name__ == "__main__":
    success = test_agent()
    sys.exit(0 if success else 1)