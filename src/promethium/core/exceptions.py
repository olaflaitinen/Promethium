class PromethiumError(Exception):
    """Base exception for Promethium framework."""
    pass

class ConfigurationError(PromethiumError):
    """Raised when configuration is invalid or missing."""
    pass

class DataIngestionError(PromethiumError):
    """Raised when data ingestion fails (e.g., corrupt SEG-Y)."""
    pass

class ModelError(PromethiumError):
    """Raised when ML model operations fail."""
    pass

class WorkflowError(PromethiumError):
    """Raised when a workflow/pipeline step fails."""
    pass

class ProcessingError(PromethiumError):
    """Raised when signal processing operations fail."""
    pass

class ValidationError(PromethiumError):
    """Raised when data validation fails."""
    pass

