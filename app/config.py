import os
from services.rtl_service import RTLService
from services.waveform_service import WaveformService
from services.embedding_service import EmbeddingService
from services.rag_service import RAGService
from services.regression_service import RegressionService
from connectors.git import GitConnector
from services.formal_service import FormalService

from services.llm_service import LLMService

# Workspace root
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Database paths
DATABASE_DIR = os.path.join(WORKSPACE_ROOT, "database")
RAG_DB_PATH = os.path.join(DATABASE_DIR, "rag.db")
REGRESSION_DB_PATH = os.path.join(DATABASE_DIR, "regression.db")

# Default search directories for RTL
RTL_SEARCH_DIRS = [WORKSPACE_ROOT]

# Instantiate singletons
embedding_service = EmbeddingService()
llm_service = LLMService()
rtl_service = RTLService()
waveform_service = WaveformService()
rag_service = RAGService(RAG_DB_PATH, embedding_service)
regression_service = RegressionService(REGRESSION_DB_PATH, embedding_service)
git_connector = GitConnector(WORKSPACE_ROOT)
formal_service = FormalService()

# Populate mock data for database demonstration
rag_service.populate_mock_data()
regression_service.populate_mock_data()
