try:
    from llama_index.llms.ollama import Ollama
    print("✅ Import successful: llama_index.llms.ollama")
except ImportError:
    try:
        from llama_index.core.llms.ollama import Ollama
        print("✅ Import successful: llama_index.core.llms.ollama")
    except ImportError:
        print("❌ Failed to import Ollama from LlamaIndex")
try:
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    print("✅ Import successful: llama_index.embeddings.huggingface")
except ImportError:
    try:
        from llama_index.core.embeddings.huggingface import HuggingFaceEmbedding
        print("✅ Import successful: llama_index.core.embeddings.huggingface")
    except ImportError:
        print("❌ Failed to import HuggingFaceEmbedding from LlamaIndex")
