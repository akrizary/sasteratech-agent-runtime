# Artifact Registry

Tracks artifact_id, path, SHA-256, size, media type, producing run/step, canonical flag, parents, supersession and metadata.

Integrity verification re-reads the file and compares existence, size and SHA-256. A stored registry row alone is not proof that the artifact still exists unchanged.
