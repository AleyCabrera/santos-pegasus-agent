# Crear archivo test_imports.py
print("🔍 Probando imports...")

try:
    from sentence_transformers import SentenceTransformer
    print("✅ sentence-transformers: OK")
except ImportError as e:
    print(f"❌ sentence-transformers: {e}")

try:
    import faiss
    print("✅ faiss: OK")
except ImportError as e:
    print(f"❌ faiss: {e}")

try:
    import torch
    print(f"✅ torch: OK (versión {torch.__version__})")
except ImportError as e:
    print(f"❌ torch: {e}")

try:
    from app.embeddings.embedding_manager import EmbeddingManager
    print("✅ EmbeddingManager: OK")
except ImportError as e:
    print(f"❌ EmbeddingManager: {e}")

print("\n🎯 Prueba completada!")